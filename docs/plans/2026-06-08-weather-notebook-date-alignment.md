# Weather Notebook Date Alignment Plan

Date: 2026-06-08

Status: Completed

## Goal

Make the NOAA notebook resilient to missing daily datatype observations by
aligning values by observation date before building the dataframe.

## Scope

- Replace parallel datatype lists with a `weather_by_date` collection.
- Record NOAA results into date buckets keyed by datatype.
- Build the dataframe from sorted date rows with explicit columns.
- Preserve cleared notebook outputs and environment-based NOAA token loading.
- Add a dependency-free static contract for date-aligned row construction.

## TDD Notes

- Red: `python3 scripts/check_weather_notebook_contracts.py` failed with
  `AssertionError: notebook must collect NOAA observations by date`.
- Green: `python3 scripts/check_weather_notebook_contracts.py` passed after
  moving the notebook transformation to date-keyed rows and adding this plan.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `git diff --check`
