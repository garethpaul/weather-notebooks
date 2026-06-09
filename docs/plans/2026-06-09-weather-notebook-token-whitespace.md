# Weather Notebook Token Whitespace Guard

Status: Completed

## Context

The notebook already loads the NOAA Climate Data Online token from
`NOAA_TOKEN` instead of storing a literal token in source. A whitespace-only
environment value still passed the local presence check and would only fail
later as an API request problem.

## Plan

- Strip surrounding whitespace when reading `NOAA_TOKEN`.
- Keep the existing explicit runtime error for missing or blank tokens.
- Extend `scripts/check_weather_notebook_contracts.py` so future notebook edits
  keep token normalization before validation.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `make verify`
- `git diff --check`
