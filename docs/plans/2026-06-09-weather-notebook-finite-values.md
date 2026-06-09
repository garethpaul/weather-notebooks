# Weather Notebook Finite Values

## Status: Completed

## Context

The notebook already guarded malformed NOAA numeric fields, but `float("nan")`
and `float("inf")` produce values that can flow into unit conversion and plots.
Those non-finite values should be treated like malformed observations.

## Objectives

- Preserve NOAA date-aligned row construction.
- Keep malformed numeric fields from crashing unit conversion.
- Reject NaN and infinite numeric values before unit conversion.
- Keep the notebook output-free and dependency-light.

## Work Completed

- Imported `math` in the notebook setup cell.
- Updated `noaa_number` to reject non-finite floats before returning values.
- Added static checker coverage for finite numeric parsing.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Raise an explicit error when the NOAA response root is not a JSON object.
- Add pagination if the configured date range exceeds NOAA result limits.
