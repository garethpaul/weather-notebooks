import unittest

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
        self.assertEqual([call[2]["offset"] for call in calls], [1, 1001])
        self.assertTrue(all(call[2]["units"] == "metric" for call in calls))
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


if __name__ == "__main__":
    unittest.main()
