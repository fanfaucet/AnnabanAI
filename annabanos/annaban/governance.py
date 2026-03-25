"""Governance layer for policy checks, approval gating, and ledgering."""

from __future__ import annotations

import re
from typing import Optional

from .grok_client import GrokClient
from .ledger import GovernanceLedger


class AnnabanGovernance:
    """Policy enforcement wrapper around Grok client calls."""

    HIGH_RISK_KEYWORDS = ("deploy", "execute", "run", "activate")
    APPROVAL_MESSAGE = "⚠️ HUMAN APPROVAL REQUIRED FROM Jacob Kinnaird BEFORE EXECUTION"

    def __init__(self, grok_client: GrokClient, ledger: Optional[GovernanceLedger] = None) -> None:
        self.grok_client = grok_client
        self.ledger = ledger or GovernanceLedger()

    def _is_high_risk(self, prompt: str) -> bool:
        pattern = r"\b(" + "|".join(map(re.escape, self.HIGH_RISK_KEYWORDS)) + r")\b"
        return bool(re.search(pattern, prompt, flags=re.IGNORECASE))

    def process(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        """Run policy checks, optionally gate execution, and log all outcomes."""
        risk_flagged = self._is_high_risk(prompt)

        if risk_flagged:
            response = self.APPROVAL_MESSAGE
            self.ledger.append(
                prompt=prompt,
                response=response,
                risk_flagged=True,
                requires_approval=True,
            )
            return response

        response = self.grok_client.call(prompt=prompt, system_prompt=system_prompt)
        self.ledger.append(
            prompt=prompt,
            response=response,
            risk_flagged=False,
            requires_approval=False,
        )
        return response
