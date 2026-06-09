# Weather Notebook Value Guards

## Status: Completed

## Context

The notebook already validates NOAA response containers and aligns observations
by date, but row construction still assumed every observation date matched the
expected timestamp format and every value could be converted to a float. A
malformed API row should not crash the whole exploratory analysis.

## Objectives

- Preserve the NOAA station analysis flow.
- Parse NOAA timestamps through a guarded helper.
- Skip malformed NOAA dates before appending dataframe rows.
- Convert numeric NOAA values through a guarded helper.
- Treat malformed numeric observations as missing values.
- Keep static checks covering the value parsing guardrails.

## Work Completed

- Added `parse_noaa_date` to return `None` for malformed timestamps.
- Added `noaa_number` to return `None` for missing or non-numeric values.
- Updated temperature and precipitation conversion helpers to use guarded
  numeric conversion.
- Skipped rows with invalid dates before building the dataframe.
- Extended `scripts/check_weather_notebook_contracts.py` and updated README,
  VISION, and CHANGES.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Document station and date-range choices in more detail.
- Add data-source timestamps to generated outputs.
