# Weather Notebook Measurement Rows

## Status: Completed

## Context

The notebook already rejects malformed dates, malformed numeric values, NaN or
infinite values, and completely empty parsed observation sets. A row with a
valid date but no converted temperature or precipitation value could still be
added to the dataframe, which would let the notebook plot dates with no usable
measurements.

## Objectives

- Preserve date-aligned NOAA row construction.
- Convert each supported measurement once before row append.
- Skip date-valid rows when every converted measurement is missing.
- Keep empty parsed observation set detection before dataframe construction.
- Extend static checks so measurement-empty rows do not return.

## Work Completed

- Stored converted average, minimum, and maximum temperatures before appending
  dataframe rows.
- Stored converted precipitation before appending dataframe rows.
- Skipped rows when all converted measurement values are `None`.
- Updated dataframe row construction to use the guarded converted values.
- Extended `scripts/check_weather_notebook_contracts.py` with
  measurement-empty row checks and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_weather_notebook_contracts.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Extract row-building helpers into a small Python module for direct unit
  testing.
- Add plot labels that describe the station, date range, and filtered row
  count.
