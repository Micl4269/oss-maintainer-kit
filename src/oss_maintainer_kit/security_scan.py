from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SecurityFinding:
    path: str
    line: int
    rule: str
    message: str


SECRET_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "aws-access-key",
        "AWS access key pattern found.",
        re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    (
        "github-token",
        "GitHub token pattern found.",
        re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})\b"),
    ),
    (
        "openai-key",
        "OpenAI API key pattern found.",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "slack-token",
        "Slack token pattern found.",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ),
    (
        "stripe-live-key",
        "Stripe live secret key pattern found.",
        re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "google-api-key",
        "Google API key pattern found.",
        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    (
        "private-key-block",
        "Private key block found.",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ),
)

ENV_ALLOWLIST = {".env.example", ".env.sample", ".env.template"}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".jks", ".keystore"}
SENSITIVE_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}


def scan_repository(repo: Path) -> list[SecurityFinding]:
    repo = repo.resolve()
    return scan_paths(_tracked_files(repo), repo)


def scan_paths(paths: Iterable[Path], repo: Path) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    for path in paths:
        findings.extend(_scan_path(path, repo))
    return findings


def _tracked_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return [repo / name for name in names]


def _scan_path(path: Path, repo: Path) -> list[SecurityFinding]:
    rel = path.relative_to(repo).as_posix()
    findings = _sensitive_filename_findings(path, rel)

    try:
        raw = path.read_bytes()
    except OSError as exc:
        findings.append(SecurityFinding(rel, 0, "read-error", f"Could not read tracked file: {exc}."))
        return findings

    if _looks_binary(raw):
        return findings

    text = raw.decode("utf-8", errors="replace")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule, message, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(SecurityFinding(rel, line_number, rule, message))
    return findings


def _sensitive_filename_findings(path: Path, rel: str) -> list[SecurityFinding]:
    name = path.name
    suffix = path.suffix.lower()
    findings: list[SecurityFinding] = []

    if name.startswith(".env") and name not in ENV_ALLOWLIST:
        findings.append(SecurityFinding(rel, 0, "tracked-env-file", "Tracked environment file found."))

    if suffix in SENSITIVE_SUFFIXES:
        findings.append(SecurityFinding(rel, 0, "sensitive-key-file", "Tracked key or certificate container found."))

    if suffix == ".key" and not name.endswith(".pub"):
        findings.append(SecurityFinding(rel, 0, "sensitive-key-file", "Tracked private key file found."))

    if name in SENSITIVE_NAMES:
        findings.append(SecurityFinding(rel, 0, "ssh-private-key", "Tracked SSH private key filename found."))

    return findings


def _looks_binary(raw: bytes) -> bool:
    return b"\0" in raw


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan tracked repository files for high-signal secret leaks.")
    parser.add_argument("--repo", default=".", help="Repository path to scan.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args(argv)

    findings = scan_repository(Path(args.repo))
    if args.format == "json":
        print(json.dumps([asdict(finding) for finding in findings], indent=2))
    elif findings:
        print("Security scan failed. Potential secrets or sensitive files were found:")
        for finding in findings:
            location = finding.path if finding.line == 0 else f"{finding.path}:{finding.line}"
            print(f"- {location} [{finding.rule}] {finding.message}")
    else:
        print("Security scan passed. No high-signal secrets or sensitive tracked files found.")

    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
