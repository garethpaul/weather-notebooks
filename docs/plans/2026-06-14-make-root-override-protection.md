# Protect the Make Repository Root from Overrides

## Status: Planned

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
