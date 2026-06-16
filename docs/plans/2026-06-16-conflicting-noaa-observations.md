# Conflicting NOAA Observation Guard

Status: In Progress

## Context

`record_observation` merges NOAA records by timestamp and datatype before the
notebook builds its dataframe. A second record for the same timestamp and
datatype currently overwrites the first value. When duplicate records
conflict, the resulting analysis depends on response order and can silently
replace a valid measurement with malformed or different data.

## Priorities

1. Protect dataframe integrity by rejecting conflicting duplicate
   observations before row construction.
2. Keep exact duplicate records idempotent so repeated NOAA pages or records do
   not fail otherwise valid analysis.
3. Preserve the notebook helper API, supported datatype set, conversion rules,
   and synthetic dataframe/plot flow.
4. Continue separately with source-provenance and generated-output timestamps;
   those concerns do not replace input consistency checks.

## Implementation Plan

1. Add executable tests that establish first-write behavior, identical-repeat
   idempotence, and fail-closed handling for conflicting values, including a
   valid measurement followed by a malformed value.
2. Update `weather_notebook.py` so an existing date/datatype pair is retained
   only when the incoming value compares equal; otherwise raise a stable
   `ValueError` without mutating accumulated observations.
3. Add a registered static contract for duplicate handling, test presence,
   completed-plan evidence, and notebook-helper parity.
4. Synchronize `CHANGES.md` and `VISION.md` with the enforced data-integrity
   boundary.

## Verification Plan

- Run the focused executable duplicate-observation tests first.
- Run `make check` from the repository and an external working directory.
- Reject hostile mutations that restore overwrite behavior, accept conflicts,
  mutate before validation, deregister the contract, weaken guidance, or leave
  this plan incomplete.
- Audit the exact diff, generated artifacts, whitespace, file modes, and added
  credential-shaped text before committing explicit paths.

## Assumptions

- Exact duplicate values are safe to treat as idempotent; numerically equal
  Python values such as `10` and `10.0` compare equal.
- Conflicting observations should stop analysis instead of choosing a value by
  response order because the repository has no reviewed quality-ranking rule.
- Live NOAA and notebook UI execution remain outside this offline change; the
  existing synthetic analysis flow covers dataframe and headless plotting.

## Verification

Pending implementation and validation.
