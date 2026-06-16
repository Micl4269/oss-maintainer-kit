# Maintainer Playbook

## Weekly Maintenance Loop

1. Run the repository audit.
2. Review failures first, then warnings.
3. Triage new issues with the triage command.
4. Convert accepted issues into small scoped tasks.
5. Cut releases from passing CI only.

```bash
PYTHONPATH=src python -m oss_maintainer_kit audit --repo . --output maintainer-readiness-report.md
PYTHONPATH=src python -m oss_maintainer_kit triage --title "Example issue" --body-file issue.md
```

## Review Standard

A PR is ready to merge when:

- It solves one clear problem.
- Tests cover the changed behavior.
- The report score does not regress.
- Docs are updated when behavior changes.
- Security-sensitive changes have an explicit risk note.

## Release Standard

For each release:

- Update `CHANGELOG.md`.
- Tag the release.
- Verify the GitHub Action still runs.
- Publish a short note describing what changed and why maintainers should care.

