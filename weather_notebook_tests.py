import unittest
from datetime import datetime, timedelta, timezone

import weather_notebook


class FakeResponse:
    def __init__(self, payload, error=None, status_code=200):
        self.payload = payload
        self.error = error
        self.status_code = status_code
        self.json_calls = 0

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        self.json_calls += 1
        return self.payload


class WeatherNotebookTest(unittest.TestCase):
    def test_analysis_provenance_normalizes_station_range_and_utc_time(self):
        retrieved_at = datetime(
            2026, 6, 16, 5, 30, 45, 999999,
            tzinfo=timezone(timedelta(hours=2)),
        )

        title = weather_notebook.format_analysis_provenance(
            "  GHCND:US1CAMR0037  ", 2019, 2020, retrieved_at
        )

        self.assertEqual(
            title,
            "NOAA CDO GHCND:US1CAMR0037 | 2019-01-01 to 2019-12-31 | "
            "retrieved 2026-06-16T03:30:45Z",
        )

    def test_analysis_provenance_rejects_ambiguous_inputs(self):
        aware_time = datetime(2026, 6, 16, tzinfo=timezone.utc)
        invalid_inputs = [
            (None, 2019, 2020, aware_time),
            ("   ", 2019, 2020, aware_time),
            ("station", True, 2020, aware_time),
            ("station", 999, 2020, aware_time),
            ("station", 2020, 2020, aware_time),
            ("station", 2019, 10000, aware_time),
            ("station", 2019, 2020, "2026-06-16T00:00:00Z"),
            ("station", 2019, 2020, datetime(2026, 6, 16)),
        ]

        for station_id, start_year, end_year, retrieved_at in invalid_inputs:
            with self.subTest(
                    station_id=station_id,
                    start_year=start_year,
                    end_year=end_year,
                    retrieved_at=retrieved_at):
                with self.assertRaises(ValueError):
                    weather_notebook.format_analysis_provenance(
                        station_id, start_year, end_year, retrieved_at
                    )

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

        def fake_get(url, headers, params, timeout, allow_redirects):
            calls.append((headers, params.copy(), allow_redirects))
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
        self.assertFalse(calls[0][2])

    def test_fetch_accumulates_pages_and_advances_offsets(self):
        calls = []
        pages = [
            [{"id": index} for index in range(weather_notebook.NOAA_PAGE_LIMIT)],
            [{"id": "last"}],
        ]

        def fake_get(url, headers, params, timeout, allow_redirects):
            calls.append((url, headers, params.copy(), timeout, allow_redirects))
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
        self.assertTrue(all(call[4] is False for call in calls))

    def test_fetch_stops_after_a_short_page(self):
        calls = []

        def fake_get(url, headers, params, timeout, allow_redirects):
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

        def fake_get(url, headers, params, timeout, allow_redirects):
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

        def fake_get(url, headers, params, timeout, allow_redirects):
            calls.append(params["offset"])
            return FakeResponse({
                "results": pages[len(calls) - 1],
                "metadata": {"resultset": {"count": 3, "offset": calls[-1]}}
            })

        results = weather_notebook.fetch_noaa_data(
            2019, ["TAVG"], "token", "station", requests_get=fake_get
        )

        self.assertEqual(results, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(calls, [1, 3])

    def test_fetch_rejects_result_count_drift_between_pages(self):
        for later_count in (2, 4):
            with self.subTest(later_count=later_count):
                calls = []
                pages = [[{"id": 1}, {"id": 2}], [{"id": 3}]]

                def fake_get(url, headers, params, timeout, allow_redirects):
                    page_index = len(calls)
                    calls.append(params["offset"])
                    return FakeResponse({
                        "results": pages[page_index],
                        "metadata": {"resultset": {
                            "count": 3 if page_index == 0 else later_count,
                            "offset": calls[-1],
                        }},
                    })

                with self.assertRaisesRegex(ValueError, "result count changed"):
                    weather_notebook.fetch_noaa_data(
                        2019, ["TAVG"], "token", "station", requests_get=fake_get
                    )

                self.assertEqual(calls, [1, 3])

    def test_fetch_uses_pinned_count_when_later_metadata_is_omitted(self):
        calls = []
        pages = [[{"id": 1}, {"id": 2}], [{"id": 3}]]

        def fake_get(url, headers, params, timeout, allow_redirects):
            page_index = len(calls)
            calls.append(params["offset"])
            payload = {"results": pages[page_index]}
            if page_index == 0:
                payload["metadata"] = {"resultset": {"count": 3, "offset": 1}}
            return FakeResponse(payload)

        results = weather_notebook.fetch_noaa_data(
            2019, ["TAVG"], "token", "station", requests_get=fake_get
        )

        self.assertEqual(results, [{"id": 1}, {"id": 2}, {"id": 3}])
        self.assertEqual(calls, [1, 3])

    def test_fetch_rejects_mismatched_response_offset_before_next_request(self):
        calls = []

        def fake_get(url, headers, params, timeout, allow_redirects):
            calls.append(params["offset"])
            return FakeResponse({
                "results": [{"id": "wrong-page"}],
                "metadata": {"resultset": {"count": 2, "offset": 2}},
            })

        with self.assertRaisesRegex(ValueError, "offset does not match request"):
            weather_notebook.fetch_noaa_data(
                2019, ["TAVG"], "token", "station", requests_get=fake_get
            )

        self.assertEqual(calls, [1])

    def test_fetch_rejects_malformed_response_offsets(self):
        for offset in (True, 0, -1, 1.5, "1"):
            with self.subTest(offset=offset):
                def fake_get(url, headers, params, timeout, allow_redirects):
                    return FakeResponse({
                        "results": [],
                        "metadata": {"resultset": {"count": 0, "offset": offset}},
                    })

                with self.assertRaisesRegex(ValueError, "positive integer"):
                    weather_notebook.fetch_noaa_data(
                        2019, ["TAVG"], "token", "station", requests_get=fake_get
                    )

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

    def test_fetch_rejects_redirect_before_parsing_json(self):
        response = FakeResponse(
            {"results": [{"must": "not be parsed"}]},
            status_code=302,
        )

        def fake_get(url, headers, params, timeout, allow_redirects):
            self.assertFalse(allow_redirects)
            return response

        with self.assertRaisesRegex(ValueError, "successful status"):
            weather_notebook.fetch_noaa_data(
                2019, ["PRCP"], "token", "station", requests_get=fake_get
            )

        self.assertEqual(response.json_calls, 0)

    def test_fetch_fails_at_page_safety_limit(self):
        calls = []

        def fake_get(url, headers, params, timeout, allow_redirects):
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

    def test_record_observation_accepts_identical_duplicate(self):
        weather_by_date = {}
        observation = {
            "date": "2019-01-01T00:00:00",
            "datatype": "TAVG",
            "value": 12.5,
        }

        weather_notebook.record_observation(observation, weather_by_date)
        weather_notebook.record_observation(dict(observation), weather_by_date)

        self.assertEqual(
            weather_by_date,
            {"2019-01-01T00:00:00": {"TAVG": 12.5}},
        )

    def test_record_observation_rejects_conflicting_duplicate_without_mutation(self):
        weather_by_date = {
            "2019-01-01T00:00:00": {"TAVG": 12.5, "PRCP": 2.0},
        }
        before = {
            date: dict(values) for date, values in weather_by_date.items()
        }

        for conflicting_value in (13.0, "bad"):
            with self.subTest(conflicting_value=conflicting_value):
                with self.assertRaisesRegex(ValueError, "Conflicting NOAA observation"):
                    weather_notebook.record_observation(
                        {
                            "date": "2019-01-01T00:00:00",
                            "datatype": "TAVG",
                            "value": conflicting_value,
                        },
                        weather_by_date,
                    )
                self.assertEqual(weather_by_date, before)

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

    def test_build_weather_rows_sorts_converts_and_skips_invalid_rows(self):
        weather_by_date = {
            "bad-date": {"TAVG": 10},
            "2019-01-02T00:00:00": {"TAVG": 20, "PRCP": 25.4},
            "2019-01-01T00:00:00": {"TMIN": 0, "TMAX": 10},
            "2019-01-03T00:00:00": {"TAVG": float("nan")},
        }

        rows = weather_notebook.build_weather_rows(weather_by_date)

        self.assertEqual([row["date"] for row in rows], [
            datetime(2019, 1, 1),
            datetime(2019, 1, 2),
        ])
        self.assertEqual(rows[0]["minTemp"], 32.0)
        self.assertEqual(rows[0]["maxTemp"], 50.0)
        self.assertEqual(rows[1]["avgTemp"], 68.0)
        self.assertEqual(rows[1]["prcp"], 1.0)

    def test_build_weather_rows_treats_boolean_measurements_as_missing(self):
        rows = weather_notebook.build_weather_rows({
            "2019-01-01T00:00:00": {"TAVG": True},
            "2019-01-02T00:00:00": {"TAVG": 20},
        })

        self.assertEqual(
            rows,
            [{
                "date": datetime(2019, 1, 2),
                "avgTemp": 68.0,
                "minTemp": None,
                "maxTemp": None,
                "prcp": None,
            }],
        )

    def test_build_weather_rows_rejects_empty_analysis(self):
        with self.assertRaisesRegex(ValueError, "No valid NOAA observations"):
            weather_notebook.build_weather_rows({
                "bad-date": {"TAVG": 10},
                "2019-01-01T00:00:00": {"TAVG": float("inf")},
            })

    def test_synthetic_analysis_flow_builds_dataframe_and_plot(self):
        import matplotlib
        matplotlib.use("Agg", force=True)
        import pandas as pd
        from matplotlib import pyplot as plt

        observations = {
            ("TAVG", "TMAX"): [
                {"date": "2019-01-02T00:00:00", "datatype": "TAVG", "value": 20},
                {"date": "2019-01-01T00:00:00", "datatype": "TAVG", "value": 10},
                {"date": "2019-01-01T00:00:00", "datatype": "TMAX", "value": 15},
            ],
            ("TMIN", "PRCP"): [
                {"date": "2019-01-01T00:00:00", "datatype": "TMIN", "value": 5},
                {"date": "2019-01-02T00:00:00", "datatype": "PRCP", "value": 25.4},
            ],
        }
        calls = []

        def fake_get(url, headers, params, timeout, allow_redirects):
            self.assertEqual(url, weather_notebook.NOAA_API_URL)
            self.assertFalse(allow_redirects)
            calls.append(tuple(params["datatypeid"]))
            results = observations[tuple(params["datatypeid"])]
            return FakeResponse({
                "results": results,
                "metadata": {"resultset": {"count": len(results), "offset": 1}},
            })

        weather_by_date = {}
        for datatypes in (("TAVG", "TMAX"), ("TMIN", "PRCP")):
            results = weather_notebook.fetch_noaa_data(
                2019, datatypes, "synthetic-token", "synthetic-station", requests_get=fake_get
            )
            for item in results:
                weather_notebook.record_observation(item, weather_by_date)

        rows = weather_notebook.build_weather_rows(weather_by_date)
        dataframe = pd.DataFrame(
            rows,
            columns=["date", "avgTemp", "minTemp", "maxTemp", "prcp"],
        )
        axes = dataframe.plot(kind="line", x="date", y="avgTemp")
        axes.set_title(weather_notebook.format_analysis_provenance(
            "synthetic-station",
            2019,
            2020,
            datetime(2026, 6, 16, 3, 30, 45, tzinfo=timezone.utc),
        ))
        axes.set_xlabel("Observation date")
        axes.set_ylabel("Average temperature (degrees F)")

        self.assertEqual(calls, [("TAVG", "TMAX"), ("TMIN", "PRCP")])
        self.assertEqual(list(dataframe.columns), [
            "date", "avgTemp", "minTemp", "maxTemp", "prcp"
        ])
        self.assertEqual(list(dataframe["date"]), [
            datetime(2019, 1, 1),
            datetime(2019, 1, 2),
        ])
        self.assertEqual(list(dataframe["avgTemp"]), [50.0, 68.0])
        self.assertEqual(len(axes.lines), 1)
        self.assertEqual(
            axes.get_title(),
            "NOAA CDO synthetic-station | 2019-01-01 to 2019-12-31 | "
            "retrieved 2026-06-16T03:30:45Z",
        )
        self.assertEqual(axes.get_xlabel(), "Observation date")
        self.assertEqual(axes.get_ylabel(), "Average temperature (degrees F)")
        plt.close(axes.figure)


if __name__ == "__main__":
    unittest.main()
