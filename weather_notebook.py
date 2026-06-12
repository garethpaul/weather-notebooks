import math
from datetime import datetime

import requests


NOAA_API_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
REQUEST_TIMEOUT_SECONDS = 10
NOAA_PAGE_LIMIT = 1000
MAX_NOAA_PAGES = 20
SUPPORTED_DATATYPES = {"TAVG", "TMIN", "TMAX", "PRCP"}


def fetch_noaa_data(year, datatype_ids, token, station_id, requests_get=None):
    requests_get = requests_get or requests.get
    all_results = []
    for page_index in range(MAX_NOAA_PAGES):
        params = {
            "datasetid": "GHCND",
            "datatypeid": datatype_ids,
            "limit": NOAA_PAGE_LIMIT,
            "offset": page_index * NOAA_PAGE_LIMIT + 1,
            "stationid": station_id,
            "startdate": "{0}-01-01".format(year),
            "enddate": "{0}-12-31".format(year),
            "units": "metric",
        }
        response = requests_get(
            NOAA_API_URL,
            headers={"token": token},
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("NOAA response must be an object")
        results = payload.get("results", [])
        if not isinstance(results, list):
            raise ValueError("NOAA results must be a list")
        all_results.extend(results)
        if len(results) < NOAA_PAGE_LIMIT:
            return all_results
    raise ValueError("NOAA response exceeded the page safety limit")


def record_observation(item, weather_by_date):
    if not isinstance(item, dict):
        return
    date = item.get("date")
    datatype = item.get("datatype")
    if not isinstance(date, str) or not isinstance(datatype, str):
        return
    if not date or datatype not in SUPPORTED_DATATYPES:
        return
    weather_by_date.setdefault(date, {})[datatype] = item.get("value")


def parse_noaa_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError):
        return None


def noaa_number(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def c_to_f(value):
    number = noaa_number(value)
    if number is None:
        return None
    return number * 1.8 + 32


def mm_to_inches(value):
    number = noaa_number(value)
    if number is None:
        return None
    return number / 25.4
