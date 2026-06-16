from __future__ import annotations

import json
import urllib.error
import urllib.request

from .models import GitHubSignals


class GitHubSignalsError(RuntimeError):
    """Raised when public GitHub repository signals cannot be fetched."""


def fetch_github_signals(repo: str, token: str | None = None) -> GitHubSignals:
    owner, name = _parse_repo(repo)
    repo_data = _github_json(f"https://api.github.com/repos/{owner}/{name}", token)
    release_data = _github_json(
        f"https://api.github.com/repos/{owner}/{name}/releases/latest",
        token,
        allow_not_found=True,
    )

    latest_release = None
    latest_release_url = None
    if release_data is not None:
        latest_release = str(release_data.get("tag_name") or release_data.get("name") or "")
        latest_release_url = release_data.get("html_url")

    default_branch = str(repo_data.get("default_branch") or "main")
    commits_data = _github_json(
        f"https://api.github.com/repos/{owner}/{name}/commits?per_page=30&sha={default_branch}",
        token,
        allow_not_found=True,
    )
    recent_commits_count = len(commits_data) if isinstance(commits_data, list) else 0

    return GitHubSignals(
        full_name=str(repo_data["full_name"]),
        url=str(repo_data["html_url"]),
        description=repo_data.get("description"),
        stars=int(repo_data.get("stargazers_count") or 0),
        forks=int(repo_data.get("forks_count") or 0),
        watchers=int(repo_data.get("watchers_count") or 0),
        open_issues=int(repo_data.get("open_issues_count") or 0),
        default_branch=default_branch,
        latest_release=latest_release or None,
        latest_release_url=latest_release_url,
        pushed_at=repo_data.get("pushed_at"),
        recent_commits_count=recent_commits_count,
    )


def _parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise GitHubSignalsError("GitHub repo must use owner/name format.")
    return parts[0], parts[1]


def _github_json(url: str, token: str | None, allow_not_found: bool = False) -> dict[str, object] | None:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "oss-maintainer-kit",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if allow_not_found and exc.code == 404:
            return None
        raise GitHubSignalsError(f"GitHub API returned HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        raise GitHubSignalsError(f"Could not reach GitHub API: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise GitHubSignalsError("GitHub API returned invalid JSON.") from exc
