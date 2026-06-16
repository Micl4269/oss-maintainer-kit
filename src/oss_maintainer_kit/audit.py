from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .models import AuditReport, Check, TriageBrief


def audit_repository(repo_path: Path, profile: str = "codex-oss") -> AuditReport:
    repo = repo_path.resolve()
    checks = [
        _file_check(
            repo,
            "readme",
            "README explains purpose and usage",
            "Project basics",
            ["README.md", "README.rst", "README.txt"],
            "Add a README with installation, usage, examples, and maintainer status.",
        ),
        _file_check(
            repo,
            "license",
            "Repository has an open-source license",
            "Project basics",
            ["LICENSE", "LICENSE.md", "COPYING"],
            "Add a recognized OSS license so users know their rights.",
        ),
        _file_check(
            repo,
            "changelog",
            "Changes are tracked for releases",
            "Maintenance",
            ["CHANGELOG.md", "HISTORY.md", "RELEASES.md"],
            "Add a changelog with an Unreleased section and release history.",
        ),
        _file_check(
            repo,
            "contributing",
            "Contributor path is documented",
            "Maintenance",
            ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"],
            "Add CONTRIBUTING.md with setup, tests, PR expectations, and review flow.",
        ),
        _file_check(
            repo,
            "security",
            "Security reporting is private and documented",
            "Security",
            ["SECURITY.md", ".github/SECURITY.md"],
            "Add SECURITY.md with a private vulnerability reporting path.",
        ),
        _file_check(
            repo,
            "code-of-conduct",
            "Community behavior expectations are present",
            "Community",
            ["CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"],
            "Add a concise code of conduct so contributors know the rules.",
        ),
        _directory_check(
            repo,
            "ci",
            "Continuous integration exists",
            "Quality",
            [".github/workflows"],
            "Add GitHub Actions or another CI system that runs tests and lint checks.",
        ),
        _directory_check(
            repo,
            "tests",
            "Automated tests exist",
            "Quality",
            ["tests", "test"],
            "Add tests for the highest-risk behavior before asking for outside contributions.",
        ),
        _directory_check(
            repo,
            "issue-templates",
            "Issue templates guide contributors",
            "Maintenance",
            [".github/ISSUE_TEMPLATE"],
            "Add issue templates for bugs, features, and maintainer tasks.",
        ),
        _file_check(
            repo,
            "pull-request-template",
            "Pull request template sets review expectations",
            "Maintenance",
            [".github/pull_request_template.md", "pull_request_template.md"],
            "Add a PR template with tests, screenshots, and risk notes.",
        ),
        _package_manifest_check(repo),
        _release_signal_check(repo),
        _git_signal_check(repo),
        _codex_plan_check(repo),
    ]

    notes = [
        "Codex for OSS applications are reviewed for maintainer role, repository usage, ecosystem importance, and active maintenance evidence.",
        "This audit cannot prove GitHub stars, downloads, or admin permissions. Capture those manually before applying.",
    ]
    if profile != "codex-oss":
        notes.append(f"Profile '{profile}' uses the same checks in v0.1.0.")
    return AuditReport(repo_path=repo, profile=profile, checks=checks, notes=notes)


def build_triage_brief(title: str, body: str = "") -> TriageBrief:
    text = f"{title}\n{body}".lower()
    labels: list[str] = []

    label_rules = [
        ("security", ["security", "vulnerability", "cve", "secret", "token", "exploit"]),
        ("bug", ["bug", "error", "traceback", "crash", "broken", "regression", "fails"]),
        ("documentation", ["docs", "readme", "documentation", "typo"]),
        ("enhancement", ["feature", "request", "support", "add option"]),
        ("tests", ["test", "coverage", "fixture"]),
        ("dependencies", ["dependency", "upgrade", "package manager", "requirements.txt"]),
    ]
    for label, words in label_rules:
        if any(word in text for word in words):
            labels.append(label)

    if not labels:
        labels.append("needs-triage")

    missing = []
    if not re.search(r"repro|reproduction|steps to reproduce", text):
        missing.append("Steps to reproduce or a minimal example")
    if not re.search(r"expected|should happen", text):
        missing.append("Expected behavior")
    if not re.search(r"actual|what happened|observed", text):
        missing.append("Actual behavior")
    if not re.search(r"version|environment|os|python|node|browser", text):
        missing.append("Environment and version details")

    actions = [
        "Confirm whether the report is actionable from the current information.",
        "Ask for the missing information before assigning implementation work.",
        "If reproducible, add or request a failing test before merging a fix.",
    ]
    if "security" in labels:
        actions.insert(0, "Move sensitive details to the private security reporting path.")
    if "documentation" in labels and len(missing) >= 3:
        actions.append("If this is a simple docs issue, mark it good-first-issue after confirming scope.")

    return TriageBrief(
        title=title,
        suggested_labels=labels,
        missing_information=missing,
        maintainer_actions=actions,
    )


def _file_check(
    repo: Path,
    check_id: str,
    title: str,
    category: str,
    candidates: list[str],
    recommendation: str,
) -> Check:
    matches = [candidate for candidate in candidates if (repo / candidate).is_file()]
    if matches:
        return Check(check_id, title, category, "pass", 10, 10, matches[0], "Keep current.")
    return Check(check_id, title, category, "fail", 0, 10, "not found", recommendation)


def _directory_check(
    repo: Path,
    check_id: str,
    title: str,
    category: str,
    candidates: list[str],
    recommendation: str,
) -> Check:
    matches = [candidate for candidate in candidates if (repo / candidate).is_dir()]
    if matches and any((repo / match).iterdir() for match in matches):
        return Check(check_id, title, category, "pass", 10, 10, matches[0], "Keep current.")
    if matches:
        return Check(check_id, title, category, "warn", 5, 10, matches[0], recommendation)
    return Check(check_id, title, category, "fail", 0, 10, "not found", recommendation)


def _package_manifest_check(repo: Path) -> Check:
    manifests = [
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "Gemfile",
        "composer.json",
    ]
    matches = [manifest for manifest in manifests if (repo / manifest).is_file()]
    if matches:
        return Check(
            "package-manifest",
            "Package or runtime metadata exists",
            "Project basics",
            "pass",
            10,
            10,
            matches[0],
            "Keep current.",
        )
    return Check(
        "package-manifest",
        "Package or runtime metadata exists",
        "Project basics",
        "warn",
        5,
        10,
        "not found",
        "Add a manifest or document why this repo is not packaged.",
    )


def _release_signal_check(repo: Path) -> Check:
    changelog = repo / "CHANGELOG.md"
    if not changelog.is_file():
        return Check(
            "release-signal",
            "Release history is visible",
            "Maintenance",
            "warn",
            4,
            10,
            "CHANGELOG.md missing",
            "Add release notes and tag public releases when shipping stable changes.",
        )
    text = changelog.read_text(encoding="utf-8", errors="ignore")
    has_version = bool(re.search(r"^## \[?\d+\.\d+\.\d+", text, re.MULTILINE))
    if has_version:
        return Check(
            "release-signal",
            "Release history is visible",
            "Maintenance",
            "pass",
            10,
            10,
            "versioned changelog entry found",
            "Keep current.",
        )
    return Check(
        "release-signal",
        "Release history is visible",
        "Maintenance",
        "warn",
        6,
        10,
        "changelog exists without versioned entries",
        "Add versioned release entries once the first release ships.",
    )


def _git_signal_check(repo: Path) -> Check:
    if not (repo / ".git").exists():
        return Check(
            "git-history",
            "Git history is present",
            "Maintenance",
            "warn",
            5,
            10,
            ".git not found",
            "Initialize git before publishing so releases and maintenance activity are visible.",
        )
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        result = None
    if result and result.returncode == 0:
        count = int(result.stdout.strip() or "0")
        if count >= 3:
            return Check(
                "git-history",
                "Git history is present",
                "Maintenance",
                "pass",
                10,
                10,
                f"{count} commits",
                "Keep current.",
            )
        return Check(
            "git-history",
            "Git history is present",
            "Maintenance",
            "warn",
            7,
            10,
            f"{count} commits",
            "Build a visible history of releases, fixes, and reviews.",
        )
    if result and result.returncode != 0:
        stderr = result.stderr.lower()
        if "ambiguous argument" in stderr or "unknown revision" in stderr:
            return Check(
                "git-history",
                "Git history is present",
                "Maintenance",
                "warn",
                6,
                10,
                "git initialized with no commits",
                "Create an initial commit before publishing the repository.",
            )
    return Check(
        "git-history",
        "Git history is present",
        "Maintenance",
        "warn",
        5,
        10,
        "git command unavailable",
        "Verify git history manually before applying to maintainer programs.",
    )


def _codex_plan_check(repo: Path) -> Check:
    candidates = [
        "docs/CODEX_FOR_OSS_PLAN.md",
        "CODEX_FOR_OSS_PLAN.md",
        "docs/MAINTAINER_PLAYBOOK.md",
    ]
    matches = [candidate for candidate in candidates if (repo / candidate).is_file()]
    if matches:
        return Check(
            "codex-plan",
            "Codex usage plan is documented",
            "Codex for OSS",
            "pass",
            10,
            10,
            matches[0],
            "Keep current as workflows mature.",
        )
    return Check(
        "codex-plan",
        "Codex usage plan is documented",
        "Codex for OSS",
        "warn",
        5,
        10,
        "not found",
        "Add a short plan for how API credits would support PR review, triage, and releases.",
    )
