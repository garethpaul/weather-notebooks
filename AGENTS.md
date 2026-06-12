# AGENTS.md

## Repository purpose

`garethpaul/weather-notebooks` is a data science notebook project. Weather Notebooks

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `requirements.txt` - Python runtime dependencies
- `weather_notebook.py` - importable NOAA request and conversion helpers
- `weather_notebook_tests.py` - dependency-free helper behavior tests

## Development commands

- Install dependencies: `python3 -m pip install --require-hashes -r requirements-py312.lock`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: no dominant source language detected.
- Prefer dependency-free tests or stdlib checks when legacy packages are unavailable.

## Testing guidance

- `weather_notebook_tests.py` covers pagination, payload validation, HTTP
  failures, safety bounds, and unit conversion behavior.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- `NOAA_TOKEN` is required to fetch NOAA Climate Data Online data. Keep it in your local environment and out of git; blank or whitespace-only values are rejected before requests are made.
- Do not commit NOAA API tokens, private datasets, or refreshed outputs without source dates.
- The scan did not identify production authentication, payment, or secret-management code. Treat future additions in those areas as security-sensitive.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-weather-notebook-reproducibility.md` for the current notebook reproducibility baseline.
- Notebook outputs can be large or noisy; clear unnecessary execution output before committing notebooks.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
