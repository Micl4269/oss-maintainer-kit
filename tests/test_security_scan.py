from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from oss_maintainer_kit.security_scan import scan_paths


class SecurityScanTests(unittest.TestCase):
    def test_flags_high_signal_secret_without_echoing_value(self) -> None:
        secret = "sk-" + ("a" * 32)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = repo / "notes.txt"
            path.write_text(f"OPENAI_API_KEY={secret}\n", encoding="utf-8")

            findings = scan_paths([path], repo)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule, "openai-key")
        self.assertNotIn(secret, findings[0].message)

    def test_flags_tracked_env_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = repo / ".env.local"
            path.write_text("DEBUG=true\n", encoding="utf-8")

            findings = scan_paths([path], repo)

        self.assertEqual(findings[0].rule, "tracked-env-file")

    def test_allows_documented_token_environment_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            path = repo / "README.md"
            path.write_text("Set GITHUB_TOKEN for higher API rate limits.\n", encoding="utf-8")

            findings = scan_paths([path], repo)

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
