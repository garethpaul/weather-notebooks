# Dependency Reproducibility

Status: Completed

## Context

The notebook declared broad minimum dependency versions, so installations could
resolve materially different scientific stacks without any hosted proof that
the current environment remained importable.

## Objectives

- Pin the current stable direct notebook dependencies exactly.
- Verify direct pins against the OSV advisory database.
- Install and import the stack on supported Python versions in CI.
- Keep NOAA-token-dependent notebook execution out of automated checks.

## Verification

- `python -m pip install -r requirements.txt`
- `python -c "import jupyter, matplotlib, numpy, pandas, requests"`
- `make check`
- Complete active `requirements.txt` lines must equal the five reviewed direct
  pins; comments and extra unpinned entries cannot satisfy the contract.
- OSV query for all direct dependency pins returned no advisories.
- `git diff --check`
