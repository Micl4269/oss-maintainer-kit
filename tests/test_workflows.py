from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_dashboard_workflow_updates_stable_issue(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "maintainer-dashboard.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("issues: write", workflow)
        self.assertIn("uses: ./", workflow)
        self.assertIn("Maintainer dashboard in:title", workflow)
        self.assertIn("gh issue edit", workflow)
        self.assertIn("gh issue create", workflow)

    def test_dashboard_example_uses_published_action(self) -> None:
        example = (ROOT / "examples" / "maintainer-dashboard-workflow.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("uses: Micl4269/oss-maintainer-kit@v0.2.0", example)
        self.assertIn("issues: write", example)
        self.assertIn("github-repo: ${{ github.repository }}", example)


if __name__ == "__main__":
    unittest.main()

