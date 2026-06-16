# OSS Maintainer Kit

OSS Maintainer Kit helps maintainers audit whether a repository is ready for
outside contributors, public maintenance, and Codex-assisted maintainer
workflows.

It is built for maintainers who need a simple answer:

> What is missing before this repo looks credible, safe, and maintainable?

## Features

- Repository readiness audit with a 0-100 score.
- Markdown or JSON reports.
- Optional public GitHub usage signals: stars, forks, open issues, latest release, and recent activity.
- GitHub Action wrapper for scheduled audits.
- Scheduled maintainer dashboard workflow that updates a stable GitHub issue.
- Built-in tracked-file secret scan for high-signal credential leaks.
- Public contributor lead discovery for manual, non-spam outreach.
- Local Semgrep rules for dangerous Python execution patterns.
- Issue triage brief generator for labels, missing information, and next steps.
- Codex for OSS planning guidance for maintainers preparing an application.
- No runtime dependencies.

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

Include public GitHub usage signals:

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit \
  --repo . \
  --github-repo Micl4269/oss-maintainer-kit \
  --output maintainer-readiness-report.md
```

For higher GitHub API rate limits, set `GITHUB_TOKEN` or pass a different token
environment variable:

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit \
  --repo . \
  --github-repo Micl4269/oss-maintainer-kit \
  --github-token-env MY_GITHUB_TOKEN
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

Run the security hygiene scan:

```bash
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```

If Semgrep is installed, run the optional static-analysis rules:

```bash
semgrep scan --config .semgrep.yml --error .
```

Find public GitHub profile leads from contributors to related repositories:

```bash
PYTHONPATH=src python -m oss_maintainer_kit contributor-leads \
  --query "maintainer tools language:Python stars:>10 pushed:>2025-01-01" \
  --query "repository health language:Python stars:>10 pushed:>2025-01-01" \
  --exclude-user Micl4269 \
  --output contributor-leads.csv
```

This command does not scrape private contact information or send messages. It
returns public GitHub profile URLs, the source repositories where each person
was found, and the search query that made the lead relevant. Review every lead
manually before reaching out.

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
      - uses: Micl4269/oss-maintainer-kit@v0.3.0
        with:
          repo-path: "."
          output: "maintainer-readiness-report.md"
          fail-under: "80"
          github-repo: "Micl4269/oss-maintainer-kit"
```

## Maintainer Dashboard

Use [examples/maintainer-dashboard-workflow.yml](examples/maintainer-dashboard-workflow.yml)
to create or update one stable issue titled `Maintainer dashboard` on a weekly
schedule.

The workflow needs:

```yaml
permissions:
  contents: read
  issues: write
```

It does not use AI or any external paid API. It runs the audit, builds a markdown
issue body, then uses the GitHub CLI and the repository `GITHUB_TOKEN` to create
or update the dashboard issue.

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
- Optional public GitHub usage signals
- Optional scheduled maintainer dashboard issue
- Optional public contributor lead discovery

## Codex for OSS Fit

This repository is designed to become a credible open-source project for
maintainer automation. The intended Codex usage is documented in
[docs/CODEX_FOR_OSS_PLAN.md](docs/CODEX_FOR_OSS_PLAN.md).

## Development

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m oss_maintainer_kit audit --repo .
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```

Optional maintainer security check:

```bash
semgrep scan --config .semgrep.yml --error .
```

## License

MIT
