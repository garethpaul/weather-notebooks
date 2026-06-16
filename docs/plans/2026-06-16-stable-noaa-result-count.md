# Require Stable NOAA Result Counts Across Pages

## Status: Planned

## Context

`fetch_noaa_data` validates each NOAA result count independently but does not
require the count to remain stable across pages. If result-set metadata changes
during one paginated fetch, the notebook can combine pages from different
logical snapshots or stop against a later count without detecting drift.

## Requirements

- Pin the first reported NOAA result count for a paginated request.
- Reject any later non-null result count that differs before appending that
  page's observations.
- Preserve offset validation, no-progress detection, page limits, redirect
  blocking, exact token handling, and metadata-optional fallback behavior.
- Accept stable result counts and requests whose every page omits metadata.
- Add runtime and mutation-sensitive static coverage plus maintained guidance.
- Keep the notebook delegation contract unchanged.

## Implementation Units

### U1. Stabilize pagination metadata

- **Files:** `weather_notebook.py`
- Track the expected result count and fail before accumulation when later
  metadata disagrees.

### U2. Add deterministic regressions

- **Files:** `weather_notebook_tests.py`,
  `scripts/check_weather_notebook_contracts.py`
- Cover stable counts, increasing/decreasing drift, pre-mutation failure,
  metadata omission, checker registration, and plan evidence.

### U3. Maintain analysis guidance

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Document fail-closed pagination metadata consistency.

## Verification

- Run focused unit/static contracts and repository/external-directory
  non-cleaning `make verify` gates with explicit timeouts.
- Reject mutations that remove count pinning, compare after accumulation,
  accept drift, break metadata omission, unregister coverage, weaken guidance,
  or reopen the plan.
- Audit the exact diff, generated artifacts, conflicts, file modes, and
  credential-like additions before committing.

## Runtime Boundary

No live NOAA token or request is used. Deterministic fake responses verify the
client contract; NOAA service-side consistency remains external.
