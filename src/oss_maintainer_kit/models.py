from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

Severity = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class Check:
    id: str
    title: str
    category: str
    severity: Severity
    points: int
    max_points: int
    evidence: str
    recommendation: str

    @property
    def passed(self) -> bool:
        return self.severity == "pass"


@dataclass(frozen=True)
class AuditReport:
    repo_path: Path
    profile: str
    checks: list[Check]
    notes: list[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        possible = sum(check.max_points for check in self.checks)
        if possible == 0:
            return 0
        earned = sum(check.points for check in self.checks)
        return round((earned / possible) * 100)

    @property
    def failing_checks(self) -> list[Check]:
        return [check for check in self.checks if check.severity == "fail"]

    @property
    def warning_checks(self) -> list[Check]:
        return [check for check in self.checks if check.severity == "warn"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_path": str(self.repo_path),
            "profile": self.profile,
            "score": self.score,
            "checks": [
                {
                    "id": check.id,
                    "title": check.title,
                    "category": check.category,
                    "severity": check.severity,
                    "points": check.points,
                    "max_points": check.max_points,
                    "evidence": check.evidence,
                    "recommendation": check.recommendation,
                }
                for check in self.checks
            ],
            "notes": self.notes,
        }


@dataclass(frozen=True)
class TriageBrief:
    title: str
    suggested_labels: list[str]
    missing_information: list[str]
    maintainer_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "suggested_labels": self.suggested_labels,
            "missing_information": self.missing_information,
            "maintainer_actions": self.maintainer_actions,
        }

