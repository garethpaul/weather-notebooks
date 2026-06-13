import unittest
from datetime import datetime

import weather_notebook


class FakeResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        return self.payload


class WeatherNotebookTest(unittest.TestCase):
    def test_fetch_rejects_invalid_inputs_before_request(self):
        calls = []

        def fake_get(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("invalid inputs must not reach the network")

        invalid_inputs = [
            (True, ["TAVG"], "token", "station"),
            (99, ["TAVG"], "token", "station"),
            (2019, [], "token", "station"),
            (2019, ["SNOW"], "token", "station"),
            (2019, ["TAVG", 1], "token", "station"),
            (2019, ["TAVG"], "   ", "station"),
            (2019, ["TAVG"], "token", "   "),
        ]
        for year, datatypes, token, station in invalid_inputs:
            with self.assertRaises(ValueError):
                weather_notebook.fetch_noaa_data(
                    year, datatypes, token, station, requests_get=fake_get
                )

        self.assertEqual(calls, [])

    def test_fetch_normalizes_valid_text_and_datatype_tuple(self):
        calls = []

        def fake_get(url, headers, params, timeout):
            calls.append((headers, params.copy()))
            return FakeResponse({"results": []})

        weather_notebook.fetch_noaa_data(
            2019,
            ("TAVG", "PRCP"),
            "  test-token  ",
            "  test-station  ",
            requests_get=fake_get,
        )

        self.assertEqual(calls[0][0], {"token": "test-token"})
        self.assertEqual(calls[0][1]["stationid"], "test-station")
        self.assertEqual(calls[0][1]["datatypeid"], ["TAVG", "PRCP"])

    def test_fetch_accumulates_pages_and_advances_offsets(self):
        calls = []
        pages = [
            [{"id": index} for index in range(weather_notebook.NOAA_PAGE_LIMIT)],
            [{"id": "last"}],
        ]

        def fake_get(url, headers, params, timeout):
            calls.append((url, headers, params.copy(), timeout))
            return FakeResponse({"results": pages[len(calls) - 1]})

        results = weather_notebook.fetch_noaa_data(
            2019,
            ["TAVG", "TMAX"],
            "test-token",
            "test-station",
            requests_get=fake_get,
        )

        self.assertEqual(len(results), weather_notebook.NOAA_PAGE_LIMIT + 1)
        self.assertTrue(all(call[0] == weather_notebook.NOAA_API_URL for call in calls))
        self.assertEqual([call[2]["offset"] for call in calls], [1, 1001])
        self.assertTrue(all(call[2]["units"] == "metric" for call in calls))
        self.assertTrue(all(call[2]["datasetid"] == "GHCND" for call in calls))
        self.assertTrue(all(call[2]["datatypeid"] == ["TAVG", "TMAX"] for call in calls))
        self.assertTrue(all(call[2]["limit"] == weather_notebook.NOAA_PAGE_LIMIT for call in calls))
        self.assertTrue(all(call[2]["stationid"] == "test-station" for call in calls))
        self.assertTrue(all(call[2]["startdate"] == "2019-01-01" for call in calls))
        self.assertTrue(all(call[2]["enddate"] == "2019-12-31" for call in calls))
        self.assertTrue(all(call[1] == {"token": "test-token"} for call in calls))
        self.assertTrue(all(call[3] == weather_notebook.REQUEST_TIMEOUT_SECONDS for call in calls))

    def test_fetch_stops_after_a_short_page(self):
        calls = []

        def fake_get(url, headers, params, timeout):
            calls.append(params.copy())
            return FakeResponse({"results": [{"id": 1}]})

        results = weather_notebook.fetch_noaa_data(
            2019, ["PRCP"], "token", "station", requests_get=fake_get
        )

        self.assertEqual(results, [{"id": 1}])
        self.assertEqual(len(calls), 1)

    def test_fetch_uses_metadata_count_for_exact_full_final_page(self):
        calls = []
        page = [{"id": index} for index in range(weather_notebook.NOAA_PAGE_LIMIT)]

        def fake_get(url, headers, params, timeout):
            calls.append(params["offset"])
            return FakeResponse({
                "results": page,
                "metadata": {"resultset": {"count": len(page)}}
            })

        results = weather_notebook.fetch_noaa_data(
            2019, ["TAVG"], "token", "station", requests_get=fake_get
        )

        self.assertEqual(results, page)
        self.assertEqual(calls, [1])

    def test_fetch_advances_metadata_pages_by_records_received(self):
        calls = []
        pages = [[{"id": 1}, {"id": 2}], [{"id": 3}]]

        def fake_get(url, headers, params, timeout):
            calls.append(params["offset"])
            return FakeResponse({
                "results": pages[len(calls) - 1],
                "metadata": {"resultset": {"count": 3}}
            })

        results = weather_notebook.fetch_noaa_data(
            2019, ["TAVG"], "token", "station", requests_get=fake_get
        )

        self.assertEqual(results, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(calls, [1, 3])

    def test_fetch_rejects_malformed_or_stalled_metadata_pages(self):
        payloads = [
            ({"results": [], "metadata": []}, "metadata must be an object"),
            (
                {"results": [], "metadata": {"resultset": {"count": True}}},
                "nonnegative integer",
            ),
            (
                {"results": [], "metadata": {"resultset": {"count": 1}}},
                "made no progress",
            ),
            (
                {
                    "results": [{"id": 1}, {"id": 2}],
                    "metadata": {"resultset": {"count": 1}},
                },
                "count is inconsistent",
            ),
        ]
        for payload, message in payloads:
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ValueError, message):
                    weather_notebook.fetch_noaa_data(
                        2019,
                        ["PRCP"],
                        "token",
                        "station",
                        requests_get=lambda *args, **kwargs: FakeResponse(payload),
                    )

    def test_fetch_rejects_malformed_payloads(self):
        for payload, message in (([], "object"), ({"results": {}}, "list")):
            with self.subTest(payload=payload):
                with self.assertRaisesRegex(ValueError, message):
                    weather_notebook.fetch_noaa_data(
                        2019,
                        ["PRCP"],
                        "token",
                        "station",
                        requests_get=lambda *args, **kwargs: FakeResponse(payload),
                    )

    def test_fetch_propagates_http_failures(self):
        with self.assertRaisesRegex(RuntimeError, "HTTP failed"):
            weather_notebook.fetch_noaa_data(
                2019,
                ["PRCP"],
                "token",
                "station",
                requests_get=lambda *args, **kwargs: FakeResponse(
                    {}, RuntimeError("HTTP failed")
                ),
            )

    def test_fetch_fails_at_page_safety_limit(self):
        calls = []

        def fake_get(url, headers, params, timeout):
            calls.append(params["offset"])
            return FakeResponse({"results": [None] * weather_notebook.NOAA_PAGE_LIMIT})

        with self.assertRaisesRegex(ValueError, "page safety limit"):
            weather_notebook.fetch_noaa_data(
                2019, ["PRCP"], "token", "station", requests_get=fake_get
            )

        self.assertEqual(len(calls), weather_notebook.MAX_NOAA_PAGES)
        self.assertEqual(calls[-1], 19001)

    def test_unit_conversions_reject_invalid_values(self):
        self.assertAlmostEqual(weather_notebook.c_to_f(0), 32.0)
        self.assertAlmostEqual(weather_notebook.mm_to_inches(25.4), 1.0)
        for value in (None, "bad", float("nan"), float("inf")):
            with self.subTest(value=value):
                self.assertIsNone(weather_notebook.c_to_f(value))
                self.assertIsNone(weather_notebook.mm_to_inches(value))

    def test_record_observation_merges_supported_values_by_date(self):
        weather_by_date = {}

        weather_notebook.record_observation(
            {"date": "2019-01-01T00:00:00", "datatype": "TAVG", "value": 12.5},
            weather_by_date,
        )
        weather_notebook.record_observation(
            {"date": "2019-01-01T00:00:00", "datatype": "PRCP", "value": 2.0},
            weather_by_date,
        )

        self.assertEqual(
            weather_by_date,
            {"2019-01-01T00:00:00": {"TAVG": 12.5, "PRCP": 2.0}},
        )

    def test_record_observation_ignores_invalid_keys_and_datatypes(self):
        weather_by_date = {}
        invalid_items = [
            None,
            [],
            {"date": 20190101, "datatype": "TAVG", "value": 1},
            {"date": "2019-01-01T00:00:00", "datatype": 1, "value": 1},
            {"date": "", "datatype": "TAVG", "value": 1},
            {"date": "2019-01-01T00:00:00", "datatype": "SNOW", "value": 1},
        ]

        for item in invalid_items:
            with self.subTest(item=item):
                weather_notebook.record_observation(item, weather_by_date)

        self.assertEqual(weather_by_date, {})

    def test_parse_noaa_date_accepts_expected_format_and_rejects_invalid_values(self):
        self.assertEqual(
            weather_notebook.parse_noaa_date("2019-01-02T00:00:00"),
            datetime(2019, 1, 2),
        )
        for value in (None, 20190102, "2019-02-30T00:00:00", "2019-01-02"):
            with self.subTest(value=value):
                self.assertIsNone(weather_notebook.parse_noaa_date(value))


if __name__ == "__main__":
    unittest.main()
