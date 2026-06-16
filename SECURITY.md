# Security Policy

Please do not open public issues for vulnerabilities, suspected leaked
credentials, or security-sensitive reproduction details.

Use GitHub private vulnerability reporting when available. If that is not
available, report security concerns by emailing the maintainer listed on the
GitHub profile for `Micl4269`.

Include:

- Affected version or commit.
- Steps to reproduce.
- Expected impact.
- Any safe proof of concept.

Before opening a pull request, run:

```bash
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```
