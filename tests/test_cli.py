from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_audit_json_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "README.md").write_text("hello", encoding="utf-8")
            output = Path(tmp) / "report.json"

            result = self._run_cli(
                "audit",
                "--repo",
                str(repo),
                "--format",
                "json",
                "--output",
                str(output),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(data["profile"], "codex-oss")
            self.assertIn("score", data)
            self.assertIsNone(data["github_signals"])

    def test_fail_under_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()

            result = self._run_cli("audit", "--repo", str(repo), "--fail-under", "90")

            self.assertEqual(result.returncode, 2)

    def test_triage_json_output(self) -> None:
        result = self._run_cli(
            "triage",
            "--title",
            "Docs typo in README",
            "--body",
            "The documentation has a typo.",
            "--format",
            "json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("documentation", data["suggested_labels"])

    def _run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        src = Path(__file__).resolve().parents[1] / "src"
        env["PYTHONPATH"] = str(src)
        return subprocess.run(
            [sys.executable, "-m", "oss_maintainer_kit", *args],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )


if __name__ == "__main__":
    unittest.main()
