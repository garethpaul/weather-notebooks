# Weather Notebook Reproducibility Plan

Date: 2026-06-08

Status: Completed

## Goal

Make the NOAA weather notebook safer to rerun by keeping API tokens local, bounding network calls, and removing stale checked-in outputs.

## Scope

- Load the NOAA CDO API token from `NOAA_TOKEN` instead of a notebook literal.
- Use structured `requests.get(..., params=..., timeout=...)` calls and fail fast on HTTP errors.
- Make the station and date range constants explicit in the notebook.
- Clear saved notebook outputs and execution counts so historical output is not presented as current data.
- Add a dependency-free notebook contract and local verification targets.

## TDD Notes

- Red: `python3 scripts/check_weather_notebook_contracts.py` failed with `AssertionError: NOAA requests must set a timeout`.
- Red: after notebook normalization, the same contract failed with `AssertionError: weather notebook plan must live under docs/plans`.
- Green: `python3 scripts/check_weather_notebook_contracts.py` passed after adding the completed plan.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
