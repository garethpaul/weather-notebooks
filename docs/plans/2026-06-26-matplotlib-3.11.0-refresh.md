# Matplotlib 3.11.0 Refresh

## Status: Completed

## Context

The repository maintains exact scientific direct pins and reviewed hashed Linux
lock graphs for Python 3.12 and 3.14. Matplotlib 3.11.0 became the only newer
direct dependency release and continues to support Python 3.11 or newer.

## Requirements

- Update Matplotlib exactly from 3.10.9 to 3.11.0.
- Regenerate both locks with the canonical `make lock` command and public PyPI.
- Reject unrelated package-version drift in the reviewed lock comparison.
- Preserve offline NOAA tests, headless plotting, notebook content, request
  boundaries, and token handling unchanged.

## Verification Plan

- Compare active package versions before and after lock regeneration.
- Refresh and enforce both full lockfile SHA-256 digests.
- Install each lock with `--require-hashes` under Python 3.12 and 3.14.
- Run scientific imports, `make check`, and the external-directory Make gate on
  both supported runtimes.
- Mutate the Matplotlib direct pin and a lock digest in isolated checkouts and
  require the static contract suite to fail closed.

## Work Completed

- Updated the exact direct Matplotlib requirement to 3.11.0.
- Regenerated both lock graphs with `uv 0.11.23`.
- Verified Matplotlib was the only package version changed in either lock.
- Updated README, roadmap, lock digests, and completed-plan registration.

## Verification

- Canonical lock regeneration resolved 106 packages per supported runtime.
- Each lock comparison contained exactly one version change.
- Fresh Python 3.12 and 3.14 hashed installs passed scientific imports and
  `pip check` with Matplotlib 3.11.0.
- Both runtimes passed checkout-local and external-directory `make check`,
  including 27 offline tests, 21 static contracts, and 40 Make authority cases.
- Direct-pin and lock-digest hostile mutations failed on the intended checker
  assertions, and `git diff --check` passed.
- Hosted Python 3.12 and 3.14 hash-locked gates plus CodeQL passed on PR #15.
- The Codex review helper returned HTTP 401 before analysis; an immutable
  manual review confirmed both lock graphs changed only Matplotlib.
