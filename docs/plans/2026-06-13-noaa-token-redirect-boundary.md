---
title: "fix: Keep NOAA tokens on the configured API origin"
type: fix
date: 2026-06-13
---

# NOAA Token Redirect Boundary

## Status: Completed

## Context

The NOAA client sends its API token in the provider-specific `token` request
header. Requests 2.34.2 enables redirects for GET requests by default, while
its redirect authentication rebuild specifically strips the conventional
`Authorization` header. Automatically following a redirect can therefore send
the NOAA token to a different origin.

Primary references:

- Requests 2.34.2 Developer Interface documents `allow_redirects=True` as the
  default request behavior.
- Requests 2.34.2 `SessionRedirectMixin.rebuild_auth` removes
  `Authorization` on qualifying redirects and does not define equivalent
  handling for the NOAA-specific `token` header.

## Requirements

- R1. Disable redirects on every token-bearing NOAA request.
- R2. Treat redirect responses as HTTP failures before parsing a payload or
  issuing another request.
- R3. Preserve request parameters, pagination, timeout, input validation, and
  the public helper signature.
- R4. Add executable fake-response coverage and mutation-sensitive static
  contracts for the no-redirect option and fail-before-JSON ordering.
- R5. Document the credential-origin boundary and verification evidence.

## Implementation

1. Pass `allow_redirects=False` to the injected request function.
2. Keep `raise_for_status()` before `response.json()` so 3xx responses fail
   without payload processing.
3. Extend runtime fakes, offline contracts, maintenance documentation, and
   hostile mutations without adding dependencies or making a live NOAA call.

## Verification

- Four focused runtime tests passed for redirect disabling, normalized request
  options, HTTP failure propagation, and fail-before-JSON ordering.
- All 17 executable helper tests passed.
- Four hostile mutations covering option removal, redirect re-enablement,
  reversed status/JSON ordering, and missing runtime coverage were rejected.
- Final local and external-working-directory `make check` runs passed under
  explicit three-minute timeouts with 17 executable tests and 16 offline
  contracts.
- Notebook JSON/output state, Python syntax, workflow YAML, lockfile integrity,
  intended paths, artifacts, conflict markers, whitespace, and changed-line
  credential patterns are included in the final audit.
- No live NOAA token or network request was used.

## Scope Boundaries

- Do not add redirect allowlists, retries, session wrappers, new dependencies,
  notebook outputs, or provider API changes.
- Do not merge or close any pull request without explicit owner authorization.
