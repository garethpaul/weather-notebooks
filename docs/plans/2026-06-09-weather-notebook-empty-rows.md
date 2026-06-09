# Weather Notebook Empty Rows

## Status: Completed

## Context

The notebook now guards malformed NOAA response containers, dates, and numeric
values. If every observation row is skipped after those guards run, the notebook
could still construct and plot an empty dataframe, making a data-quality problem
look like a valid empty chart.

## Objectives

- Preserve the existing NOAA fetch and transformation flow.
- Detect when no valid parsed observation rows remain.
- Raise an explicit error before dataframe construction and plotting.
- Keep the notebook output-free and covered by static checks.

## Work Completed

- Added an `if not rows` guard before dataframe construction.
- Raised `ValueError("No valid NOAA observations were available")` for empty
  parsed observation sets.
- Extended `scripts/check_weather_notebook_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check: `python3 scripts/check_weather_notebook_contracts.py` failed
  before the empty-row guard was added.
- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add pagination if the configured date range exceeds NOAA result limits.
- Extract NOAA fetching into a testable Python module with unit tests.
