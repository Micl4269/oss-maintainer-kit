from __future__ import annotations

import json
from collections import defaultdict

from .models import AuditReport, Check, TriageBrief


def render_audit_markdown(report: AuditReport) -> str:
    lines = [
        "# OSS Maintainer Readiness Report",
        "",
        f"Repository: `{report.repo_path}`",
        f"Profile: `{report.profile}`",
        f"Score: **{report.score}/100**",
        "",
        "## Summary",
        "",
        f"- Passing checks: {len([check for check in report.checks if check.severity == 'pass'])}",
        f"- Warnings: {len(report.warning_checks)}",
        f"- Failures: {len(report.failing_checks)}",
        "",
    ]

    if report.github_signals is not None:
        signals = report.github_signals
        lines.extend(
            [
                "## Public GitHub Signals",
                "",
                f"- Repository: [{signals.full_name}]({signals.url})",
                f"- Stars: {signals.stars}",
                f"- Forks: {signals.forks}",
                f"- Watchers: {signals.watchers}",
                f"- Open issues: {signals.open_issues}",
                f"- Default branch: `{signals.default_branch}`",
                f"- Latest release: {signals.latest_release or 'none'}",
                f"- Last push: {signals.pushed_at or 'unknown'}",
                f"- Recent commits (last 30): {signals.recent_commits_count}",
                "",
            ]
        )

    by_category: dict[str, list[Check]] = defaultdict(list)
    for check in report.checks:
        by_category[check.category].append(check)

    for category in sorted(by_category):
        lines.extend([f"## {category}", ""])
        for check in by_category[category]:
            icon = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}[check.severity]
            lines.extend(
                [
                    f"### {icon}: {check.title}",
                    "",
                    f"- Check: `{check.id}`",
                    f"- Evidence: {check.evidence}",
                    f"- Score: {check.points}/{check.max_points}",
                    f"- Recommendation: {check.recommendation}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Codex for OSS Application Notes",
            "",
            "Before applying, gather evidence this local audit cannot prove:",
            "",
            "- Your maintainer role and repository permissions.",
            "- Public usage signals such as stars, forks, downloads, dependents, or user reports.",
            "- Active maintenance signals such as releases, reviewed PRs, issue triage, and security handling.",
            "- A concrete API-credit plan for PR review, issue triage, release workflows, or maintainer automation.",
            "",
        ]
    )
    if report.notes:
        lines.extend(["## Notes", ""])
        lines.extend(f"- {note}" for note in report.notes)
        lines.append("")

    return "\n".join(lines)


def render_audit_json(report: AuditReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"


def render_triage_markdown(brief: TriageBrief) -> str:
    lines = [
        "# Maintainer Triage Brief",
        "",
        f"Issue: {brief.title}",
        "",
        "## Suggested Labels",
        "",
    ]
    lines.extend(f"- `{label}`" for label in brief.suggested_labels)
    lines.extend(["", "## Missing Information", ""])
    if brief.missing_information:
        lines.extend(f"- {item}" for item in brief.missing_information)
    else:
        lines.append("- None detected from the issue text.")
    lines.extend(["", "## Maintainer Actions", ""])
    lines.extend(f"- {action}" for action in brief.maintainer_actions)
    lines.append("")
    return "\n".join(lines)


def render_triage_json(brief: TriageBrief) -> str:
    return json.dumps(brief.to_dict(), indent=2, sort_keys=True) + "\n"
