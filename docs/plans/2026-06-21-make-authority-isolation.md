# Isolate Make, Python, and uv Verification Authority

## Status: Completed

## Context

The Makefile rooted checks, cleanup, and lock generation at its own location,
but callers could still replace the recipe shell, load startup makefiles,
override the Makefile list, select non-executing or error-ignoring modes,
embed Make syntax in executable values, or append single-colon public recipes
after the reviewed file.

## Requirements

- Derive the repository root only from the reviewed Makefile path.
- Freeze literal Python and uv executable values without evaluating Make
  syntax, including paths with spaces and shell metacharacters.
- Fix ordinary public recipes to `/bin/sh`, reject injected startup files and
  replaced Makefile lists, and reject unsafe execution modes.
- Reject later single-colon replacement of every public target while
  preserving documented caller-override boundaries.
- Keep bytecode cleanup confined to the reviewed repository before and after
  the full offline gate.
- Exercise all eight public targets under command-line and environment root
  and shell attacks, including fake offline lock generation.
- Invoke hosted root and external verification through `/usr/bin/make`.

## Scope Boundaries

- Do not change NOAA request behavior, notebook contents, dependency pins,
  lockfile bytes, or scientific output.
- Keep `make lock` outside the default offline verification gate.
- Caller-supplied GNU Make `override` directives and `PATH` selection of the
  default `python3` and `uv` remain explicit trust boundaries.

## Verification

- Repository and external-directory `make check` passed 27 unit tests and 20
  notebook contracts without loading a NOAA token or making a live request.
- The authority harness passed 40 public-target/root/shell cases, six raw
  Make-syntax controls, two Makefile-list rejections, two startup boundaries,
  eight later recipe-replacement rejections, later root/Python/uv and shell
  controls, PATH boundaries, cleanup containment, caller `MAKEFLAGS`, and ten
  unsafe-mode rejections.
- Python and shell syntax, workflow YAML, notebook JSON, lockfile digests,
  `git diff --check`, intended-path, artifact, and changed-line credential
  audits passed.
