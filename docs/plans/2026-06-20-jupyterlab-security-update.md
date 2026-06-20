# Update the JupyterLab Security Pin

## Status: Completed

## Context

The reviewed Python 3.12 and 3.14 lockfiles pinned JupyterLab 4.5.8. GitHub
Advisory GHSA-vmhf-c436-hxj4 identifies that release as affected by stored
cross-site scripting through unsanitized extension package metadata and lists
4.5.9 as the first patched version.

## Requirements

- Update both hashed lockfiles to JupyterLab 4.5.9 from public PyPI.
- Preserve every direct dependency version and all unrelated transitive
  versions.
- Refresh the reviewed lockfile SHA-256 values.
- Require the patched transitive version in the repository contract checker.
- Run `make check` from the repository and an external working directory.
- Install the Python 3.12 lock with hash enforcement and rerun dependency
  auditing without a live NOAA token or request.

## Work Completed

- Regenerated both lockfiles with a targeted JupyterLab upgrade.
- Updated only JupyterLab and its artifact hashes in each lockfile.
- Refreshed the fail-closed lock digests and added an explicit security-pin
  assertion for both supported Python lockfiles.

## Verification Completed

- The Python 3.12 lock installed successfully with hash enforcement from
  public PyPI.
- Repository, external-directory, and hostile-root `make check` passed with 27
  unit tests and 20 static contract groups.
- `pip check` reported no broken requirements.
- `pip-audit` reported no known vulnerabilities after the update.
- The exact diff passed whitespace, artifact, and credential-pattern audits.

## Runtime Boundary

Validation used deterministic fake NOAA responses. No NOAA credential or live
provider request was used.
