# Changes

## 2026-06-18

- Updated both hashed Python lockfiles to `jupyter-server` 2.20.0 to remediate
  CVE-2026-44727 while preserving the existing direct dependency set.
- Added a fail-closed contract for the reviewed transitive security pin and
  refreshed both lockfile integrity digests.

## 2026-06-16

- Rejected NOAA result-count drift across paginated responses before later
  observations can alter the accumulated analysis.
- Rejected conflicting duplicate NOAA observations before they can overwrite
  an earlier value while keeping identical repeated records idempotent.
- Added executable and static contracts for conflict detection and
  pre-mutation ordering.
- Added NOAA source, normalized station, inclusive historical range, and UTC
  retrieval completion time to the average-temperature plot title.
- Added explicit observation-date and Fahrenheit axis labels plus deterministic
  provenance validation in the offline synthetic plot flow.

## 2026-06-14

- Added offline synthetic NOAA analysis-flow coverage from fake API responses
  through observation bucketing, converted dataframe rows, and a headless
  average-temperature plot.
- Extracted deterministic dataframe row construction for shared notebook and
  executable-test use.

## 2026-06-13

- Disabled redirects on token-bearing NOAA requests so provider credentials
  cannot be forwarded to a different origin.
- Added executable and static ordering coverage for redirect rejection before
  response JSON parsing.
- Validated optional NOAA response offsets against each requested record before
  accumulating page results.
- Rejected malformed response offsets and added deterministic pagination tests.

## 2026-06-12

- Validated and normalized NOAA helper years, datatypes, tokens, and station
  identifiers before the first network request.
- Added fail-fast unit and static contract coverage for malformed inputs.

## 2026-06-10

- Added a GitHub Actions check workflow that runs the existing offline
  `make check` notebook contract baseline on pushes, pull requests, and manual
  dispatches.
- Added static checker coverage requiring the CI workflow and completed CI
  baseline plan to remain checked in.
- Requested scaled metric NOAA values explicitly and corrected Celsius and
  millimeter conversions, including the precipitation inches divisor.
- Added bounded NOAA offset pagination so result sets larger than 1,000 rows
  are complete and a 20-page safety-limit exhaustion fails explicitly.
- Made Make execution root-independent and fixed hosted checks to Ubuntu 24.04
  with exact action release annotations.
- Pinned the current stable Jupyter, Matplotlib, NumPy, pandas, and Requests
  releases after direct OSV checks returned no advisories.
- Added pinned, read-only Python 3.12/3.14 CI that installs and imports the
  scientific stack before running offline notebook contracts.
- Made the hosted workflow fail closed through an exact checked-in contract,
  credential-free checkout, all-branch triggers, and external-directory checks.
- Extracted NOAA request and conversion helpers into an importable module and
  added executable fake-HTTP pagination, validation, and safety-bound tests.
- Made the direct dependency contract compare the complete active requirements
  list instead of accepting pinned names in comments or extra unpinned entries.
- Added Python 3.12 and 3.14 hash-locked transitive dependency graphs and made
  hosted installs use pip hash enforcement.

## 2026-06-09

- Trimmed `NOAA_TOKEN` before validation so blank or whitespace-only token
  values fail before requests are made.
- Added static checker coverage for NOAA token whitespace normalization.
- Rejected non-text NOAA observation `date` and `datatype` values before
  supported-datatype checks and date bucketing.
- Added static checker coverage for observation key type guards.
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
