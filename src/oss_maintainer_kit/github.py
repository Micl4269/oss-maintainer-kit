from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from typing import Any

from .models import ContributorLead, GitHubSignals


class GitHubSignalsError(RuntimeError):
    """Raised when public GitHub repository signals cannot be fetched."""


DEFAULT_CONTRIBUTOR_QUERIES = (
    "maintainer tools language:Python stars:>10 pushed:>2025-01-01",
    "repository health language:Python stars:>10 pushed:>2025-01-01",
    "github api developer tools language:Python stars:>10 pushed:>2025-01-01",
)


def fetch_github_signals(repo: str, token: str | None = None) -> GitHubSignals:
    owner, name = _parse_repo(repo)
    repo_data = _github_json(f"https://api.github.com/repos/{owner}/{name}", token)
    if not isinstance(repo_data, dict):
        raise GitHubSignalsError("GitHub API returned an unexpected repository payload.")
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

    return GitHubSignals(
        full_name=str(repo_data["full_name"]),
        url=str(repo_data["html_url"]),
        description=repo_data.get("description"),
        stars=int(repo_data.get("stargazers_count") or 0),
        forks=int(repo_data.get("forks_count") or 0),
        watchers=int(repo_data.get("watchers_count") or 0),
        open_issues=int(repo_data.get("open_issues_count") or 0),
        default_branch=str(repo_data.get("default_branch") or "main"),
        latest_release=latest_release or None,
        latest_release_url=latest_release_url,
        pushed_at=repo_data.get("pushed_at"),
    )


def find_contributor_leads(
    queries: list[str] | tuple[str, ...] | None = None,
    token: str | None = None,
    max_repos: int = 10,
    max_contributors_per_repo: int = 5,
    exclude_users: list[str] | tuple[str, ...] | None = None,
) -> list[ContributorLead]:
    """Find public GitHub profile leads from contributors to related repositories."""
    if max_repos < 1:
        raise GitHubSignalsError("max_repos must be at least 1.")
    if max_contributors_per_repo < 1:
        raise GitHubSignalsError("max_contributors_per_repo must be at least 1.")

    search_queries = tuple(query.strip() for query in (queries or DEFAULT_CONTRIBUTOR_QUERIES) if query.strip())
    if not search_queries:
        raise GitHubSignalsError("At least one contributor search query is required.")

    excluded = {user.casefold() for user in (exclude_users or ())}
    raw_leads: dict[str, dict[str, set[str] | str]] = {}

    for query in search_queries:
        search_data = _github_json(_search_repositories_url(query, max_repos), token)
        if not isinstance(search_data, dict):
            raise GitHubSignalsError("GitHub search API returned an unexpected payload.")
        items = search_data.get("items", [])
        if not isinstance(items, list):
            raise GitHubSignalsError("GitHub search API returned an invalid items list.")

        for item in items:
            if not isinstance(item, dict):
                continue
            full_name = str(item.get("full_name") or "")
            html_url = str(item.get("html_url") or "")
            if "/" not in full_name:
                continue

            contributors_data = _github_json(
                _contributors_url(full_name, max_contributors_per_repo),
                token,
                allow_not_found=True,
            )
            if contributors_data is None:
                continue
            if not isinstance(contributors_data, list):
                raise GitHubSignalsError(f"GitHub contributors API returned an invalid payload for {full_name}.")

            for contributor in contributors_data:
                if not isinstance(contributor, dict):
                    continue
                username = str(contributor.get("login") or "")
                contributor_type = str(contributor.get("type") or "")
                profile_url = str(contributor.get("html_url") or "")
                if _skip_contributor(username, contributor_type, excluded):
                    continue
                lead = raw_leads.setdefault(
                    username,
                    {
                        "profile_url": profile_url,
                        "source_repositories": set(),
                        "source_repository_urls": set(),
                        "matched_queries": set(),
                    },
                )
                _cast_str_set(lead["source_repositories"]).add(full_name)
                if html_url:
                    _cast_str_set(lead["source_repository_urls"]).add(html_url)
                _cast_str_set(lead["matched_queries"]).add(query)

    leads = [
        ContributorLead(
            username=username,
            profile_url=str(data["profile_url"]),
            source_repositories=tuple(sorted(_cast_str_set(data["source_repositories"]))),
            source_repository_urls=tuple(sorted(_cast_str_set(data["source_repository_urls"]))),
            matched_queries=tuple(sorted(_cast_str_set(data["matched_queries"]))),
            reason=_lead_reason(_cast_str_set(data["source_repositories"]), _cast_str_set(data["matched_queries"])),
        )
        for username, data in raw_leads.items()
    ]
    return sorted(leads, key=lambda lead: lead.username.casefold())


def _parse_repo(repo: str) -> tuple[str, str]:
    parts = repo.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise GitHubSignalsError("GitHub repo must use owner/name format.")
    return parts[0], parts[1]


def _search_repositories_url(query: str, per_page: int) -> str:
    return "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {
            "q": query,
            "sort": "updated",
            "order": "desc",
            "per_page": str(per_page),
        }
    )


def _contributors_url(full_name: str, per_page: int) -> str:
    owner, name = _parse_repo(full_name)
    return f"https://api.github.com/repos/{owner}/{name}/contributors?" + urllib.parse.urlencode(
        {"per_page": str(per_page)}
    )


def _skip_contributor(username: str, contributor_type: str, excluded: set[str]) -> bool:
    if not username:
        return True
    lowered = username.casefold()
    return lowered in excluded or lowered.endswith("[bot]") or contributor_type.casefold() == "bot"


def _cast_str_set(value: set[str] | str) -> set[str]:
    if isinstance(value, set):
        return value
    raise GitHubSignalsError("Internal contributor lead state was malformed.")


def _lead_reason(source_repositories: set[str], matched_queries: set[str]) -> str:
    repo_sample = ", ".join(sorted(source_repositories)[:3])
    query_count = len(matched_queries)
    noun = "query" if query_count == 1 else "queries"
    return f"Contributed to related public repos ({repo_sample}) matching {query_count} search {noun}."


def _github_json(url: str, token: str | None, allow_not_found: bool = False) -> Any:
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
