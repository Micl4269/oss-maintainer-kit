from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from oss_maintainer_kit.github import GitHubSignalsError, fetch_github_signals


class _FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class GitHubSignalsTests(unittest.TestCase):
    def test_fetch_github_signals_maps_api_response(self) -> None:
        responses = [
            _FakeResponse(
                {
                    "full_name": "Micl4269/oss-maintainer-kit",
                    "html_url": "https://github.com/Micl4269/oss-maintainer-kit",
                    "description": "Audit repos",
                    "stargazers_count": 2,
                    "forks_count": 1,
                    "watchers_count": 2,
                    "open_issues_count": 4,
                    "default_branch": "main",
                    "pushed_at": "2026-06-16T00:00:00Z",
                }
            ),
            _FakeResponse(
                {
                    "tag_name": "v0.1.0",
                    "html_url": "https://github.com/Micl4269/oss-maintainer-kit/releases/tag/v0.1.0",
                }
            ),
            _FakeResponse(
                [{"sha": "abc"}, {"sha": "def"}, {"sha": "ghi"}]
            ),
        ]

        with patch("urllib.request.urlopen", side_effect=responses):
            signals = fetch_github_signals("Micl4269/oss-maintainer-kit", token="abc")

        self.assertEqual(signals.full_name, "Micl4269/oss-maintainer-kit")
        self.assertEqual(signals.stars, 2)
        self.assertEqual(signals.latest_release, "v0.1.0")
        self.assertEqual(signals.recent_commits_count, 3)

    def test_fetch_github_signals_rejects_invalid_repo_format(self) -> None:
        with self.assertRaises(GitHubSignalsError):
            fetch_github_signals("not-a-repo")

    def test_recent_commits_defaults_to_zero_when_no_commits(self) -> None:
        responses = [
            _FakeResponse(
                {
                    "full_name": "owner/empty",
                    "html_url": "https://github.com/owner/empty",
                    "description": None,
                    "stargazers_count": 0,
                    "forks_count": 0,
                    "watchers_count": 0,
                    "open_issues_count": 0,
                    "default_branch": "main",
                    "pushed_at": None,
                }
            ),
            _FakeResponse({}),
            _FakeResponse([]),
        ]

        with patch("urllib.request.urlopen", side_effect=responses):
            signals = fetch_github_signals("owner/empty", token="abc")

        self.assertEqual(signals.recent_commits_count, 0)


if __name__ == "__main__":
    unittest.main()
