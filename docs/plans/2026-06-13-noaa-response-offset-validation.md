# NOAA Response Offset Validation

Status: In Progress

## Problem

The fetch helper sends record-based offsets but trusts every returned page as
the requested page. NOAA collection metadata includes `resultset.offset`, so a
stale, repeated, or misrouted response can be detected before its records are
accumulated.

## Primary Source

NOAA Climate Data Online Web Services API v2 documents `offset` as the record
where a page begins and shows collection responses with
`metadata.resultset.offset`:
https://www.ncdc.noaa.gov/cdo-web/webservices/v2

## Plan

1. Parse and validate optional NOAA resultset offsets alongside result counts.
2. Require a returned offset to equal the offset requested for that page.
3. Reject boolean, non-integer, non-positive, and mismatched response offsets
   before accumulating page results.
4. Preserve metadata-free pagination and result-count behavior.
5. Add focused runtime and dependency-free source contracts plus mutation
   coverage.

## Verification

- Run focused response-offset unit tests.
- Run the full `make check` gate locally and from an external working
  directory.
- Reject hostile mutations for ignored offsets, malformed offset acceptance,
  late validation, compatibility regressions, and stale plan status.
- Run Python compilation, `git diff --check`, artifact review, and focused
  secret review.
- Do not perform a live NOAA request or use a real token.
