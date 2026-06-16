# Security Hardening

This project keeps the default contributor path dependency-free, then layers
optional maintainer security tools on top.

## Required Release Gates

These commands must pass before a release:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m compileall src tests
PYTHONPATH=src python -m oss_maintainer_kit audit --repo . --fail-under 85
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```

The built-in security scan checks tracked files for high-signal credential
patterns and sensitive filenames. It redacts by design: findings report the
rule, path, and line number, not the secret value.

## Optional Maintainer Checks

When installed locally, these external tools provide independent confirmation:

```bash
gitleaks dir . --redact --no-banner
gitleaks detect --source . --redact --no-banner
trufflehog filesystem . --no-update --fail --results=verified,unknown
trufflehog git file://$PWD --no-update --fail --results=verified,unknown
semgrep scan --config .semgrep.yml --error .
```

`pip-audit` is useful once the project adds runtime dependencies. At v0.3.0 the
package has no runtime dependencies, so dependency audit exposure is limited to
the Python and GitHub Actions environments.

## Repository Controls

- `.gitignore` blocks local env files, private keys, build output, logs, and
  local security reports.
- CI runs the built-in security scan on pushes and pull requests.
- CODEOWNERS marks workflows, the composite action, security policy, and the
  scanner as maintainer-reviewed files.
- Dependabot watches GitHub Actions updates weekly.
