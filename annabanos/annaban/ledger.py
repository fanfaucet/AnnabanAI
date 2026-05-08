"""JSONL governance ledger for auditability."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class GovernanceLedger:
    """Append-only JSONL log for governance decisions and model IO."""

    def __init__(self, ledger_path: str = "logs/governance_ledger.jsonl") -> None:
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        prompt: str,
        response: str,
        risk_flagged: bool,
        requires_approval: bool,
    ) -> Dict[str, Any]:
        """Append a single event to the JSONL ledger and return the event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "response": response,
            "risk_flagged": risk_flagged,
            "requires_approval": requires_approval,
        }
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event
