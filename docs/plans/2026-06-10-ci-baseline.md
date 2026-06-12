# Weather Notebooks CI Baseline

## Status: Completed

## Context

`weather-notebooks` has static notebook reproducibility, token, NOAA response,
and value-shape contracts behind `make check`. The repository needs that
offline baseline to run in GitHub Actions before review.

## Objectives

- Run the existing `make check` wrapper in GitHub Actions.
- Keep the hosted job offline and independent of NOAA credentials.
- Make the workflow presence part of the notebook contract baseline.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 for the static notebook checker.
- Extended `scripts/check_weather_notebook_contracts.py` to require the CI
  workflow and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check_weather_notebook_contracts.py`
- `git diff --check`

## Follow-Up Candidates

- Add notebook execution smoke tests only after a synthetic NOAA fixture is
  documented.
