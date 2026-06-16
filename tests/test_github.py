from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from oss_maintainer_kit.github import GitHubSignalsError, fetch_github_signals, find_contributor_leads


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

    def test_recent_commit_lookup_encodes_default_branch(self) -> None:
        responses = [
            _FakeResponse(
                {
                    "full_name": "owner/repo",
                    "html_url": "https://github.com/owner/repo",
                    "description": None,
                    "stargazers_count": 0,
                    "forks_count": 0,
                    "watchers_count": 0,
                    "open_issues_count": 0,
                    "default_branch": "release/2026",
                    "pushed_at": None,
                }
            ),
            _FakeResponse({}),
            _FakeResponse([]),
        ]

        with patch("urllib.request.urlopen", side_effect=responses) as urlopen:
            fetch_github_signals("owner/repo", token="abc")

        commits_request = urlopen.call_args_list[2].args[0]
        self.assertIn("sha=release%2F2026", commits_request.full_url)

    def test_find_contributor_leads_deduplicates_and_skips_bots(self) -> None:
        responses = [
            _FakeResponse(
                {
                    "items": [
                        {
                            "full_name": "example/tool-one",
                            "html_url": "https://github.com/example/tool-one",
                        },
                        {
                            "full_name": "example/tool-two",
                            "html_url": "https://github.com/example/tool-two",
                        },
                    ]
                }
            ),
            _FakeResponse(
                [
                    {
                        "login": "useful-dev",
                        "type": "User",
                        "html_url": "https://github.com/useful-dev",
                    },
                    {
                        "login": "dependabot[bot]",
                        "type": "Bot",
                        "html_url": "https://github.com/apps/dependabot",
                    },
                ]
            ),
            _FakeResponse(
                [
                    {
                        "login": "useful-dev",
                        "type": "User",
                        "html_url": "https://github.com/useful-dev",
                    },
                    {
                        "login": "owner-to-skip",
                        "type": "User",
                        "html_url": "https://github.com/owner-to-skip",
                    },
                ]
            ),
        ]

        with patch("urllib.request.urlopen", side_effect=responses):
            leads = find_contributor_leads(
                queries=["topic:maintainer-tools language:Python"],
                max_repos=2,
                max_contributors_per_repo=2,
                exclude_users=["owner-to-skip"],
            )

        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0].username, "useful-dev")
        self.assertEqual(
            leads[0].source_repositories,
            ("example/tool-one", "example/tool-two"),
        )
        self.assertIn("topic:maintainer-tools language:Python", leads[0].matched_queries)

    def test_find_contributor_leads_requires_positive_limits(self) -> None:
        with self.assertRaises(GitHubSignalsError):
            find_contributor_leads(queries=["topic:maintainer-tools"], max_repos=0)


if __name__ == "__main__":
    unittest.main()
