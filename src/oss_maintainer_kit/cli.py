from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .audit import audit_repository, build_triage_brief
from .report import (
    render_audit_json,
    render_audit_markdown,
    render_triage_json,
    render_triage_markdown,
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit":
        return _run_audit(args)
    if args.command == "triage":
        return _run_triage(args)

    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-maintainer-kit",
        description="Audit OSS repositories and generate maintainer triage briefs.",
    )
    subparsers = parser.add_subparsers(dest="command")

    audit = subparsers.add_parser("audit", help="Audit a repository for maintainer readiness.")
    audit.add_argument("--repo", default=".", help="Repository path to audit.")
    audit.add_argument("--profile", default="codex-oss", help="Audit profile name.")
    audit.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report output format.",
    )
    audit.add_argument("--output", help="Write report to this path instead of stdout.")
    audit.add_argument(
        "--fail-under",
        type=int,
        default=None,
        help="Exit with code 2 when the score is below this threshold.",
    )

    triage = subparsers.add_parser("triage", help="Generate a maintainer triage brief.")
    triage.add_argument("--title", required=True, help="Issue or PR title.")
    triage.add_argument("--body", default="", help="Issue or PR body text.")
    triage.add_argument("--body-file", help="Read body text from a file.")
    triage.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Brief output format.",
    )
    triage.add_argument("--output", help="Write brief to this path instead of stdout.")

    return parser


def _run_audit(args: argparse.Namespace) -> int:
    report = audit_repository(Path(args.repo), profile=args.profile)
    rendered = render_audit_json(report) if args.format == "json" else render_audit_markdown(report)
    _write_output(rendered, args.output)

    if args.fail_under is not None and report.score < args.fail_under:
        return 2
    return 0


def _run_triage(args: argparse.Namespace) -> int:
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    brief = build_triage_brief(args.title, body)
    rendered = render_triage_json(brief) if args.format == "json" else render_triage_markdown(brief)
    _write_output(rendered, args.output)
    return 0


def _write_output(text: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return
    sys.stdout.write(text)


if __name__ == "__main__":
    raise SystemExit(main())

