"""AnnabanAI contract layer for Sourcery MCP review results.

This module does not call Sourcery or implement OAuth. Connect an MCP-capable
client to https://mcp.sourcery.ai/mcp using Sourcery's documented sign-in flow,
then pass the returned review data through these normalization helpers.

Advisory-only. External effects: 0. Human approval is required for changes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping


class EvidenceClass(str, Enum):
    VERIFIED = "VERIFIED"
    SOURCERY_REPORTED = "SOURCERY_REPORTED"
    SIMULATED = "SIMULATED"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class ReviewRequest:
    repository: str
    pull_request: int
    head_sha: str
    requested_by: str
    mode: str = "ADVISORY_ONLY"
    external_effects: int = 0
    human_approval_required: bool = True

    def validate(self) -> None:
        if not self.repository or "/" not in self.repository:
            raise ValueError("repository must use owner/name form")
        if self.pull_request < 1:
            raise ValueError("pull_request must be positive")
        if not self.head_sha or len(self.head_sha) < 7:
            raise ValueError("head_sha must identify the reviewed revision")
        if not self.requested_by.strip():
            raise ValueError("requested_by is required")
        if self.mode != "ADVISORY_ONLY":
            raise ValueError("only ADVISORY_ONLY mode is supported")
        if self.external_effects != 0:
            raise ValueError("external effects must remain zero")
        if not self.human_approval_required:
            raise ValueError("human approval requirement cannot be disabled")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str | None
    title: str
    severity: str
    message: str
    file_path: str | None
    line: int | None
    evidence_class: EvidenceClass = EvidenceClass.SOURCERY_REPORTED

    def to_dict(self) -> dict[str, Any]:
        if not self.title.strip() or not self.message.strip():
            raise ValueError("finding title and message are required")
        if self.line is not None and self.line < 1:
            raise ValueError("line must be a positive 1-based line number")
        return asdict(self) | {"evidence_class": self.evidence_class.value}


def normalize_finding(raw: Mapping[str, Any]) -> ReviewFinding:
    """Map known fields without inventing absent IDs, paths, or line numbers.

    Callers should explicitly map the fields returned by the specific Sourcery
    MCP tool they invoked. This intentionally avoids guessing unknown schemas.
    """
    severity = str(raw.get("severity") or "UNKNOWN").upper()
    line_value = raw.get("line")
    line = int(line_value) if line_value is not None else None
    return ReviewFinding(
        finding_id=str(raw["id"]) if raw.get("id") is not None else None,
        title=str(raw.get("title") or "Untitled finding"),
        severity=severity,
        message=str(raw.get("message") or raw.get("description") or ""),
        file_path=str(raw["file_path"]) if raw.get("file_path") else None,
        line=line,
        evidence_class=EvidenceClass.SOURCERY_REPORTED,
    )


def build_review_envelope(
    request: ReviewRequest, findings: list[ReviewFinding]
) -> dict[str, Any]:
    """Produce an auditable report; never authorize code edits or merges."""
    request.validate()
    return {
        "schema_version": "1.0",
        "request": request.to_dict(),
        "provider": "Sourcery MCP",
        "provider_connected": False,
        "provider_result_verified": False,
        "findings": [finding.to_dict() for finding in findings],
        "decision": "HUMAN_REVIEW_REQUIRED",
        "code_changes_authorized": False,
        "merge_authorized": False,
        "external_effects": 0,
    }
