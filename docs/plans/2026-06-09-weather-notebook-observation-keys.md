# Weather Notebook Observation Key Guards

## Status: Completed

## Context

`record_observation` skipped non-dictionary NOAA rows, but it accepted truthy
non-string `date` values and could test non-string `datatype` values against
the supported datatype set. Malformed observation keys could therefore raise
before the later date parser skipped them, or be stored in `weather_by_date`
and break sorted row construction.

## Objectives

- Keep the date-aligned observation bucketing behavior.
- Reject non-text `date` and `datatype` values before set membership checks.
- Reject malformed observation keys before adding rows to `weather_by_date`.
- Cover the notebook source with dependency-free static contracts.

## Work Completed

- Added a text-type guard for NOAA observation `date` and `datatype` fields.
- Kept the existing supported-datatype and blank-date checks after the type
  guard.
- Added static checker coverage for the guard order before bucketing.
- Updated README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
