# Protect the Make Repository Root from Overrides

## Status: Completed

## Context

The Makefile-derived root keeps absolute `make -f` invocations portable, but
an ordinary assignment can be replaced from the command line and redirect
tests, lock generation, contracts, or cleanup away from the reviewed checkout.

## Requirements

- Protect the Makefile-derived root with GNU Make's `override` directive.
- Preserve configurable Python, deterministic lock commands, and external
  absolute-Makefile invocation.
- Require exact protected root and Python lines in the offline checker.
- Pass local, external-directory, and hostile-root full gates.
- Reject root, checker, Python override, cleanup, lock, and plan regressions.
- Preserve NOAA request behavior, notebook state, workflows, and lockfiles.

## Verification Plan

- focused workflow/Makefile contract and Python compilation
- bounded local, external-directory, and hostile-root `make check`
- focused mutations
- notebook JSON/output, workflow YAML, lock digests, artifact, whitespace, and
  changed-line secret audits

## Scope Boundaries

- Do not change NOAA behavior, dependencies, lockfiles, workflows, or notebook
  contents.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Protected the Makefile-derived root while preserving the Python override and
  deterministic lock commands.
- Added exact-line checker contracts and registered this completed plan.

## Verification

- Python compilation and the focused workflow/Makefile contract passed.
- Local, absolute-Makefile external-directory, and hostile-root `make check`
  runs passed under 300-second timeouts with 17 executable tests and 16 offline
  contracts.
- Nine hostile root, checker, Python override, cleanup, lock-command, and
  plan-status mutations were rejected.
- Lockfile SHA-256 digests remained unchanged, the notebook JSON had no saved
  outputs or execution counts, and YAML/artifact/whitespace/secret audits
  passed.
