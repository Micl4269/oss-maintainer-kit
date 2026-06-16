# OSS Maintainer Kit

OSS Maintainer Kit helps maintainers audit whether a repository is ready for
outside contributors, public maintenance, and Codex-assisted maintainer
workflows.

It is built for maintainers who need a simple answer:

> What is missing before this repo looks credible, safe, and maintainable?

## Features

- Repository readiness audit with a 0-100 score.
- Markdown or JSON reports.
- GitHub Action wrapper for scheduled audits.
- Issue triage brief generator for labels, missing information, and next steps.
- Codex for OSS planning guidance for maintainers preparing an application.
- No runtime dependencies in v0.1.

## Install

From a checkout:

```bash
git clone https://github.com/Micl4269/oss-maintainer-kit.git
cd oss-maintainer-kit
PYTHONPATH=src python -m oss_maintainer_kit audit --repo .
```

After packaging:

```bash
pip install oss-maintainer-kit
oss-maintainer-kit audit --repo .
```

## Usage

Run an audit:

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit --repo . --output maintainer-readiness-report.md
```

Fail CI if the score is too low:

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit --repo . --fail-under 85
```

Generate a triage brief:

```bash
PYTHONPATH=src python -m oss_maintainer_kit triage \
  --title "Crash when running audit" \
  --body "I get a traceback on Python 3.12"
```

## GitHub Action

```yaml
name: Maintainer readiness

on:
  schedule:
    - cron: "0 9 * * 1"
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: Micl4269/oss-maintainer-kit@v0.1.0
        with:
          repo-path: "."
          output: "maintainer-readiness-report.md"
          fail-under: "80"
```

## What It Checks

- README
- License
- Changelog and release signals
- Contributing guide
- Security policy
- Code of conduct
- CI workflows
- Tests
- Issue templates
- PR template
- Package metadata
- Git history
- Codex for OSS usage plan

## Codex for OSS Fit

This repository is designed to become a credible open-source project for
maintainer automation. The intended Codex usage is documented in
[docs/CODEX_FOR_OSS_PLAN.md](docs/CODEX_FOR_OSS_PLAN.md).

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m oss_maintainer_kit audit --repo .
```

## License

MIT

