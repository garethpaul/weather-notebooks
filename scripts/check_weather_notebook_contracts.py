#!/usr/bin/env python3
"""Static reproducibility and token-safety checks for Weather.ipynb."""
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "Weather.ipynb"
RUNTIME_MODULE = ROOT / "weather_notebook.py"
RUNTIME_TESTS = ROOT / "weather_notebook_tests.py"
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
CI_PLAN_PATH = ROOT / "docs" / "plans" / "2026-06-10-ci-baseline.md"
DEPENDENCY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-dependency-reproducibility.md"
)
PAGINATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-noaa-pagination.md"
)
METRIC_UNITS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-10-noaa-metric-units.md"
)
REQUEST_INPUT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-12-noaa-request-input-validation.md"
)
METADATA_PAGINATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-noaa-metadata-pagination.md"
)
RESPONSE_OFFSET_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-noaa-response-offset-validation.md"
)
REDIRECT_BOUNDARY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-13-noaa-token-redirect-boundary.md"
)
MAKE_ROOT_PROTECTION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-make-root-override-protection.md"
)
SYNTHETIC_ANALYSIS_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-14-synthetic-analysis-flow.md"
)
CONFLICTING_OBSERVATION_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-16-conflicting-noaa-observations.md"
)
ANALYSIS_PROVENANCE_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-16-weather-analysis-provenance.md"
)
STABLE_RESULT_COUNT_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-16-stable-noaa-result-count.md"
)
JUPYTERLAB_SECURITY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-20-jupyterlab-security-update.md"
)
MAKE_AUTHORITY_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-21-make-authority-isolation.md"
)
README_SETUP_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-26-readme-setup-and-dependencies.md"
)
MATPLOTLIB_REFRESH_PLAN_PATH = (
    ROOT / "docs" / "plans" / "2026-06-26-matplotlib-3.11.0-refresh.md"
)
CI_WORKFLOW_PATH = ROOT / ".github" / "workflows" / "check.yml"
LOCKFILE_SHA256 = {
    "requirements-py312.lock": "dd4346f346397fde4de14614b1510a9a7c7ed74444aed1e3c6fd7f387593cdb7",
    "requirements-py314.lock": "2521fca259203f72004966359210fc7ae76b5f2b5c8b2f233f8a8bdc1e0bef29",
}

EXPECTED_WORKFLOW = """name: Check

on:
  pull_request:
  push:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    name: Python ${{ matrix.python-version }}
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        include:
          - python-version: \"3.12\"
            lockfile: requirements-py312.lock
          - python-version: \"3.14\"
            lockfile: requirements-py314.lock
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Set up Python
        uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install dependencies
        run: python -m pip install --require-hashes -r \"${{ matrix.lockfile }}\"
      - name: Verify scientific stack imports
        run: python -c \"import jupyter, matplotlib, numpy, pandas, requests\"
      - name: Run repository checks
        run: /usr/bin/make check
      - name: Verify external working directory
        run: cd \"$(mktemp -d)\" && /usr/bin/make -f \"$GITHUB_WORKSPACE/Makefile\" check
"""


def load_notebook():
    return json.loads(NOTEBOOK.read_text())


def notebook_source(notebook):
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
    )


def project_source():
    return notebook_source(load_notebook()) + "\n" + RUNTIME_MODULE.read_text()


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
    source = project_source()
    assert_true("params=" in source, "NOAA requests must use structured query parameters")
    assert_true("timeout=REQUEST_TIMEOUT_SECONDS" in source, "NOAA requests must set a timeout")
    assert_true("allow_redirects=False" in source, "NOAA token requests must not follow redirects")
    assert_true(".raise_for_status()" in source, "NOAA responses must fail fast on HTTP errors")
    assert_true(
        "response.status_code < 200 or response.status_code >= 300" in source,
        "NOAA responses must explicitly reject redirects and other non-2xx statuses",
    )
    assert_true(
        'raise ValueError("NOAA response must have a successful status")' in source,
        "NOAA non-success status failures must be explicit",
    )
    request_function = RUNTIME_MODULE.read_text().split("def fetch_noaa_data", 1)[1].split(
        "def noaa_resultset", 1
    )[0]
    assert_true(
        request_function.index("response.status_code < 200 or response.status_code >= 300")
        < request_function.index("payload = response.json()"),
        "NOAA redirects and HTTP failures must be rejected before JSON parsing",
    )
    runtime_tests = RUNTIME_TESTS.read_text()
    assert_true(
        "test_fetch_rejects_redirect_before_parsing_json" in runtime_tests,
        "runtime tests must cover redirect rejection before JSON parsing",
    )


def test_noaa_request_inputs_are_validated_before_network_use():
    source = RUNTIME_MODULE.read_text()
    function = source.split("def fetch_noaa_data", 1)[1].split("def record_observation", 1)[0]
    request_index = function.index("response = requests_get(")
    for contract in (
        "isinstance(year, bool)",
        "not isinstance(year, int)",
        "year < 1000 or year > 9999",
        "not isinstance(datatype_ids, (list, tuple)) or not datatype_ids",
        "datatype not in SUPPORTED_DATATYPES",
        "not isinstance(token, str) or not token.strip()",
        "not isinstance(station_id, str) or not station_id.strip()",
        "datatype_ids = list(datatype_ids)",
        "token = token.strip()",
        "station_id = station_id.strip()",
    ):
        assert_true(contract in function, "NOAA request validation must include {0!r}".format(contract))
        assert_true(function.index(contract) < request_index, "NOAA request validation must run before network use")

    tests = RUNTIME_TESTS.read_text()
    assert_true(
        "test_fetch_rejects_invalid_inputs_before_request" in tests,
        "runtime tests must reject malformed NOAA request inputs",
    )
    assert_true(
        "test_fetch_normalizes_valid_text_and_datatype_tuple" in tests,
        "runtime tests must cover valid NOAA request normalization",
    )


def test_noaa_metric_units_are_explicit_and_converted():
    notebook = load_notebook()
    markdown = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "markdown"
    )
    source = notebook_source(notebook) + "\n" + RUNTIME_MODULE.read_text()
    assert_true('"units": "metric"' in source, "NOAA requests must explicitly request scaled metric values")
    assert_true("def c_to_f(value):" in source, "temperature conversion must accept metric Celsius values")
    assert_true("return number * 1.8 + 32" in source, "Celsius values must convert to Fahrenheit without raw-data scaling")
    assert_true("return number / 25.4" in source, "millimeters must convert to inches with the exact divisor")
    assert_true("tenths_c_to_f" not in source, "metric NOAA values must not use raw tenths-Celsius conversion")
    assert_true("number / 25.54" not in source, "precipitation conversion must not use an incorrect divisor")
    assert_true("tenths of Celsius" not in markdown, "notebook guidance must describe scaled metric Celsius values")
    for measurement in ("avg_temp", "min_temp", "max_temp"):
        assert_true("{0} = c_to_f(".format(measurement) in source, "{0} must use metric temperature conversion".format(measurement))


def test_noaa_requests_are_paginated_with_a_safety_bound():
    source = project_source()
    for contract in (
            "NOAA_PAGE_LIMIT = 1000",
            "MAX_NOAA_PAGES = 20",
            "next_offset = 1",
            "for _page_index in range(MAX_NOAA_PAGES):",
            '"offset": next_offset',
            "all_results.extend(results)",
            "next_offset += len(results)",
            "resultset = noaa_resultset(payload)",
            "if len(all_results) == expected_result_count:",
            "elif len(results) < NOAA_PAGE_LIMIT:",
            "return all_results",
            'raise ValueError("NOAA response exceeded the page safety limit")'):
        assert_true(contract in source, "missing NOAA pagination contract {0}".format(contract))
    assert_true(
        source.index('"offset": next_offset')
        < source.index("response = requests_get("),
        "NOAA offset must be included before each request",
    )


def test_noaa_pagination_metadata_is_validated():
    source = RUNTIME_MODULE.read_text()
    for contract in (
        'metadata = payload.get("metadata")',
        'raise ValueError("NOAA metadata must be an object")',
        'raise ValueError("NOAA resultset metadata must be an object")',
        "isinstance(count, bool)",
        'raise ValueError("NOAA result count must be a nonnegative integer")',
        'raise ValueError("NOAA pagination made no progress")',
    ):
        assert_true(contract in source, "missing NOAA metadata contract {0}".format(contract))


def test_noaa_response_offsets_are_validated_before_accumulation():
    source = RUNTIME_MODULE.read_text()
    for contract in (
            'offset = resultset.get("offset")',
            "isinstance(offset, bool)",
            "not isinstance(offset, int)",
            "offset < 1",
            'raise ValueError("NOAA response offset must be a positive integer")',
            "response_offset is not None and response_offset != next_offset",
            'raise ValueError("NOAA response offset does not match request")'):
        assert_true(contract in source, "missing NOAA response-offset contract {0}".format(contract))

    mismatch_guard = source.index(
        "if response_offset is not None and response_offset != next_offset:"
    )
    accumulation = source.index("all_results.extend(results)")
    assert_true(
        mismatch_guard < accumulation,
        "NOAA response offsets must be validated before page accumulation",
    )


def test_noaa_result_counts_remain_stable_across_pages():
    source = project_source()
    tests = RUNTIME_TESTS.read_text()
    for contract in (
        "expected_result_count = None",
        "if result_count is not None:",
        "if expected_result_count is None:",
        "expected_result_count = result_count",
        "elif result_count != expected_result_count:",
        'raise ValueError("NOAA result count changed during pagination")',
        "if expected_result_count is not None:",
        "if len(all_results) > expected_result_count:",
        "if len(all_results) == expected_result_count:",
    ):
        assert_true(contract in source, "missing stable NOAA result-count contract {0}".format(contract))

    assert_true(
        source.index("elif result_count != expected_result_count:")
        < source.index("all_results.extend(results)"),
        "NOAA result-count drift must fail before page accumulation",
    )
    for test_name in (
        "test_fetch_rejects_result_count_drift_between_pages",
        "test_fetch_uses_pinned_count_when_later_metadata_is_omitted",
    ):
        assert_true(
            "def {0}(self):".format(test_name) in tests,
            "runtime coverage is missing {0}".format(test_name),
        )

    docs = {
        "README.md": "NOAA result counts must remain stable across paginated responses",
        "SECURITY.md": "NOAA result-count changes fail before later pages are accumulated",
        "VISION.md": "Reject NOAA result-count drift across paginated responses",
        "CHANGES.md": "Rejected NOAA result-count drift across paginated responses",
    }
    for relative_path, phrase in docs.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(),
            "{0} must document stable NOAA result counts".format(relative_path),
        )


def test_noaa_result_shape_is_checked():
    source = project_source()
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
    source = project_source()
    notebook = notebook_source(load_notebook())
    assert_true("weather_by_date = {}" in source, "notebook must collect NOAA observations by date")
    assert_true("def record_observation(item, weather_by_date):" in source, "notebook must centralize observation recording")
    assert_true("def build_weather_rows(weather_by_date):" in source, "row construction must be importable")
    assert_true(
        "for date, values in sorted(weather_by_date.items()):" in source,
        "row construction must preserve chronological date ordering",
    )
    assert_true("rows = build_weather_rows(weather_by_date)" in notebook, "notebook must use shared row construction")
    assert_true(".setdefault(date, {})" in source, "notebook must merge datatype values into a date bucket")
    assert_true(
        'pd.DataFrame(rows, columns=["date", "avgTemp", "minTemp", "maxTemp", "prcp"])' in source,
        "notebook must build the dataframe from aligned date rows",
    )
    assert_true("dates_temp = []" not in source, "notebook must not rely on parallel date lists")
    assert_true("temps = []" not in source, "notebook must not rely on parallel value lists")


def test_notebook_rejects_non_text_observation_keys():
    source = project_source()
    assert_true(
        "if not isinstance(date, str) or not isinstance(datatype, str):" in source,
        "NOAA observation date and datatype keys must be textual before bucketing",
    )
    assert_true(
        source.index("if not isinstance(date, str) or not isinstance(datatype, str):")
        < source.index("if not date or datatype not in SUPPORTED_DATATYPES:")
        < source.index("observations = weather_by_date.setdefault(date, {})"),
        "NOAA observation key type guard must run before set membership and bucketing",
    )


def test_conflicting_observations_fail_before_mutation():
    source = RUNTIME_MODULE.read_text()
    method = source.split("def record_observation", 1)[1].split(
        "def parse_noaa_date", 1
    )[0]
    tests = RUNTIME_TESTS.read_text()
    notebook = notebook_source(load_notebook())
    vision = (ROOT / "VISION.md").read_text()
    changes = (ROOT / "CHANGES.md").read_text()

    required_source = (
        'observations = weather_by_date.setdefault(date, {})',
        'value = item.get("value")',
        'if datatype in observations and observations[datatype] != value:',
        'raise ValueError("Conflicting NOAA observation for date and datatype")',
        'observations[datatype] = value',
    )
    for contract in required_source:
        assert_true(
            contract in method,
            "duplicate observation guard must include {0}".format(contract),
        )
    assert_true(
        method.index("if datatype in observations and observations[datatype] != value:")
        < method.index('observations[datatype] = value'),
        "duplicate observation conflicts must fail before mutation",
    )
    for test_name in (
        "test_record_observation_accepts_identical_duplicate",
        "test_record_observation_rejects_conflicting_duplicate_without_mutation",
    ):
        assert_true(
            "def {0}(self):".format(test_name) in tests,
            "duplicate observation tests must remain defined",
        )
    assert_true(
        "from weather_notebook import build_weather_rows, fetch_noaa_data, record_observation"
        in notebook,
        "notebook must continue using the guarded observation helper",
    )
    assert_true(
        "conflicting duplicate NOAA observations" in vision,
        "VISION must preserve conflict rejection",
    )
    assert_true(
        "conflicting duplicate NOAA observations" in changes,
        "CHANGES must record conflict rejection",
    )


def test_notebook_guards_observation_dates_and_values():
    source = project_source()
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
    assert_true(
        "isinstance(value, bool)" in source,
        "NOAA numeric parsing must reject JSON booleans",
    )
    assert_true("number = noaa_number(value)" in source, "unit conversion must use guarded numeric conversion")
    assert_true("import math" in source, "notebook must import math for finite numeric checks")
    assert_true(
        "if not math.isfinite(number):" in source,
        "NOAA numeric parsing must reject NaN and infinite values",
    )
    assert_true("return number * 1.8 + 32" in source, "temperature conversion must use guarded numeric values")
    assert_true("return number / 25.4" in source, "precipitation conversion must use guarded numeric values")


def test_notebook_rejects_empty_valid_observation_rows():
    source = RUNTIME_MODULE.read_text()
    notebook = notebook_source(load_notebook())
    assert_true(
        "if not rows:" in source,
        "notebook must detect when all NOAA observation rows were skipped",
    )
    assert_true(
        'raise ValueError("No valid NOAA observations were available")' in source,
        "empty NOAA observation sets must raise an explicit error",
    )
    assert_true(
        source.index("if not rows:") < source.index("return rows"),
        "row helper must reject empty row sets before returning",
    )
    assert_true(
        notebook.index("rows = build_weather_rows(weather_by_date)")
        < notebook.index('pd.DataFrame(rows, columns=["date", "avgTemp", "minTemp", "maxTemp", "prcp"])'),
        "notebook must build validated rows before dataframe construction",
    )


def test_notebook_skips_rows_without_measurements():
    source = RUNTIME_MODULE.read_text()
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
    assert_completed_plan(CI_PLAN_PATH, "weather notebook CI baseline")
    assert_completed_plan(DEPENDENCY_PLAN_PATH, "weather notebook dependency reproducibility")
    assert_completed_plan(PAGINATION_PLAN_PATH, "NOAA pagination")
    assert_completed_plan(METRIC_UNITS_PLAN_PATH, "NOAA metric units")
    assert_completed_plan(REQUEST_INPUT_PLAN_PATH, "NOAA request input validation")
    assert_completed_plan(METADATA_PAGINATION_PLAN_PATH, "NOAA metadata pagination")
    assert_completed_plan(RESPONSE_OFFSET_PLAN_PATH, "NOAA response offset validation")
    assert_completed_plan(REDIRECT_BOUNDARY_PLAN_PATH, "NOAA token redirect boundary")
    assert_completed_plan(MAKE_ROOT_PROTECTION_PLAN_PATH, "Make root override protection")
    assert_completed_plan(SYNTHETIC_ANALYSIS_PLAN_PATH, "synthetic analysis flow")
    assert_completed_plan(CONFLICTING_OBSERVATION_PLAN_PATH, "conflicting NOAA observations")
    assert_completed_plan(ANALYSIS_PROVENANCE_PLAN_PATH, "weather analysis provenance")
    assert_completed_plan(STABLE_RESULT_COUNT_PLAN_PATH, "stable NOAA result count")
    assert_completed_plan(JUPYTERLAB_SECURITY_PLAN_PATH, "JupyterLab security update")
    assert_completed_plan(MAKE_AUTHORITY_PLAN_PATH, "Make authority isolation")
    assert_completed_plan(README_SETUP_PLAN_PATH, "README setup and dependencies")
    assert_completed_plan(MATPLOTLIB_REFRESH_PLAN_PATH, "Matplotlib 3.11.0 refresh")
    checker_main = Path(__file__).read_text().rsplit("def main():", 1)[1]
    assert_true(
        "test_synthetic_analysis_flow_is_exercised," in checker_main,
        "synthetic analysis-flow contract must run in the main suite",
    )
    assert_true(
        "test_conflicting_observations_fail_before_mutation," in checker_main,
        "conflicting observation contract must run in the main suite",
    )
    assert_true(
        "test_noaa_result_counts_remain_stable_across_pages," in checker_main,
        "stable NOAA result-count contract must run in the main suite",
    )
    assert_true(
        "test_readme_setup_and_dependency_requirements," in checker_main,
        "README setup and dependency contract must run in the main suite",
    )


def test_synthetic_analysis_flow_is_exercised():
    tests = RUNTIME_TESTS.read_text()
    flow_test = tests.split(
        "def test_synthetic_analysis_flow_builds_dataframe_and_plot(self):", 1
    )[1].split("\n\nif __name__", 1)[0]
    notebook = notebook_source(load_notebook())
    vision = (ROOT / "VISION.md").read_text()
    changes = (ROOT / "CHANGES.md").read_text()

    assert_true(
        "def test_synthetic_analysis_flow_builds_dataframe_and_plot(self):" in tests,
        "synthetic analysis test must remain defined",
    )
    for contract in (
        'matplotlib.use("Agg", force=True)',
        "requests_get=fake_get",
        "record_observation(item, weather_by_date)",
        "build_weather_rows(weather_by_date)",
        "pd.DataFrame(",
        'dataframe.plot(kind="line", x="date", y="avgTemp")',
        "plt.close(axes.figure)",
    ):
        assert_true(contract in flow_test, "synthetic analysis test must include {0}".format(contract))
    assert_true(
        "rows = build_weather_rows(weather_by_date)" in notebook,
        "notebook must use the integration-tested row helper",
    )
    assert_true(
        "Exercise the complete offline analysis flow" in vision,
        "VISION must preserve synthetic analysis coverage",
    )
    assert_true(
        "offline synthetic NOAA analysis-flow coverage" in changes,
        "CHANGES must record synthetic analysis coverage",
    )


def test_analysis_provenance_is_visible_and_deterministic():
    runtime = RUNTIME_MODULE.read_text()
    tests = RUNTIME_TESTS.read_text()
    notebook = notebook_source(load_notebook())
    readme = " ".join((ROOT / "README.md").read_text().split())
    security = " ".join((ROOT / "SECURITY.md").read_text().split())
    vision = " ".join((ROOT / "VISION.md").read_text().split())
    changes = " ".join((ROOT / "CHANGES.md").read_text().split())

    for contract in (
        "def format_analysis_provenance(",
        "retrieved_at.astimezone(timezone.utc)",
        'isoformat(timespec="seconds")',
        '.replace("+00:00", "Z")',
    ):
        assert_true(contract in runtime, "runtime provenance helper must include {0}".format(contract))
    for contract in (
        "test_analysis_provenance_normalizes_station_range_and_utc_time",
        "test_analysis_provenance_rejects_ambiguous_inputs",
        'axes.set_title(weather_notebook.format_analysis_provenance(',
        'axes.set_xlabel("Observation date")',
        'axes.set_ylabel("Average temperature (degrees F)")',
    ):
        assert_true(contract in tests, "runtime provenance tests must include {0}".format(contract))
    for contract in (
        "from datetime import datetime, timezone",
        "format_analysis_provenance",
        "RETRIEVED_AT = datetime.now(timezone.utc)",
        "axes.set_title(format_analysis_provenance(",
        'axes.set_xlabel("Observation date")',
        'axes.set_ylabel("Average temperature (degrees F)")',
    ):
        assert_true(contract in notebook, "notebook provenance flow must include {0}".format(contract))
    assert_true(
        notebook.index("record_observation(item, weather_by_date)") <
        notebook.index("RETRIEVED_AT = datetime.now(timezone.utc)") <
        notebook.index("rows = build_weather_rows(weather_by_date)"),
        "retrieval completion time must be captured after NOAA collection and before plotting",
    )
    assert_true("repository's original sample selection" in readme,
                "README must explain the station choice")
    assert_true("keeps the analysis bounded and historical" in readme,
                "README must explain the date-range choice")
    assert_true("UTC retrieval completion time" in security, "SECURITY must preserve plot provenance")
    assert_true("Include NOAA source, station, historical range" in vision,
                "VISION must preserve generated plot provenance")
    assert_true("deterministic provenance validation" in changes,
                "CHANGES must record provenance validation")
    assert_true("Document station and date-range choices" not in vision,
                "completed station/date documentation must leave next priorities")
    assert_true("Add data-source timestamps to generated outputs" not in vision,
                "completed output timestamps must leave next priorities")


def test_dependency_and_ci_contracts():
    expected_requirements = [
        "jupyter==1.1.1",
        "matplotlib==3.11.0",
        "numpy==2.4.6",
        "pandas==3.0.3",
        "requests==2.34.2",
    ]
    requirements = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert_true(requirements == expected_requirements, "requirements must match the exact direct dependency pins")
    expected_direct = {
        re.sub(r"[-_.]+", "-", name).lower(): version
        for name, version in (requirement.split("==", 1) for requirement in expected_requirements)
    }

    for lock_name in ("requirements-py312.lock", "requirements-py314.lock"):
        lock_path = ROOT / lock_name
        assert_true(lock_path.is_file(), "{0} must be checked in".format(lock_name))
        lock_bytes = lock_path.read_bytes()
        assert_true(
            hashlib.sha256(lock_bytes).hexdigest() == LOCKFILE_SHA256[lock_name],
            "{0} must match the reviewed lock digest".format(lock_name),
        )
        lock_text = lock_bytes.decode("utf-8")
        assert_true("#    make lock" in lock_text, "{0} must document reproducible generation".format(lock_name))
        lock_lines = lock_text.splitlines()
        active_indexes = [
            index
            for index, line in enumerate(lock_lines)
            if line and not line.startswith((" ", "#"))
        ]
        assert_true(active_indexes, "{0} must contain locked packages".format(lock_name))
        locked_packages = {}
        for position, index in enumerate(active_indexes):
            line = lock_lines[index]
            end = active_indexes[position + 1] if position + 1 < len(active_indexes) else len(lock_lines)
            block = lock_lines[index:end]
            assert_true(
                "==" in line and line.endswith(" \\") and any("--hash=sha256:" in item for item in block),
                "{0} package entries must be exact pins with hashes".format(lock_name),
            )
            name, version = line[:-2].split("==", 1)
            normalized_name = re.sub(r"[-_.]+", "-", name).lower()
            assert_true(normalized_name not in locked_packages, "{0} must not duplicate packages".format(lock_name))
            locked_packages[normalized_name] = version
        for name, version in expected_direct.items():
            assert_true(
                locked_packages.get(name) == version,
                "{0} must contain active direct pin {1}=={2}".format(lock_name, name, version),
            )
        assert_true(
            locked_packages.get("jupyter-server") == "2.20.0",
            "{0} must contain the reviewed jupyter-server security pin".format(lock_name),
        )
        assert_true(
            locked_packages.get("jupyterlab") == "4.5.9",
            "{0} must contain the reviewed jupyterlab security pin".format(lock_name),
        )

    workflow = CI_WORKFLOW_PATH.read_text()
    assert_true(workflow == EXPECTED_WORKFLOW, "CI workflow must match the fail-closed baseline")
    workflow_files = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))
    assert_true(workflow_files == [CI_WORKFLOW_PATH], "check.yml must be the only workflow")

    makefile = (ROOT / "Makefile").read_text()
    makefile_lines = set(makefile.splitlines())
    for contract in (
        ".DEFAULT_GOAL := check",
        ".SECONDEXPANSION:",
        "PYTHON ?= python3",
        "override PYTHON := $(value PYTHON)",
        "UV ?= uv",
        "override UV := $(value UV)",
        "override SHELL := /bin/sh",
        "override .SHELLFLAGS := -c",
        "override MAKEFILES :=",
        "ifneq ($(origin MAKEFILE_LIST),file)",
        "export ROOT",
        "root-test::",
        "\t/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'",
        "$(eval $(REPOSITORY_PUBLIC_RECIPES))",
    ):
        assert_true(contract in makefile_lines, "Makefile authority contract is missing {0!r}".format(contract))
    assert_true("MAKEFLAGS must not be overridden" in makefile, "Makefile must reject caller MAKEFLAGS")
    assert_true("MAKEFILES must be empty" in makefile, "Makefile must reject startup files")
    assert_true("MAKEFILE_LIST must not be overridden" in makefile, "Makefile must reject Makefile-list replacement")
    assert_true("PYTHON must be a literal executable path" in makefile, "Makefile must reject Python Make syntax")
    assert_true("UV must be a literal executable path" in makefile, "Makefile must reject uv Make syntax")
    assert_true(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'" in makefile,
        "Makefile must use the rooted authority harness",
    )
    assert_true(
        "scripts/check_weather_notebook_contracts.py" in makefile,
        "Makefile must use the rooted notebook contract path",
    )
    assert_true(
        "/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)'" in makefile,
        "Makefile cleanup must stay inside the repository",
    )
    assert_true(
        "'$(REPOSITORY_PYTHON_LITERAL)' -I -B -c "
        "'import runpy, sys; sys.path.insert(0, \".\"); "
        "runpy.run_path(\"weather_notebook_tests.py\", run_name=\"__main__\")'" in makefile,
        "Makefile must run executable NOAA helper tests",
    )
    assert_true("verify:: root-test lint test build" in makefile_lines, "full verification must run authority tests")
    lock_command_template = (
        "'$(REPOSITORY_UV_LITERAL)' pip compile '$(REPOSITORY_ROOT_LITERAL)/requirements.txt' "
        "--python-version {python_version} "
        '--python-platform x86_64-manylinux_2_28 --default-index https://pypi.org/simple '
        "--generate-hashes --custom-compile-command 'make lock' "
        "--output-file '$(REPOSITORY_ROOT_LITERAL)/{lockfile}'"
    )
    for python_version, lockfile in (("3.12", "requirements-py312.lock"), ("3.14", "requirements-py314.lock")):
        assert_true(
            lock_command_template.format(python_version=python_version, lockfile=lockfile) in makefile,
            "Makefile must preserve the reviewed {0} lock command".format(python_version),
        )
    assert_true(
        makefile.count(
            "'$(REPOSITORY_UV_LITERAL)' pip compile '$(REPOSITORY_ROOT_LITERAL)/requirements.txt'"
        ) == 2,
        "Makefile must define exactly two frozen lock commands",
    )

    authority_test = (ROOT / "scripts" / "test-makefile-root.sh").read_text()
    for contract in (
        "40 target/authority cases",
        "literal hostile Python and UV paths",
        "6 raw Make-syntax controls",
        "2 MAKEFILE_LIST rejections",
        "2 startup parse-time boundary reproductions",
        "8 later single-colon replacement rejections",
        "8 later double-colon append boundary reproductions",
        "PATH-Python/PATH-UV boundary controls",
        "cleanup containment",
        "10 mode rejections",
    ):
        assert_true(contract in authority_test, "Make authority harness must include {0!r}".format(contract))
    assert_true(RUNTIME_MODULE.is_file(), "NOAA runtime helpers must be importable")
    assert_true(RUNTIME_TESTS.is_file(), "NOAA runtime helper tests must be checked in")

    for docs_file in ("README.md", "VISION.md", "SECURITY.md", "CHANGES.md"):
        assert_true(
            "GitHub Actions" in (ROOT / docs_file).read_text(),
            "{0} must document the GitHub Actions baseline".format(docs_file),
        )
    docs_text = "\n".join(
        (ROOT / docs_file).read_text()
        for docs_file in ("README.md", "CHANGES.md", "docs/plans/2026-06-21-make-authority-isolation.md")
    )
    for phrase in (
        "Caller-supplied double-colon public recipes and startup makefile parse-time code are outside the local Make trust boundary.",
        "Documented caller-added double-colon public recipes and startup parse-time Make code as outside the local Make trust boundary.",
        "Startup makefiles can run parse-time Make functions before the repository Makefile rejects them.",
    ):
        assert_true(phrase in docs_text, "Make boundary documentation must include {0!r}".format(phrase))


def test_readme_setup_and_dependency_requirements():
    readme = " ".join((ROOT / "README.md").read_text().split())
    vision = " ".join((ROOT / "VISION.md").read_text().split())
    changes = " ".join((ROOT / "CHANGES.md").read_text().split())

    for contract in (
        "CPython 3.12 or 3.14",
        "reproducible Linux x86_64 installs",
        "requirements-py312.lock",
        "requirements-py314.lock",
        "python3.12 -m venv .venv",
        "python3.14 -m venv .venv",
        "Do not install `requirements.txt` directly for a reviewed environment",
        "`uv` is required only to regenerate both lockfiles with `make lock`",
        "`NOAA_TOKEN` is not required for `make check`",
    ):
        assert_true(contract in readme, "README setup guidance must include {0}".format(contract))
    for requirement in (
        line.strip()
        for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ):
        assert_true("`{0}`".format(requirement) in readme, "README must list direct pin {0}".format(requirement))
    assert_true(
        "Keep README setup and exact dependency requirements aligned with the supported lockfiles" in vision,
        "VISION must preserve setup and lockfile guidance",
    )
    assert_true(
        "matching Python 3.12 or 3.14 lockfile" in changes,
        "CHANGES must record supported lockfile selection",
    )


def main():
    tests = [
        test_noaa_token_comes_from_environment,
        test_noaa_requests_are_parameterized_and_bounded,
        test_noaa_request_inputs_are_validated_before_network_use,
        test_noaa_metric_units_are_explicit_and_converted,
        test_noaa_requests_are_paginated_with_a_safety_bound,
        test_noaa_pagination_metadata_is_validated,
        test_noaa_response_offsets_are_validated_before_accumulation,
        test_noaa_result_counts_remain_stable_across_pages,
        test_noaa_result_shape_is_checked,
        test_notebook_has_no_stale_outputs,
        test_notebook_aligns_observations_by_date,
        test_notebook_rejects_non_text_observation_keys,
        test_conflicting_observations_fail_before_mutation,
        test_notebook_guards_observation_dates_and_values,
        test_notebook_rejects_empty_valid_observation_rows,
        test_notebook_skips_rows_without_measurements,
        test_completed_plans_are_in_docs_plans,
        test_synthetic_analysis_flow_is_exercised,
        test_analysis_provenance_is_visible_and_deterministic,
        test_dependency_and_ci_contracts,
        test_readme_setup_and_dependency_requirements,
    ]
    for test in tests:
        test()
    print("weather notebook contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
