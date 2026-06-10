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
FINITE_VALUES_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-finite-values.md"
RESPONSE_ROOT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-response-root.md"
)
EMPTY_ROWS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-empty-rows.md"
)
MEASUREMENT_ROWS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-measurement-rows.md"
)
OBSERVATION_KEYS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-observation-keys.md"
)
TOKEN_WHITESPACE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-09-weather-notebook-token-whitespace.md"
)
DEPENDENCY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-dependency-reproducibility.md"
)
PAGINATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-noaa-pagination.md"
)
METRIC_UNITS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-noaa-metric-units.md"
)
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "check.yml"


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
    assert_true(
        'os.environ.get("NOAA_TOKEN", "").strip()' in source,
        "notebook must strip whitespace around NOAA_TOKEN before validation",
    )
    assert_true("token = 'XXX'" not in source, "notebook must not keep a hardcoded token placeholder")
    assert_true('token = "XXX"' not in source, "notebook must not keep a hardcoded token placeholder")


def test_noaa_requests_are_parameterized_and_bounded():
    source = notebook_source(load_notebook())
    assert_true("params=" in source, "NOAA requests must use structured query parameters")
    assert_true("timeout=REQUEST_TIMEOUT_SECONDS" in source, "NOAA requests must set a timeout")
    assert_true(".raise_for_status()" in source, "NOAA responses must fail fast on HTTP errors")


def test_noaa_metric_units_are_explicit_and_converted():
    source = notebook_source(load_notebook())
    assert_true('"units": "metric"' in source, "NOAA requests must explicitly request scaled metric values")
    assert_true("def c_to_f(value):" in source, "temperature conversion must accept metric Celsius values")
    assert_true("return number * 1.8 + 32" in source, "Celsius values must convert to Fahrenheit without raw-data scaling")
    assert_true("return number / 25.4" in source, "millimeters must convert to inches with the exact divisor")
    assert_true("tenths_c_to_f" not in source, "metric NOAA values must not use raw tenths-Celsius conversion")
    assert_true("number / 25.54" not in source, "precipitation conversion must not use an incorrect divisor")
    for measurement in ("avg_temp", "min_temp", "max_temp"):
        assert_true("{0} = c_to_f(".format(measurement) in source, "{0} must use metric temperature conversion".format(measurement))


def test_noaa_requests_are_paginated_with_a_safety_bound():
    source = notebook_source(load_notebook())
    for contract in (
            "NOAA_PAGE_LIMIT = 1000",
            "MAX_NOAA_PAGES = 20",
            "for page_index in range(MAX_NOAA_PAGES):",
            '"offset": page_index * NOAA_PAGE_LIMIT + 1',
            "all_results.extend(results)",
            "if len(results) < NOAA_PAGE_LIMIT:",
            "return all_results",
            'raise ValueError("NOAA response exceeded the page safety limit")'):
        assert_true(contract in source, "missing NOAA pagination contract {0}".format(contract))
    assert_true(
        source.index('"offset": page_index * NOAA_PAGE_LIMIT + 1')
        < source.index("response = requests.get("),
        "NOAA offset must be included before each request",
    )


def test_noaa_result_shape_is_checked():
    source = notebook_source(load_notebook())
    assert_true("payload = response.json()" in source, "NOAA response JSON must be captured before reading results")
    assert_true("isinstance(payload, dict)" in source, "NOAA response root must be checked before dictionary access")
    assert_true(
        'raise ValueError("NOAA response must be an object")' in source,
        "NOAA response root-shape errors must be explicit",
    )
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


def test_notebook_rejects_non_text_observation_keys():
    source = notebook_source(load_notebook())
    assert_true(
        "if not isinstance(date, str) or not isinstance(datatype, str):" in source,
        "NOAA observation date and datatype keys must be textual before bucketing",
    )
    assert_true(
        source.index("if not isinstance(date, str) or not isinstance(datatype, str):")
        < source.index("if not date or datatype not in SUPPORTED_DATATYPES:")
        < source.index("weather_by_date.setdefault(date, {})[datatype]"),
        "NOAA observation key type guard must run before set membership and bucketing",
    )


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
    assert_true("import math" in source, "notebook must import math for finite numeric checks")
    assert_true(
        "if not math.isfinite(number):" in source,
        "NOAA numeric parsing must reject NaN and infinite values",
    )
    assert_true("return number * 1.8 + 32" in source, "temperature conversion must use guarded numeric values")
    assert_true("return number / 25.4" in source, "precipitation conversion must use guarded numeric values")


def test_notebook_rejects_empty_valid_observation_rows():
    source = notebook_source(load_notebook())
    assert_true(
        "if not rows:" in source,
        "notebook must detect when all NOAA observation rows were skipped",
    )
    assert_true(
        'raise ValueError("No valid NOAA observations were available")' in source,
        "empty NOAA observation sets must raise an explicit error",
    )
    assert_true(
        source.index("if not rows:")
        < source.index(
            'pd.DataFrame(rows, columns=["date", "avgTemp", "minTemp", "maxTemp", "prcp"])'
        ),
        "notebook must reject empty row sets before dataframe construction",
    )


def test_notebook_skips_rows_without_measurements():
    source = notebook_source(load_notebook())
    assert_true(
        'avg_temp = c_to_f(values.get("TAVG"))' in source,
        "row building must store converted average temperature before append",
    )
    assert_true(
        'min_temp = c_to_f(values.get("TMIN"))' in source,
        "row building must store converted minimum temperature before append",
    )
    assert_true(
        'max_temp = c_to_f(values.get("TMAX"))' in source,
        "row building must store converted maximum temperature before append",
    )
    assert_true(
        'precipitation = mm_to_inches(values.get("PRCP"))' in source,
        "row building must store converted precipitation before append",
    )
    assert_true(
        "if all(value is None for value in (avg_temp, min_temp, max_temp, precipitation)):" in source,
        "notebook must skip rows without any converted measurements",
    )
    assert_true(
        source.index("if all(value is None for value in (avg_temp, min_temp, max_temp, precipitation)):")
        < source.index("rows.append({"),
        "measurement-empty row guard must run before appending dataframe rows",
    )
    for field, variable in (
        ('"avgTemp"', "avg_temp"),
        ('"minTemp"', "min_temp"),
        ('"maxTemp"', "max_temp"),
        ('"prcp"', "precipitation"),
    ):
        assert_true(
            "{0}: {1}".format(field, variable) in source,
            "dataframe rows must use guarded {0} values".format(field),
        )


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
    assert_completed_plan(FINITE_VALUES_PLAN_PATH, "weather notebook finite values")
    assert_completed_plan(RESPONSE_ROOT_PLAN_PATH, "weather notebook response root")
    assert_completed_plan(EMPTY_ROWS_PLAN_PATH, "weather notebook empty rows")
    assert_completed_plan(MEASUREMENT_ROWS_PLAN_PATH, "weather notebook measurement rows")
    assert_completed_plan(OBSERVATION_KEYS_PLAN_PATH, "weather notebook observation keys")
    assert_completed_plan(TOKEN_WHITESPACE_PLAN_PATH, "weather notebook token whitespace")
    assert_completed_plan(DEPENDENCY_PLAN_PATH, "weather notebook dependency reproducibility")
    assert_completed_plan(PAGINATION_PLAN_PATH, "NOAA pagination")
    assert_completed_plan(METRIC_UNITS_PLAN_PATH, "NOAA metric units")


def test_dependency_and_ci_contracts():
    requirements = (ROOT / "requirements.txt").read_text()
    for requirement in (
            "jupyter==1.1.1",
            "matplotlib==3.10.9",
            "numpy==2.4.6",
            "pandas==3.0.3",
            "requests==2.34.2"):
        assert_true(requirement in requirements, "missing exact dependency pin {0}".format(requirement))
    assert_true(">=" not in requirements, "direct notebook dependencies must be exact pins")

    workflow = CI_WORKFLOW_PATH.read_text()
    for contract in (
            "permissions:\n  contents: read",
            "concurrency:",
            "cancel-in-progress: true",
            "runs-on: ubuntu-24.04",
            "timeout-minutes: 15",
            'python-version: ["3.12", "3.14"]',
            "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
            "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
            "python -m pip install -r requirements.txt",
            "import jupyter, matplotlib, numpy, pandas, requests",
            "run: make check"):
        assert_true(contract in workflow, "missing CI contract {0}".format(contract))
    assert_true("@v" not in workflow, "CI actions must use immutable commits")
    assert_true("ubuntu-latest" not in workflow, "CI must not use a floating Ubuntu runner")
    assert_true("# v6.0.3" in workflow, "checkout pin annotation must identify the exact release")
    assert_true("# v6.2.0" in workflow, "setup-python pin annotation must identify the exact release")

    makefile = (ROOT / "Makefile").read_text()
    assert_true("ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile, "Makefile must resolve the repository root")
    assert_true("$(ROOT)/scripts/check_weather_notebook_contracts.py" in makefile, "Makefile must use the rooted contract path")
    assert_true('find "$(ROOT)"' in makefile, "Makefile cleanup must stay inside the repository")


def main():
    tests = [
        test_noaa_token_comes_from_environment,
        test_noaa_requests_are_parameterized_and_bounded,
        test_noaa_metric_units_are_explicit_and_converted,
        test_noaa_requests_are_paginated_with_a_safety_bound,
        test_noaa_result_shape_is_checked,
        test_notebook_has_no_stale_outputs,
        test_notebook_aligns_observations_by_date,
        test_notebook_rejects_non_text_observation_keys,
        test_notebook_guards_observation_dates_and_values,
        test_notebook_rejects_empty_valid_observation_rows,
        test_notebook_skips_rows_without_measurements,
        test_completed_plans_are_in_docs_plans,
        test_dependency_and_ci_contracts,
    ]
    for test in tests:
        test()
    print("weather notebook contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
