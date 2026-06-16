# Project Spec

## Goal

Help open-source maintainers quickly see whether a repository is ready for
outside contributors and AI-assisted maintenance workflows.

## Primary Users

- Solo maintainers preparing a repo for public contributors.
- Small OSS teams trying to reduce issue triage and review load.
- Maintainers preparing evidence for programs that support open-source work.

## V0.1 Scope

- Local repository audit.
- Markdown and JSON reports.
- CI-friendly score threshold.
- Issue triage brief generator.
- Composite GitHub Action wrapper.
- Docs for Codex for OSS readiness and maintainer workflow.

## Non-Goals

- No automatic posting to GitHub issues in v0.1.
- No AI API calls in v0.1.
- No private repository scanning without owner authorization.
- No claim that a score qualifies a maintainer for any external program.

## Acceptance Criteria

- The CLI runs with only Python standard-library dependencies.
- A repository can generate a markdown readiness report.
- A repository can fail CI below a configured readiness threshold.
- Triage output identifies likely labels, missing information, and maintainer actions.
- Tests cover scoring behavior and CLI output.
- The repo includes public OSS hygiene files: README, license, contributing guide,
  security policy, code of conduct, issue templates, PR template, CI, changelog.

## Roadmap

### 0.2

- Add optional GitHub API mode for stars, forks, releases, and open issue counts.
- Add a scheduled report workflow that opens or updates a maintainer dashboard issue.
- Add a dependency-free tracked-file secret scan and CI gate.
- Add repository controls for security-sensitive files.

### 0.3

- Add optional AI-assisted triage behind explicit maintainer-owned repo checks.
- Add configurable scoring rules.
- Add SARIF or check-run output for GitHub code scanning style reporting.
- Add more checks for package publish metadata and README examples.
