"""
AnnabanAI Companion v2 reference implementation.

Goals:
- Treat every user as a first-class participant.
- Make personalization opt-in and portable.
- Permit model confidence to act as authorization when a policy explicitly
  allows the requested capability and action risk is bounded.
- Keep high-impact or irreversible external effects behind explicit policy gates.
- Record concise decision metadata without storing private chain-of-thought.
"""

from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI


DB_FILE = os.getenv("ANNABAN_DB_FILE", "annabanai_state.db")
LOG_FILE = os.getenv("ANNABAN_LOG_FILE", "interactions.jsonl")
OUTPUT_DIR = Path(os.getenv("ANNABAN_OUTPUT_DIR", "annabanai_outputs"))
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-3")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class CapabilityPolicy:
    name: str
    confidence_threshold: float
    risk: str
    reversible: bool
    model_confidence_authorizes: bool
    human_authorization_required: bool = False


DEFAULT_POLICIES = {
    "conversation": CapabilityPolicy(
        "conversation", 0.60, "low", True, True, False
    ),
    "draft_content": CapabilityPolicy(
        "draft_content", 0.75, "low", True, True, False
    ),
    "local_analysis": CapabilityPolicy(
        "local_analysis", 0.80, "low", True, True, False
    ),
    "persist_user_preference": CapabilityPolicy(
        "persist_user_preference", 0.90, "moderate", True, True, False
    ),
    "external_effect": CapabilityPolicy(
        "external_effect", 0.99, "high", False, False, True
    ),
}


@dataclass
class Decision:
    capability: str
    confidence: float
    authorized: bool
    authorization_source: str
    reason: str
    external_effect: bool = False


class CapabilityAuthorizer:
    """Turns calibrated model confidence into policy-bounded authorization."""

    def __init__(self, policies: Optional[Dict[str, CapabilityPolicy]] = None):
        self.policies = policies or DEFAULT_POLICIES

    def authorize(self, capability: str, confidence: float) -> Decision:
        policy = self.policies.get(capability)
        if policy is None:
            return Decision(
                capability,
                confidence,
                False,
                "policy",
                "Unknown capability; fail closed.",
            )

        confidence = max(0.0, min(1.0, float(confidence)))

        if policy.human_authorization_required:
            return Decision(
                capability,
                confidence,
                False,
                "human_required",
                "Policy requires explicit human authorization.",
                external_effect=True,
            )

        if policy.model_confidence_authorizes and confidence >= policy.confidence_threshold:
            return Decision(
                capability,
                confidence,
                True,
                "model_confidence",
                f"Confidence {confidence:.2f} meets policy threshold "
                f"{policy.confidence_threshold:.2f}.",
                external_effect=False,
            )

        return Decision(
            capability,
            confidence,
            False,
            "policy",
            f"Confidence {confidence:.2f} is below policy threshold "
            f"{policy.confidence_threshold:.2f}.",
        )


class StateStore:
    def __init__(self, path: str = DB_FILE):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        row = self.conn.execute(
            "SELECT preferences FROM user_preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return json.loads(row[0]) if row else {}

    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO user_preferences(user_id, preferences, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                preferences=excluded.preferences,
                updated_at=excluded.updated_at
            """,
            (
                user_id,
                json.dumps(preferences, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.conn.commit()


class AuditLog:
    def __init__(self, path: str = LOG_FILE):
        self.path = path

    def write(self, event: Dict[str, Any]) -> None:
        record = dict(event)
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class AnnabanAICompanion:
    """
    Receptive multi-user companion.

    Users are not ranked by identity. A caller receives the same base
    capability set, with personalization controlled by explicit preferences.
    """

    def __init__(
        self,
        db_file: str = DB_FILE,
        log_file: str = LOG_FILE,
        model: str = XAI_MODEL,
    ):
        self.store = StateStore(db_file)
        self.audit = AuditLog(log_file)
        self.authorizer = CapabilityAuthorizer()
        self.model = model

        if not XAI_API_KEY:
            raise RuntimeError(
                "XAI_API_KEY is not configured. Set it as an environment "
                "variable or Colab secret before calling the model."
            )

        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
        )

    def _system_prompt(self, user_id: str) -> str:
        preferences = self.store.get_preferences(user_id)
        preference_text = json.dumps(preferences, ensure_ascii=False)

        return f"""
You are AnnabanAI Companion, an inclusive AI assistant.

Treat every user as a first-class participant. Do not give privileged
treatment merely because of identity. Use explicit user preferences when
available and otherwise ask or adapt naturally.

Be receptive to different backgrounds, goals, communication styles, and
levels of technical knowledge. Do not assume that a user shares the creator's
values, relationships, ambitions, or circumstances.

Personalization preferences:
{preference_text}

You may make recommendations and decisions within the capability policy.
Model confidence is an authorization signal only where the policy explicitly
permits it. Confidence does not authorize high-impact or irreversible external
effects.

Never expose private chain-of-thought. Provide concise conclusions,
assumptions, evidence, and decision metadata when useful.
"""

    def process(
        self,
        user_id: str,
        user_input: str,
        capability: str = "conversation",
        confidence: float = 0.85,
    ) -> Dict[str, Any]:
        decision = self.authorizer.authorize(capability, confidence)

        self.audit.write(
            {
                "event": "authorization_decision",
                "user_id": user_id,
                "capability": capability,
                "decision": asdict(decision),
            }
        )

        if not decision.authorized:
            return {
                "status": "HOLD",
                "message": decision.reason,
                "decision": asdict(decision),
            }

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt(user_id)},
                {"role": "user", "content": user_input},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        text = response.choices[0].message.content or ""

        self.audit.write(
            {
                "event": "model_response",
                "user_id": user_id,
                "capability": capability,
                "authorization_source": decision.authorization_source,
                "model": response.model,
                "response_id": response.id,
                "usage": response.usage.to_dict() if response.usage else {},
            }
        )

        return {
            "status": "ALLOW",
            "response": text,
            "decision": asdict(decision),
        }


if __name__ == "__main__":
    user_id = os.getenv("ANNABAN_USER_ID", "demo-user")
    companion = AnnabanAICompanion()
    result = companion.process(
        user_id=user_id,
        user_input="Help me plan my next project.",
        capability="conversation",
        confidence=0.92,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
