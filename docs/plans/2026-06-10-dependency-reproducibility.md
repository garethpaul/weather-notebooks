# Dependency Reproducibility

Status: Completed

## Context

The notebook declared broad minimum dependency versions, so installations could
resolve materially different scientific stacks without any hosted proof that
the current environment remained importable.

## Objectives

- Pin the current stable direct notebook dependencies exactly.
- Lock complete Python 3.12 and 3.14 Linux dependency graphs with hashes.
- Verify every locked package/version against the OSV advisory database.
- Install and import the stack on supported Python versions in CI.
- Keep NOAA-token-dependent notebook execution out of automated checks.

## Verification

- `python -m pip install --require-hashes -r requirements-py312.lock`
- `python -m pip install --require-hashes -r requirements-py314.lock`
- `python -c "import jupyter, matplotlib, numpy, pandas, requests"`
- `make check`
- Complete active `requirements.txt` lines must equal the five reviewed direct
  pins; comments and extra unpinned entries cannot satisfy the contract.
- Official OSV querybatch for all 106 unique locked package/version pairs
  returned no advisories on 2026-06-12.
- `git diff --check`
