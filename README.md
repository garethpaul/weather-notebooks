# weather-notebooks

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/weather-notebooks` is a reproducible NOAA weather-data notebook and
an importable set of request, validation, conversion, dataframe, and plotting
helpers.

The checked-in analysis uses a fixed historical station and date range. It does
not provide current-weather conditions or a representative climate series.

## Repository Contents

- `Weather.ipynb` - the preserved interactive NOAA analysis
- `weather_notebook.py` - reusable NOAA request and transformation helpers
- `weather_notebook_tests.py` - dependency-aware offline behavior tests
- `requirements.txt` - five exact direct dependency pins used as lock input
- `requirements-py312.lock` and `requirements-py314.lock` - reviewed complete
  Linux dependency graphs with SHA-256 hashes
- `Makefile` and `scripts/` - canonical verification, lock generation, static
  contracts, and Make authority tests
- `SECURITY.md` and `VISION.md` - security and maintenance guardrails

## Getting Started

### Prerequisites

- Git
- CPython 3.12 or 3.14 with `venv` and pip
- A NOAA Climate Data Online API token available as `NOAA_TOKEN` only when
  running the live notebook

The repository supports reproducible Linux x86_64 installs only for the two
Python versions with reviewed lockfiles:

- Python 3.12 uses `requirements-py312.lock`.
- Python 3.14 uses `requirements-py314.lock`.

Do not install `requirements.txt` directly for a reviewed environment. It is
the five-package direct input to lock generation; the version-matched lockfile
contains the complete transitive graph and required hashes. `uv` is required
only to regenerate both lockfiles with `make lock`, not for normal setup.

The direct dependency requirements are:

- `jupyter==1.1.1`
- `matplotlib==3.10.9`
- `numpy==2.4.6`
- `pandas==3.0.3`
- `requests==2.34.2`

### Setup

```bash
git clone https://github.com/garethpaul/weather-notebooks.git
cd weather-notebooks
```

Create exactly one of the following environments.

#### Python 3.12

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-py312.lock
```

#### Python 3.14

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-py314.lock
```

Then verify the selected environment:

```bash
python -c "import jupyter, matplotlib, numpy, pandas, requests"
make check
```

`NOAA_TOKEN` is not required for `make check`; the gate is offline and uses fake
responses. Export the token only in the shell that launches a live notebook:

```bash
export NOAA_TOKEN=your-noaa-token
jupyter notebook Weather.ipynb
```

If the selected interpreter is unavailable, install CPython 3.12 or 3.14 rather
than applying the other lockfile to an unreviewed Python version. A different
operating system or CPU architecture needs a separately generated and reviewed
lockfile before the environment can be called reproducible.

## Running or Using the Project

- Run `jupyter notebook Weather.ipynb` after installing the matching lockfile
  and setting `NOAA_TOKEN` in the launch shell.
- The notebook fetches NOAA CDO observations for station `GHCND:US1CAMR0037` across the configured date range.
- The station is the repository's original sample selection, and the fixed
  2019 range keeps the analysis bounded and historical. Neither is claimed as
  a representative climate series or current-weather source.
- NOAA requests explicitly use metric units; Celsius temperatures and
  millimeter precipitation are converted for Fahrenheit/inch presentation.
- Token-bearing NOAA requests do not follow redirects, keeping credentials on
  the configured Climate Data Online API origin.
- NOAA result sets are fetched in 1,000-row pages with a 20-page safety limit
  per request group; exhausting the limit raises instead of silently truncating.
- The average-temperature plot identifies NOAA CDO, the station, inclusive
  observation range, UTC retrieval completion time, and Fahrenheit display
  units so exported screenshots retain their analysis context.

## Testing and Verification

- `make verify` runs static notebook reproducibility, token-safety, date
  alignment, NOAA root/result-shape, observation key, finite numeric value,
  observation value-guard, token whitespace, metric-unit conversion,
  pagination, response-offset validation, redirect-boundary, measurement-row,
  and empty-row
  checks. It also runs executable
  fake-HTTP tests for pagination, payload validation, failure propagation,
  request bounds, and unit conversions.
- `make check` runs `make verify` with bytecode cleanup before and after.
- The Make entry points derive their root from the reviewed Makefile and reject
  caller shell, startup-file, Makefile-list, unsafe-mode, executable Make
  syntax, and later public-recipe replacement. `PYTHON` and `UV` remain
  literal caller-selectable executables; `PATH` lookup for their defaults and
  later GNU Make `override` directives are explicit trust boundaries.
- Caller-supplied double-colon public recipes and startup makefile parse-time code are outside the local Make trust boundary.
- GitHub Actions installs the exact scientific stack and runs offline contracts
  on every push, pull request, and manual dispatch for Python 3.12 and 3.14 on
  Ubuntu 24.04 with read-only permissions, immutable action pins,
  credential-free checkout, and cancellation for superseded runs.
- The hosted matrix invokes `/usr/bin/make` and reruns the full gate from an
  external working directory.
- `python3 scripts/check_weather_notebook_contracts.py` runs just the notebook contracts.
- `python3 -m unittest weather_notebook_tests` runs the executable NOAA helper
  tests plus an offline synthetic flow through fake responses, date bucketing,
  converted pandas rows, and a headless matplotlib line plot without a token or
  network request. The synthetic plot also verifies deterministic provenance
  title and axis labels.
- `make lock` regenerates reviewed Python 3.12 and 3.14 Linux lockfiles with
  SHA-256 hashes from the five direct pins in `requirements.txt`.
- See `docs/plans/2026-06-26-readme-setup-and-dependencies.md` for the supported
  interpreter, lock-selection, token, and lock-regeneration guidance.
- Hosted installs use pip `--require-hashes` against the matrix-matched lock;
  the current 106-package graph returned no findings from the official OSV API.
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- `NOAA_TOKEN` is required to fetch NOAA Climate Data Online data. Keep it in
  your local environment and out of git; blank or whitespace-only values are
  rejected before requests are made. The reusable fetch helper also rejects
  invalid years, datatypes, and station identifiers before network use.
- NOAA result counts must remain stable across paginated responses; count drift
  fails before a later page can alter the accumulated analysis.
- Do not commit NOAA API tokens, private datasets, or refreshed outputs without source dates.

## Security and Privacy Notes

- The scan did not identify production authentication, payment, or secret-management code. Treat future additions in those areas as security-sensitive.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-weather-notebook-reproducibility.md` for the
  current notebook reproducibility baseline.
- See `docs/plans/2026-06-08-weather-notebook-date-alignment.md` for the NOAA
  datatype date-alignment contract.
- See `docs/plans/2026-06-08-weather-notebook-result-shape.md` for NOAA JSON
  result-shape handling.
- See `docs/plans/2026-06-09-weather-notebook-value-guards.md` for malformed
  NOAA date and numeric value handling.
- See `docs/plans/2026-06-09-weather-notebook-finite-values.md` for NaN and
  infinite NOAA numeric value handling.
- See `docs/plans/2026-06-09-weather-notebook-response-root.md` for explicit
  NOAA response root-shape errors.
- See `docs/plans/2026-06-09-weather-notebook-empty-rows.md` for rejecting
  empty parsed observation sets before plotting.
- See `docs/plans/2026-06-09-weather-notebook-measurement-rows.md` for
  filtering date-valid rows that have no usable converted measurements.
- See `docs/plans/2026-06-09-weather-notebook-observation-keys.md` for
  rejecting non-text NOAA observation date and datatype keys before bucketing.
- See `docs/plans/2026-06-09-weather-notebook-token-whitespace.md` for
  trimming and rejecting blank NOAA token environment values before requests.
- See `docs/plans/2026-06-10-ci-baseline.md` for the GitHub Actions baseline.
- See `docs/plans/2026-06-10-dependency-reproducibility.md` for exact scientific
  stack pins and hosted import verification.
- See `docs/plans/2026-06-10-noaa-pagination.md` for bounded NOAA result
  pagination and explicit safety-limit failure.
- See `docs/plans/2026-06-10-noaa-metric-units.md` for explicit NOAA unit
  scaling and corrected display conversions.
- See `docs/plans/2026-06-12-noaa-request-input-validation.md` for fail-fast
  validation and normalization at the reusable NOAA request boundary.
- See `docs/plans/2026-06-13-noaa-metadata-pagination.md` for result-count-aware
  NOAA pagination and record-based offset advancement.
- See `docs/plans/2026-06-13-noaa-response-offset-validation.md` for validating
  optional response offsets before accumulating NOAA pages.
- See `docs/plans/2026-06-13-noaa-token-redirect-boundary.md` for keeping the
  NOAA token on the configured API origin.
- See `docs/plans/2026-06-14-synthetic-analysis-flow.md` for deterministic
  offline dataframe and plotting coverage.
- See `docs/plans/2026-06-16-weather-analysis-provenance.md` for station,
  historical range, UTC retrieval-time, and display-unit plot context.
- See `docs/plans/2026-06-16-stable-noaa-result-count.md` for fail-closed
  pagination count consistency.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
