from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from oss_maintainer_kit.audit import audit_repository, build_triage_brief


class AuditRepositoryTests(unittest.TestCase):
    def test_complete_repo_scores_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self._write_complete_repo(repo)

            report = audit_repository(repo)

            self.assertGreaterEqual(report.score, 90)
            self.assertFalse(report.failing_checks)

    def test_missing_hygiene_files_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("hello", encoding="utf-8")

            report = audit_repository(repo)
            failing_ids = {check.id for check in report.failing_checks}

            self.assertIn("license", failing_ids)
            self.assertIn("security", failing_ids)
            self.assertLess(report.score, 50)

    def test_triage_brief_detects_bug_and_missing_fields(self) -> None:
        brief = build_triage_brief("Crash when running audit", "I get a traceback.")

        self.assertIn("bug", brief.suggested_labels)
        self.assertIn("Expected behavior", brief.missing_information)
        self.assertTrue(brief.maintainer_actions)

    def test_git_repo_without_commits_has_clear_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)

            report = audit_repository(repo)
            git_check = next(check for check in report.checks if check.id == "git-history")

            self.assertEqual(git_check.severity, "warn")
            self.assertEqual(git_check.evidence, "git initialized with no commits")

    def _write_complete_repo(self, repo: Path) -> None:
        for filename in [
            "README.md",
            "LICENSE",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "pyproject.toml",
        ]:
            (repo / filename).write_text("content", encoding="utf-8")
        (repo / "CHANGELOG.md").write_text("## [0.1.0]\n", encoding="utf-8")
        (repo / "docs").mkdir()
        (repo / "docs" / "CODEX_FOR_OSS_PLAN.md").write_text("plan", encoding="utf-8")
        (repo / "tests").mkdir()
        (repo / "tests" / "test_placeholder.py").write_text("def test_ok(): pass\n", encoding="utf-8")
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
        (repo / ".github" / "ISSUE_TEMPLATE").mkdir()
        (repo / ".github" / "ISSUE_TEMPLATE" / "bug.yml").write_text("name: Bug\n", encoding="utf-8")
        (repo / ".github" / "pull_request_template.md").write_text("template", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
