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
    if isinstance(year, bool) or not isinstance(year, int) or year < 1000 or year > 9999:
        raise ValueError("year must be a four-digit integer")
    if not isinstance(datatype_ids, (list, tuple)) or not datatype_ids:
        raise ValueError("datatype_ids must contain supported datatypes")
    if any(not isinstance(datatype, str) or datatype not in SUPPORTED_DATATYPES for datatype in datatype_ids):
        raise ValueError("datatype_ids must contain only supported datatypes")
    if not isinstance(token, str) or not token.strip():
        raise ValueError("token must be nonblank text")
    if not isinstance(station_id, str) or not station_id.strip():
        raise ValueError("station_id must be nonblank text")

    datatype_ids = list(datatype_ids)
    token = token.strip()
    station_id = station_id.strip()
    all_results = []
    next_offset = 1
    for _page_index in range(MAX_NOAA_PAGES):
        params = {
            "datasetid": "GHCND",
            "datatypeid": datatype_ids,
            "limit": NOAA_PAGE_LIMIT,
            "offset": next_offset,
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
            allow_redirects=False,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("NOAA response must be an object")
        results = payload.get("results", [])
        if not isinstance(results, list):
            raise ValueError("NOAA results must be a list")
        resultset = noaa_resultset(payload)
        result_count, response_offset = resultset or (None, None)
        if response_offset is not None and response_offset != next_offset:
            raise ValueError("NOAA response offset does not match request")
        all_results.extend(results)
        next_offset += len(results)
        if result_count is not None:
            if len(all_results) > result_count:
                raise ValueError("NOAA result count is inconsistent")
            if len(all_results) == result_count:
                return all_results
            if not results:
                raise ValueError("NOAA pagination made no progress")
        elif len(results) < NOAA_PAGE_LIMIT:
            return all_results
    raise ValueError("NOAA response exceeded the page safety limit")


def noaa_resultset(payload):
    metadata = payload.get("metadata")
    if metadata is None:
        return None
    if not isinstance(metadata, dict):
        raise ValueError("NOAA metadata must be an object")
    resultset = metadata.get("resultset")
    if not isinstance(resultset, dict):
        raise ValueError("NOAA resultset metadata must be an object")
    count = resultset.get("count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("NOAA result count must be a nonnegative integer")
    offset = resultset.get("offset")
    if offset is not None and (
            isinstance(offset, bool) or not isinstance(offset, int) or offset < 1):
        raise ValueError("NOAA response offset must be a positive integer")
    return count, offset


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
