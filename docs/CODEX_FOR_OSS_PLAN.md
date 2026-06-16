# Codex for OSS Plan

This document is the maintainer evidence plan for applying to OpenAI Codex for
OSS once the repository has enough public usage signals.

## Maintainer Role

The repository owner is the primary maintainer. Responsibilities include:

- Reviewing issues and pull requests.
- Cutting releases.
- Maintaining CI and tests.
- Handling security reports.
- Keeping contributor documentation current.

## Why This Repository Should Qualify

OSS Maintainer Kit helps open-source maintainers reduce maintenance load. It
turns repo hygiene, contributor readiness, issue triage, and Codex-friendly
workflow planning into repeatable reports that can run locally or in GitHub
Actions.

The repository should not be submitted until it has public evidence such as:

- Public releases.
- Stars, forks, downloads, or external usage.
- Issues and PRs from real users.
- Active maintenance history.
- Examples of the tool being used on public repos.

## API Credit Use

If selected, API credits would be used for maintainer workflows:

- Summarize and classify new issues.
- Draft maintainer review checklists for PRs.
- Generate release-note drafts from merged PRs.
- Detect under-specified issues before maintainers spend review time.
- Produce security-review prompts for code changes in owned repositories.

The tool should never scan repositories without permission. Codex Security or
AI review workflows must be limited to repositories the maintainer owns,
maintains, or is authorized to administer.

## Evidence Checklist Before Applying

- [x] Public GitHub repository exists under the maintainer account.
- [ ] Maintainer profile is public.
- [x] Repository has at least one tagged release.
- [x] README includes install, usage, examples, and maintainer status.
- [x] CI passes on main.
- [x] Issues and PR templates exist.
- [x] SECURITY.md documents private vulnerability reporting.
- [x] At least 3 public maintenance events exist: releases, closed issues,
      reviewed PRs, or documented user feedback.
- [ ] Usage signal exists: stars, forks, installs, users, or dependent repos.
- [ ] Application answers fit within the 500-character fields.

## Current Public Evidence

- Public repository: `Micl4269/oss-maintainer-kit`.
- Release history: `v0.1.0`, with `v0.2.0` planned after the security release.
- Maintenance activity: issues, merged PRs, CI, release notes, and dashboard issue.
- Contributor signal: an external contributor requested assignment on issue #1.
- Security posture: private reporting policy, CI secret-scan gate, CODEOWNERS,
  Dependabot for GitHub Actions, and documented maintainer security checks.

## Remaining Qualification Gaps

- Real adoption evidence is still the biggest gap. Avoid fake stars or alternate
  account activity; it weakens the application.
- Land at least one genuine outside contribution if possible.
- Dogfood the tool on other public repos and link to the generated reports or
  issues when the maintainers allow it.
- Keep a small public backlog of contributor-friendly issues with clear
  acceptance criteria.

## Draft Application Answers

### Role

Primary maintainer. I own releases, issue triage, PR review, security handling,
CI, documentation, and roadmap decisions for the repository.

### Why this repository qualifies

OSS Maintainer Kit helps maintainers audit repo readiness, triage issues, and
prepare Codex-assisted review/release workflows. It is public, actively
maintained, has CI/releases/docs, and is used to reduce maintenance load across
open-source repositories.

### API credit use

Use API credits for issue triage, PR review checklists, release-note drafts,
security-review prompts, and maintainer automation for repositories I own or am
authorized to maintain.
