# NOAA Request Input Validation

Status: Completed

## Problem

The notebook trims and validates `NOAA_TOKEN`, but the reusable
`fetch_noaa_data()` helper accepts unchecked years, datatype collections,
tokens, and station identifiers. Direct callers can therefore issue malformed
or unauthenticated requests before discovering configuration errors.

## Plan

1. Validate and normalize request inputs before the first network call.
2. Require a real four-digit integer year, at least one supported datatype,
   and nonblank textual token and station identifiers.
3. Preserve the existing bounded pagination, timeout, metric units, and error
   propagation behavior for valid requests.
4. Add unit and static contract coverage plus hostile mutations.

## Verification

- Two focused request-input unit tests passed.
- `make check` passed 11 unit tests and 14 notebook contracts.
- An external-working-directory Make invocation passed the same gates.
- Token-validation removal, token-normalization removal, and datatype
  normalization removal mutations failed before any real network use.
- Python compilation and `git diff --check` passed.
