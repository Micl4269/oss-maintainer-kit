# Maintainer Playbook

## Weekly Maintenance Loop

1. Run the repository audit.
2. Run the tracked-file security scan.
3. Review failures first, then warnings.
4. Triage new issues with the triage command.
5. Convert accepted issues into small scoped tasks.
6. Review contributor leads manually when the issue backlog is ready.
7. Cut releases from passing CI only.

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit --repo . --output maintainer-readiness-report.md
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
PYTHONPATH=src python -m oss_maintainer_kit triage --title "Example issue" --body-file issue.md
PYTHONPATH=src python -m oss_maintainer_kit contributor-leads --exclude-user Micl4269 --output contributor-leads.csv
```

## Maintainer Dashboard Issue

The dashboard workflow creates or updates one stable GitHub issue titled
`Maintainer dashboard`. It is meant to be public maintainer evidence: a visible,
repeatable loop that shows the repo is watched after release.

Required workflow permissions:

```yaml
permissions:
  contents: read
  issues: write
```

Local dry run:

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit \
  --repo . \
  --github-repo Micl4269/oss-maintainer-kit \
  --output maintainer-readiness-report.md
```

Then inspect `maintainer-readiness-report.md`. The workflow only posts to
GitHub when it runs inside GitHub Actions with `issues: write`.

## Review Standard

A PR is ready to merge when:

- It solves one clear problem.
- Tests cover the changed behavior.
- The report score does not regress.
- The security scan passes.
- Docs are updated when behavior changes.
- Security-sensitive changes have an explicit risk note.

## Contributor Outreach Standard

Use [CONTRIBUTOR_OUTREACH.md](CONTRIBUTOR_OUTREACH.md) when the project needs
new contributors. Outreach should be manual, relevant, and tied to a specific
issue. Do not automate direct messages, scrape private contact information, or
manufacture stars.

## Release Standard

For each release:

- Update `CHANGELOG.md`.
- Run the required release gates in `docs/SECURITY_HARDENING.md`.
- Tag the release.
- Verify the GitHub Action still runs.
- Publish a short note describing what changed and why maintainers should care.
