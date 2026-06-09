#!/usr/bin/env python3
"""Static reproducibility and token-safety checks for Weather.ipynb."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Weather.ipynb"
PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weather-notebook-reproducibility.md"


def load_notebook():
    return json.loads(NOTEBOOK.read_text())


def notebook_source(notebook):
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
    )


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def test_noaa_token_comes_from_environment():
    source = notebook_source(load_notebook())
    assert_true("NOAA_TOKEN" in source, "notebook must reference NOAA_TOKEN")
    assert_true("os.environ" in source, "notebook must load token from the environment")
    assert_true("token = 'XXX'" not in source, "notebook must not keep a hardcoded token placeholder")
    assert_true('token = "XXX"' not in source, "notebook must not keep a hardcoded token placeholder")


def test_noaa_requests_are_parameterized_and_bounded():
    source = notebook_source(load_notebook())
    assert_true("params=" in source, "NOAA requests must use structured query parameters")
    assert_true("timeout=REQUEST_TIMEOUT_SECONDS" in source, "NOAA requests must set a timeout")
    assert_true(".raise_for_status()" in source, "NOAA responses must fail fast on HTTP errors")


def test_notebook_has_no_stale_outputs():
    notebook = load_notebook()
    for index, cell in enumerate(notebook.get("cells", [])):
        assert_true(not cell.get("outputs"), "cell {0} must not have saved outputs".format(index))
        assert_true(cell.get("execution_count") is None, "cell {0} must not have an execution count".format(index))


def test_completed_plan_is_in_docs_plans():
    assert_true(PLAN_PATH.is_file(), "weather notebook plan must live under docs/plans")
    plan_text = PLAN_PATH.read_text()
    assert_true("status: completed" in plan_text.lower(), "weather notebook plan must be completed")
    assert_true("make check" in plan_text, "weather notebook plan must document make check verification")


def main():
    tests = [
        test_noaa_token_comes_from_environment,
        test_noaa_requests_are_parameterized_and_bounded,
        test_notebook_has_no_stale_outputs,
        test_completed_plan_is_in_docs_plans,
    ]
    for test in tests:
        test()
    print("weather notebook contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
