#!/usr/bin/env python3
"""Static reproducibility and token-safety checks for Weather.ipynb."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Weather.ipynb"
REPRODUCIBILITY_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weather-notebook-reproducibility.md"
DATE_ALIGNMENT_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weather-notebook-date-alignment.md"
DATA_SHAPE_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-08-weather-notebook-result-shape.md"
VALUE_GUARDS_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-value-guards.md"


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


def test_noaa_result_shape_is_checked():
    source = notebook_source(load_notebook())
    assert_true("payload = response.json()" in source, "NOAA response JSON must be captured before reading results")
    assert_true("isinstance(payload, dict)" in source, "NOAA response root must be checked before dictionary access")
    assert_true("isinstance(results, list)" in source, "NOAA results must be checked as a list")
    assert_true(
        'raise ValueError("NOAA results must be a list")' in source,
        "NOAA result-shape errors must be explicit",
    )
    assert_true("if not isinstance(item, dict):" in source, "NOAA observation rows must skip non-dict items")


def test_notebook_has_no_stale_outputs():
    notebook = load_notebook()
    for index, cell in enumerate(notebook.get("cells", [])):
        assert_true(not cell.get("outputs"), "cell {0} must not have saved outputs".format(index))
        assert_true(cell.get("execution_count") is None, "cell {0} must not have an execution count".format(index))


def test_notebook_aligns_observations_by_date():
    source = notebook_source(load_notebook())
    assert_true("weather_by_date = {}" in source, "notebook must collect NOAA observations by date")
    assert_true("def record_observation(item):" in source, "notebook must centralize observation recording")
    assert_true(".setdefault(date, {})" in source, "notebook must merge datatype values into a date bucket")
    assert_true(
        'pd.DataFrame(rows, columns=["date", "avgTemp", "minTemp", "maxTemp", "prcp"])' in source,
        "notebook must build the dataframe from aligned date rows",
    )
    assert_true("dates_temp = []" not in source, "notebook must not rely on parallel date lists")
    assert_true("temps = []" not in source, "notebook must not rely on parallel value lists")


def test_notebook_guards_observation_dates_and_values():
    source = notebook_source(load_notebook())
    assert_true("def parse_noaa_date(value):" in source, "notebook must parse NOAA dates through a guard helper")
    assert_true(
        'return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")' in source,
        "NOAA date parsing must keep the expected timestamp format",
    )
    assert_true(
        "except (TypeError, ValueError):" in source,
        "NOAA date and numeric parsing must tolerate malformed values",
    )
    assert_true("parsed_date = parse_noaa_date(date)" in source, "row building must parse dates before appending")
    assert_true("if parsed_date is None:" in source, "row building must skip invalid NOAA dates")
    assert_true('"date": parsed_date' in source, "row building must use the guarded date value")
    assert_true("def noaa_number(value):" in source, "notebook must convert NOAA numeric values through a guard helper")
    assert_true("number = noaa_number(value)" in source, "unit conversion must use guarded numeric conversion")
    assert_true("return number / 10.0 * 1.8 + 32" in source, "temperature conversion must use guarded numeric values")
    assert_true("return number / 25.54" in source, "precipitation conversion must use guarded numeric values")


def assert_completed_plan(path, label):
    assert_true(path.is_file(), "{0} plan must live under docs/plans".format(label))
    plan_text = path.read_text()
    assert_true("status: completed" in plan_text.lower(), "{0} plan must be completed".format(label))
    assert_true("make check" in plan_text, "{0} plan must document make check verification".format(label))


def test_completed_plans_are_in_docs_plans():
    assert_completed_plan(REPRODUCIBILITY_PLAN_PATH, "weather notebook reproducibility")
    assert_completed_plan(DATE_ALIGNMENT_PLAN_PATH, "weather notebook date alignment")
    assert_completed_plan(DATA_SHAPE_PLAN_PATH, "weather notebook result shape")
    assert_completed_plan(VALUE_GUARDS_PLAN_PATH, "weather notebook value guards")


def main():
    tests = [
        test_noaa_token_comes_from_environment,
        test_noaa_requests_are_parameterized_and_bounded,
        test_noaa_result_shape_is_checked,
        test_notebook_has_no_stale_outputs,
        test_notebook_aligns_observations_by_date,
        test_notebook_guards_observation_dates_and_values,
        test_completed_plans_are_in_docs_plans,
    ]
    for test in tests:
        test()
    print("weather notebook contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
