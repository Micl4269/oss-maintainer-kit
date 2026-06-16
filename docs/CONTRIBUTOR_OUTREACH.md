# Contributor Outreach

This project should attract contributors through useful issues, public project
directories, and targeted manual outreach. Do not buy stars, trade fake
engagement, scrape private contact data, or send bulk automated messages.

## Outreach Funnel

1. Keep `good first issue` tasks small, scoped, and reproducible.
2. Add clear acceptance criteria and a test command to every beginner issue.
3. List the project in opt-in contributor directories:
   - Good First Issue: `https://goodfirstissue.dev/`
   - Up For Grabs: `https://up-for-grabs.net/`
   - CodeTriage: `https://www.codetriage.com/`
4. Share specific issues in relevant communities, not generic promotion.
5. Use the lead finder for manual research only.

## Lead Finder

The `contributor-leads` command searches public GitHub repositories that match
maintainer-provided queries, then lists public GitHub profiles for contributors
to those repositories.

```bash
PYTHONPATH=src python -m oss_maintainer_kit contributor-leads \
  --query "maintainer tools language:Python stars:>10 pushed:>2025-01-01" \
  --query "repository health language:Python stars:>10 pushed:>2025-01-01" \
  --query "github api developer tools language:Python stars:>10 pushed:>2025-01-01" \
  --exclude-user Micl4269 \
  --max-repos 10 \
  --max-contributors-per-repo 5 \
  --output contributor-leads.csv
```

Use `GITHUB_TOKEN` for higher API limits:

```bash
GITHUB_TOKEN=... PYTHONPATH=src python -m oss_maintainer_kit contributor-leads \
  --exclude-user Micl4269 \
  --format json \
  --output contributor-leads.json
```

The output intentionally includes only:

- GitHub username.
- Public GitHub profile URL.
- Source repositories where the person was found.
- Search queries that explain relevance.
- A short reason for manual review.

It intentionally does not collect private emails, infer personal information, or
message anyone.

Generated lead files are ignored by git through `contributor-leads*.csv`,
`contributor-leads*.json`, and `outreach/` patterns. Keep review lists local
unless everyone listed has explicitly opted in to publication.

## Manual Review Checklist

Before contacting a person, confirm:

- They have recent public OSS activity.
- Their recent work is related to Python, GitHub Actions, developer tooling, or
  maintainer workflows.
- There is a specific issue that fits their public work.
- The message is one-to-one and easy to ignore.
- You are not repeatedly contacting the same person.

## Message Template

```text
Hi <username>, I found your work on <source repo> while looking for contributors
who already know <relevant topic>.

I maintain oss-maintainer-kit, a small Python project for repo readiness audits,
security hygiene checks, and maintainer workflows. This issue looked like a
good fit for your background:

<issue URL>

No pressure if it is not interesting. If you do want to take it, I can keep the
scope tight and review quickly.
```

## Good First Issue Standards

A contributor-friendly issue should include:

- The current behavior.
- The desired behavior.
- Files likely to change.
- A concrete acceptance checklist.
- Test commands.
- Whether docs need updating.

Avoid vague issues like "improve docs" or "add AI". Prefer issues like "Add CSV
output for contributor leads" or "Add a test for GitHub API rate-limit errors".

## Current Recruiting Targets

Good initial issues for this repository:

- Add recent commit activity to GitHub usage signals.
- Add SARIF output for the security scan.
- Add GitHub API rate-limit handling tests.
- Add label sync guidance for `good first issue` and `help wanted`.
- Add directory submission documentation for Good First Issue and Up For Grabs.
