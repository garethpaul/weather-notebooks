# Changes

## 2026-06-26 13:48 PDT - P3 - Refresh Matplotlib across reviewed locks

### Summary

Updated the exact Matplotlib pin from 3.10.9 to 3.11.0 across the direct
requirements and both reviewed Linux lock graphs.

### Work completed

- Regenerated the Python 3.12 and 3.14 hash-locked graphs with canonical
  `make lock` using `uv 0.11.23`.
- Confirmed Matplotlib was the only package version changed in either lock.
- Updated the fail-closed direct dependency and complete-lock digest contracts.
- Preserved NOAA request behavior, dataframe construction, plotting helpers,
  notebook content, and live-token boundaries unchanged.

### Threads

- Started: none — the dependency refresh was completed directly.
- Continued: none.
- Stopped: none.

### Files changed

- `requirements.txt`, `requirements-py312.lock`, and
  `requirements-py314.lock` — pin Matplotlib 3.11.0 with reviewed hashes.
- `scripts/check_weather_notebook_contracts.py` — updates exact requirements,
  lock digests, and completed-plan registration.
- `README.md`, `VISION.md`, and
  `docs/plans/2026-06-26-matplotlib-3.11.0-refresh.md` — document scope and
  verification evidence.

### Validation

- Dependency review — Jupyter, NumPy, pandas, and Requests remained current;
  Matplotlib 3.11.0 requires Python 3.11+ and supports both maintained runtimes.
- Lock comparison — exactly one version changed in each graph:
  `matplotlib==3.10.9` to `matplotlib==3.11.0`.
- The unsupported host Python 3.11 environment has an incomplete global
  Requests installation and is not used as authoritative evidence.
- Fresh Python 3.12 and 3.14 hashed installs passed scientific imports and
  `pip check` with Matplotlib 3.11.0.
- Both runtimes passed checkout-local and external-directory `make check`:
  27 offline tests, 21 static contracts, and all 40 Make authority cases.
- Isolated mutations restoring Matplotlib 3.10.9 and changing a lockfile digest
  failed on the intended direct-pin and reviewed-digest assertions.
- `git diff --check` passed; exact-head review and hosted verification remain
  the final pre-merge actions.
- Hosted Python 3.12 and 3.14 hash-locked gates plus CodeQL Actions and Python
  analysis passed on PR #15.
- `$codex-review` was invoked against `origin/master` but OpenAI authentication
  returned HTTP 401 before analysis; an immutable manual review confirmed the
  PR head and local head matched and both lock graphs changed only Matplotlib.

### Bugs / findings

- P3: the scientific direct pins lagged the current Matplotlib feature release
  while every other direct dependency remained current.

### Blockers

- None; supported-runtime disposable environments are available.
- The Codex review helper cannot authenticate to the OpenAI API in this
  environment; no model finding was produced or silently ignored.

### Next action

- Re-run exact-head gates after this evidence-only amendment and merge only the
  reviewed hosted-green head.

## 2026-06-26

- Priority P2 cycle: completed the only explicit roadmap gap; no delegated
  threads were started because the documentation and contract change was small
  and isolated.
- Documented reproducible virtual-environment setup with the matching Python
  3.12 or 3.14 lockfile and an explicit import verification step.
- Clarified that `requirements.txt` is lock-generation input, `uv` is needed
  only for `make lock`, and the NOAA token is required only for live notebook
  requests rather than offline verification.
- Replaced stale generated repository inventory with the actual notebook,
  helper, test, dependency, and verification surfaces and added fail-closed
  documentation contracts.
- Python 3.12.13 and 3.14.6 each passed hash-locked installation, scientific
  imports, 27 offline tests, 21 static contracts, 40 Make authority cases, and
  full checkout-local plus external-directory `make check` gates. Fourteen
  hostile documentation and registration mutations were rejected.
- No blocker remains. The next recommended action is to keep direct pins,
  lockfiles, README guidance, and the hosted matrix synchronized whenever the
  scientific environment changes.

## 2026-06-21

- Isolated Make verification authority from caller-controlled roots, shells,
  startup files, Makefile lists, unsafe modes, executable Make syntax, and
  later single-colon public recipe replacement.
- Documented caller-added double-colon public recipes and startup parse-time Make code as outside the local Make trust boundary.
- Added literal Python/uv, lock-command, cleanup-containment, and external-root
  authority coverage and invoked hosted verification through `/usr/bin/make`.

## 2026-06-20

- Updated both hashed Python lockfiles to `jupyterlab` 4.5.9 to remediate
  GHSA-vmhf-c436-hxj4 while preserving the existing direct dependency set.
- Added a fail-closed contract for the reviewed transitive security pin and
  refreshed both lockfile integrity digests.

## 2026-06-18

- Explicitly rejected NOAA 3xx responses before parsing JSON; Requests does
  not treat redirects as errors in `raise_for_status()`.
- Treated JSON boolean observation values as malformed instead of converting
  them to numeric weather measurements.
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
