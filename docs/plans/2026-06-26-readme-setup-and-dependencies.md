# README Setup And Dependency Requirements

Status: Completed

## Context

The repository already maintained exact direct pins, reviewed hashed Python
3.12 and 3.14 lockfiles, and a hosted install matrix, but the README described
only generic Python 3 and always selected the Python 3.12 lock. It also treated
the NOAA token as a setup requirement even though repository verification is
offline.

## Objectives

- State that reproducible local environments use CPython 3.12 or 3.14.
- Map each supported interpreter to its matching reviewed lockfile.
- Bound the reviewed reproducible environment to Linux x86_64 and list all five
  exact direct dependency requirements.
- Create an isolated virtual environment, install with `--require-hashes`, and
  verify the five scientific imports before running `make check`.
- Explain that `requirements.txt` is direct lock input and must not replace a
  complete lockfile for reviewed installs.
- Keep `uv` optional for normal setup and require it only for `make lock`.
- Separate offline verification from live NOAA requests and token handling.
- Replace stale generated inventory with the repository's real notebook,
  helper, test, dependency, and verification surfaces.

## Verification

- Focused README setup and dependency contract fails before documentation is
  aligned and passes afterward.
- Hostile interpreter, lock mapping, direct-requirements, uv, token, roadmap,
  change-history, plan-status, and test-registration mutations fail closed.
- `python3 scripts/check_weather_notebook_contracts.py`
- `python3 -m unittest weather_notebook_tests`
- `make check` from the checkout and through an absolute Makefile path from an
  external working directory.
- `git diff --check`

## Scope Boundary

- Do not change notebook behavior, request logic, data, dependencies, lockfile
  contents, workflow behavior, or generated analysis outputs.
- Do not require a NOAA token or network access for repository verification.
- Do not claim reproducibility for a Python version without a reviewed lockfile
  and hosted install proof.

## Work Completed

- Added exact Python 3.12 and 3.14 virtual-environment paths with matching
  Linux x86_64 hashed lockfiles, direct pins, and import verification.
- Distinguished direct lock input, complete lockfiles, normal setup, lock
  regeneration, offline checks, and live token-bearing notebook execution.
- Registered executable documentation and completed-plan contracts.

## Results

- Python 3.12.13 with `requirements-py312.lock` and Python 3.14.6 with
  `requirements-py314.lock` both installed with `--require-hashes` and imported
  Jupyter, Matplotlib, NumPy, pandas, and Requests.
- Each environment passed checkout-local and external-directory `make check`,
  including 27 offline tests, 21 static contracts, and 40 Make authority cases.
- Fourteen hostile setup, platform, lock, pin, token, roadmap, history, plan,
  and registration mutations failed closed.
