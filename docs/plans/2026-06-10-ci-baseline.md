# Weather Notebooks CI Baseline

## Status: Completed

## Context

`weather-notebooks` has static notebook reproducibility, token, NOAA response,
and value-shape contracts behind `make check`. The repository needs that
offline baseline to run in GitHub Actions before review.

## Objectives

- Run the existing `make check` wrapper on Python 3.12 and 3.14.
- Keep the hosted job offline and independent of NOAA credentials.
- Make the exact workflow part of the notebook contract baseline.
- Keep workflow permissions read-only and action references immutable.

## Work Completed

- Added `.github/workflows/check.yml` to run on every push, pull request, and
  manual dispatch with bounded concurrency.
- Set up Python 3.12 and 3.14 on Ubuntu 24.04 using immutable action pins,
  read-only permissions, and credential-free checkout.
- Installed and imported the exactly pinned scientific stack before running the
  offline contract gate.
- Extended `scripts/check_weather_notebook_contracts.py` to require the exact CI
  workflow, completed plans, dependency pins, and root-safe Makefile contract.
- Verified `make check` from an external working directory by invoking the
  repository Makefile directly.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check_weather_notebook_contracts.py`
- `make -f /path/to/weather-notebooks/Makefile check` from another directory
- Hostile workflow mutations must fail the contract checker
- `git diff --check`

## Follow-Up Candidates

- Add notebook execution smoke tests only after a synthetic paginated NOAA
  fixture is documented.
