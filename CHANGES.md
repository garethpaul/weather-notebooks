# Changes

## 2026-06-09

- Skipped date-valid NOAA rows when every converted measurement value is
  missing or malformed before dataframe construction.
- Added static checker coverage for measurement-empty row filtering.
- Raised an explicit error when NOAA returns a non-object JSON response root.
- Added static checker coverage for NOAA response root-shape failures.
- Raised an explicit error when no valid NOAA observations remain after parsing.
- Added static checker coverage for empty parsed observation sets.
- Rejected NaN and infinite NOAA numeric values before unit conversion.
- Added static checker coverage for finite NOAA observation values.
- Added guarded NOAA timestamp and numeric value parsing before dataframe row
  construction.
- Added static checker coverage for malformed observation date and value
  handling.

## 2026-06-08

- Added explicit NOAA JSON result-shape checks before processing observation
  rows.
- Aligned NOAA datatype observations by date before constructing the weather dataframe.
- Tightened docs-plan verification to require recorded `make check` evidence.
- Loaded NOAA CDO API tokens from the `NOAA_TOKEN` environment variable instead of notebook literals.
- Added structured NOAA request parameters, HTTP error checks, and bounded request timeouts.
- Cleared saved notebook outputs so stale 2019 data is not displayed as current output.
- Added a dependency manifest and local notebook contract checks.
