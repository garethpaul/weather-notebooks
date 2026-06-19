# NOAA Metadata Pagination

Status: Completed

## Problem

NOAA collection responses declare the total record count in
`metadata.resultset.count`, and offsets identify the first record requested.
The current helper ignores that metadata, advances every offset by 1000, and
stops on any short page. A short intermediate page can therefore skip records,
while an exact full final page can falsely reach the safety limit.

## Plan

1. Read and validate an optional NOAA result-count value.
2. Advance offsets by the number of records actually received.
3. Stop when the accumulated records reach the declared total.
4. Reject malformed metadata and metadata-directed pages that make no
   progress.
5. Preserve the short-page fallback for responses without metadata and the
   20-page safety bound.

## Verification

- Three focused metadata-pagination tests passed.
- The full `make check` gate passed 14 unit tests and 15 offline notebook,
  request, CI, and lockfile contracts.
- The same complete gate passed from an external working directory.
- Six hostile mutations were rejected: fixed-size offsets, missing exact-count
  completion, missing no-progress detection, boolean counts, premature
  short-page termination, and ignored metadata.
- Python compilation and `git diff --check` passed.
