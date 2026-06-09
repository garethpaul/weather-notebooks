# weather-notebooks

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/weather-notebooks` is a data science notebook project. Weather Notebooks

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: no dominant source language detected.

## Repository Contents

- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: none detected
- Entry points or build surfaces: none detected
- Test-looking files: no obvious test files detected

## Getting Started

### Prerequisites

- Git
- Python 3
- A NOAA Climate Data Online API token available as `NOAA_TOKEN`

### Setup

```bash
git clone https://github.com/garethpaul/weather-notebooks.git
cd weather-notebooks
python -m pip install -r requirements.txt
export NOAA_TOKEN=your-noaa-token
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Run `jupyter notebook Weather.ipynb` after installing dependencies and setting `NOAA_TOKEN`.
- The notebook fetches NOAA CDO observations for station `GHCND:US1CAMR0037` across the configured date range.

## Testing and Verification

- `make verify` runs static notebook reproducibility and token-safety checks.
- `make check` runs `make verify` with bytecode cleanup before and after.
- `python3 scripts/check_weather_notebook_contracts.py` runs just the notebook contracts.
- Completed maintenance plans live under `docs/plans` and are checked by
  `make check`.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- `NOAA_TOKEN` is required to fetch NOAA Climate Data Online data. Keep it in your local environment and out of git.
- Do not commit NOAA API tokens, private datasets, or refreshed outputs without source dates.

## Security and Privacy Notes

- The scan did not identify production authentication, payment, or secret-management code. Treat future additions in those areas as security-sensitive.

## Maintenance Notes

- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-weather-notebook-reproducibility.md` for the
  current notebook reproducibility baseline.
- See `docs/plans/2026-06-08-weather-notebook-date-alignment.md` for the NOAA
  datatype date-alignment contract.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
