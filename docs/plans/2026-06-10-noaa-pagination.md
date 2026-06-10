# NOAA Pagination

Status: Completed

## Context

The NOAA request set `limit=1000` but never requested subsequent pages. Years
with more than 1,000 matching observations were silently truncated, producing
incomplete dataframes and plots.

## Changes

- Added NOAA `offset` pagination with 1,000 results per page.
- Accumulated pages until NOAA returns a short page.
- Bounded each request group to 20 pages and raised an explicit error if the
  upstream response exhausts that safety limit.
- Added static contracts for pagination, stable CI, and rooted Make execution.

## Verification

- `make check`
- `python3 -m py_compile scripts/check_weather_notebook_contracts.py`
- Mutation checks for offsets, accumulation, termination, CI, and Make paths
- `git diff --check`

Live NOAA execution requires a user-provided `NOAA_TOKEN` and was not claimed.
