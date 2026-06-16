# Weather Analysis Provenance

## Status: Completed

## Context

The notebook plots average temperature without identifying its NOAA source,
station, historical date range, display units, or retrieval time. A screenshot
or exported figure can therefore lose the context needed to distinguish this
fixed 2019 sample from current conditions or another station's observations.

## Requirements

- Add a reusable formatter for NOAA analysis provenance containing the data
  source, normalized station ID, inclusive observation range, and UTC retrieval
  completion timestamp.
- Reject blank station IDs, invalid year bounds, non-datetime timestamps, and
  timezone-naive timestamps instead of emitting ambiguous labels.
- Normalize aware timestamps to second-precision UTC with a `Z` suffix.
- Capture retrieval completion time after NOAA collection and apply the
  provenance string as the plot title.
- Label the plot axes as observation date and average temperature in degrees
  Fahrenheit.
- Extend the offline synthetic flow to assert the exact title, labels, and
  deterministic timestamp formatting without a token or network call.
- Document why the sample uses station `GHCND:US1CAMR0037` and the fixed 2019
  historical range, without claiming representativeness or current conditions.
- Preserve output-free, token-free notebook JSON and all existing request,
  conversion, dataframe, and plotting behavior.

## Key Decision

Keep provenance formatting in `weather_notebook.py` and inject an aware
`datetime` so executable tests remain deterministic. The notebook owns the
actual `datetime.now(timezone.utc)` call after data collection; the helper owns
validation, UTC normalization, and inclusive range formatting.

## Verification Plan

- Run focused formatter and synthetic plot tests.
- Run hostile mutations for missing source/station/range/timestamp, naive-time
  acceptance, wrong UTC normalization, missing title, and missing unit labels.
- Run bounded repository and external-directory `make check` gates with the
  pinned Python 3.12 lock environment.
- Audit notebook JSON and outputs, exact diff, generated artifacts, whitespace,
  file modes, and changed lines for credential material.

## Scope Boundaries

- Do not fetch live NOAA data, change station/date defaults, refresh datasets,
  save figures, or commit notebook outputs or execution counts.
- Do not change dependencies, lockfiles, workflows, request parameters, token
  handling, pagination, unit conversion, or dataframe columns.
- Do not merge or close stacked pull requests without explicit authorization.

## Work Completed

- Added validated NOAA source, normalized station, inclusive date range, and
  second-precision UTC retrieval-time formatting.
- Captured retrieval completion after NOAA collection and applied the
  provenance title plus explicit observation-date and Fahrenheit axis labels.
- Extended the offline synthetic plot and static contracts for deterministic
  metadata, notebook ordering, documentation, and roadmap completion.

## Verification Results

- All 24 executable tests passed, including formatter validation and the
  synthetic dataframe/plot flow.
- Nine isolated hostile mutations were rejected: missing source, station
  normalization, UTC conversion, timezone validation, inclusive end year,
  notebook timestamp, title, x label, and y label.
- Repository and external-directory `make check` gates each passed all 24
  executable tests and 19 static contracts.
- The internal package index did not expose the lock-pinned `ipykernel==7.3.0`,
  so a fresh local hash-lock install could not complete. The checked-in locks
  were unchanged; exact hosted matrix installation remains required.
- No live NOAA request was made and the notebook remains output-free.
