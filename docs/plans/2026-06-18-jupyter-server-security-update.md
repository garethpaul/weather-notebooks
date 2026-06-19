# Update the Jupyter Server Security Pin

## Status: Completed

## Context

The reviewed Python 3.12 and 3.14 lockfiles pinned `jupyter-server` 2.19.0.
Dependency auditing reports CVE-2026-44727 for that release and identifies
2.20.0 as the fixed version.

## Requirements

- Update both hashed lockfiles to `jupyter-server` 2.20.0 from public PyPI.
- Preserve every direct dependency version and all other transitive versions.
- Refresh the reviewed lockfile SHA-256 values.
- Require the fixed transitive version in the repository contract checker.
- Run `make check` from the repository and an external working directory.
- Install the Python 3.12 lock with hash enforcement and rerun dependency
  auditing without a live NOAA token or request.

## Work Completed

- Regenerated both lockfiles with a targeted `jupyter-server` upgrade.
- Updated only the affected version and artifact hashes in each lockfile.
- Refreshed the fail-closed lock digests and added an explicit security-pin
  assertion for both supported Python lockfiles.

## Verification Completed

- The Python 3.12 lock installed successfully with `--require-hashes`.
- Repository and external-directory `make check` passed with 26 unit tests and
  20 static contract groups.
- `pip check` reported no broken requirements.
- `pip-audit` reported no known vulnerabilities after the update.
- The exact diff passed whitespace, artifact, and credential-pattern audits.

## Runtime Boundary

Validation used deterministic fake NOAA responses. No NOAA credential or live
provider request was used.
