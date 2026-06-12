# Security Policy

## Supported Versions

The supported security scope for `weather-notebooks` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Weather Notebooks

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/weather-notebooks` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a data science notebook project. The active security scope is the code and documentation on the default branch.
- The repository scan did not identify production authentication, payment, or secret-management code. Treat the project as public sample code unless future changes add sensitive surfaces.
- GitHub Actions runs the offline `make check` notebook contract baseline before
  review.
- Direct notebook dependencies are exactly pinned in `requirements.txt` and
  resolved into Python 3.12 and 3.14 hash-locked graphs before hosted offline
  contracts run.
- Hosted CI uses read-only permissions, immutable action pins, and
  credential-free checkout.

## Data and Notebook Notes

For notebooks or data-processing workflows, report unsafe parsing, path traversal, arbitrary code execution, credential exposure, and privacy risks involving included or referenced datasets. Do not submit reports that require exposing private third-party data.

NOAA observation rows should reject malformed or non-text date and datatype
keys before bucketing or conversion. Reports involving malformed API payloads
should include a minimal synthetic response rather than live private data.
NOAA result pagination is capped at 20,000 rows per request group so an
unexpected upstream response cannot cause unbounded API calls or accumulation.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
