## Weather Notebooks Vision

Weather Notebooks is a notebook-based NOAA weather data experiment that fetches
station data, converts temperature and precipitation values, builds a pandas
dataframe, and plots average temperature.

The repository is useful as a small exploratory analysis of NOAA API access and
weather-data transformation.

The goal is to preserve the notebook while making tokens, station assumptions,
data provenance, and reproducibility explicit.

The current focus is:

Priority:

- Preserve the notebook analysis flow
- Keep NOAA tokens as local user-provided values
- Reject blank or whitespace-only NOAA token values before requests
- Make station ID, date range, and unit conversions visible
- Validate NOAA result shapes before converting observations
- Raise explicit errors for unexpected NOAA response roots
- Reject non-text NOAA observation date and datatype keys before bucketing
- Guard malformed NOAA dates and numeric values before building rows
- Reject NaN and infinite NOAA numeric values before plotting
- Reject empty parsed observation sets before plotting
- Skip date-valid rows that have no usable converted measurements
- Keep GitHub Actions running the offline `make check` baseline before review
- Avoid presenting historical data as current conditions

Next priorities:

- Add README setup notes and dependency requirements
- Document station and date-range choices
- Extract NOAA fetching into a testable Python module
- Add data-source timestamps to generated outputs

Contribution rules:

- One PR = one focused data source, notebook, visualization, dependency, or documentation change.
- Do not commit API tokens or private datasets.
- Keep dataset refreshes sourced and dated.
- Keep `.github/workflows/check.yml` aligned with the offline notebook contract
  baseline.
- Preserve unit conversion notes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Weather notebooks can leak API tokens and create misleading stale analysis.
Tokens should stay local, and outputs should clearly identify source dates and
station scope.

## What We Will Not Merge (For Now)

- Checked-in API tokens
- Current-weather claims from stale data
- Dataset refreshes without source dates
- Hidden network calls outside the documented API

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
