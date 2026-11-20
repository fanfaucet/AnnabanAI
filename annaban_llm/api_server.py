"""Minimal, human-governed OpenAI-compatible chat API for AnnabanAI.

This is an integration scaffold, not a claim that a model provider is configured.
Set OPENAI_API_KEY and ANNABAN_MODEL to enable generation. No conversation content
is written to application logs or persisted by this module.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from annabanos.annaban.governance import AnnabanGovernance
from annabanos.annaban.ledger import GovernanceLedger
from pydantic import BaseModel, Field, ConfigDict

APP_VERSION = "0.1.0"
MODEL_NAME = os.getenv("ANNABAN_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("ANNABAN_API_KEY")
TEMPO_MODES = {
    "concise": "Be concise and direct. Prioritize the answer and actionable next steps.",
    "balanced": "Be clear and sufficiently detailed. Explain important trade-offs.",
    "reflective": "Proceed carefully. State assumptions, uncertainty, and alternatives.",
}
COVENANT = {
    "status": "design_principles",
    "principles": [
        "AI recommends; humans decide.",
        "Consequential external actions require explicit human authorization.",
        "Separate user-provided claims, generated content, and independently verified evidence.",
        "Respect user agency, consent, and withdrawal.",
        "Do not claim alignment or verification without an explicit evaluation record.",
    ],
    "implementation_status": "Principles are published by this API; runtime compliance is not independently certified.",
}

app = FastAPI(
    title="AnnabanAI Chat API",
    version=APP_VERSION,
    description="Human-governed chat API scaffold. Provider credentials are configured at runtime.",
)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=50_000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[ChatMessage] = Field(min_length=1, max_length=100)
    tempo_mode: Literal["concise", "balanced", "reflective"] = "balanced"
    preserve_agency: bool = True
    max_tokens: int = Field(default=800, ge=1, le=8192)
    temperature: float = Field(default=0.2, ge=0, le=2)
    conversation_id: str | None = Field(default=None, max_length=128)


class BenefitVector(BaseModel):
    # These are deliberately unknown until an actual evaluation method exists.
    clarity: float | None = None
    agency: float | None = None
    skill: float | None = None
    dependency_risk: float | None = None
    passion: float | None = None
    measurement_status: Literal["not_measured"] = "not_measured"


class Provenance(BaseModel):
    provenance_id: str
    created_at: str
    provider: str
    model: str
    evidence_status: Literal["generated_not_independently_verified"] = "generated_not_independently_verified"


class ChatResponse(BaseModel):
    id: str
    conversation_id: str
    content: str
    model: str
    created_at: str
    metadata: dict[str, Any]


class FeedbackRequest(BaseModel):
    response_id: str = Field(min_length=1, max_length=128)
    rating: Literal["helpful", "not_helpful", "mixed"]
    comment: str | None = Field(default=None, max_length=2000)


async def authorize(authorization: str | None = Header(default=None)) -> None:
    """Optional bearer-key gate. Set ANNABAN_API_KEY to enable it."""
    if not API_KEY:
        return
    expected = f"Bearer {API_KEY}"
    if authorization is None or not _constant_time_equal(authorization, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")


def _constant_time_equal(left: str, right: str) -> bool:
    import hmac
    return hmac.compare_digest(left.encode(), right.encode())


def _client():
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Model provider is not configured. Set OPENAI_API_KEY and ANNABAN_MODEL at runtime.",
        )
    try:
        from openai import AsyncOpenAI
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Install the optional openai dependency.") from exc
    kwargs: dict[str, Any] = {"api_key": os.environ["OPENAI_API_KEY"]}
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return AsyncOpenAI(**kwargs)


def _user_prompt(request: ChatRequest) -> str:
    return "\\n".join(message.content for message in request.messages if message.role == "user")


def _ledger() -> GovernanceLedger:
    path = os.getenv("ANNABAN_GOVERNANCE_LEDGER_PATH", "logs/governance_ledger.jsonl")
    return GovernanceLedger(ledger_path=path)


def _audit_event(
    action: str,
    status: str,
    request: ChatRequest,
    *,
    risk_flagged: bool = False,
    requires_approval: bool = False,
    response_marker: str = "[REDACTED]",
) -> None:
    """Write governance metadata without retaining user prompts or model output."""
    try:
        _ledger().append(
            action=action,
            status=status,
            notes="Prompt and response content redacted by API privacy policy.",
            prompt="[REDACTED]",
            response=response_marker,
            risk_flagged=risk_flagged,
            requires_approval=requires_approval,
            governance_output={
                "request_id": request.conversation_id,
                "policy": "AnnabanGovernance",
                "content_retained": False,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Governance audit ledger unavailable; request stopped.") from exc


def _client_for_request(request: ChatRequest, action: str):
    try:
        return _client()
    except HTTPException:
        _audit_event(action, "failed", request, response_marker="[PROVIDER UNAVAILABLE]")
        raise


def _preflight(request: ChatRequest, action: str) -> None:
    """Fail closed on the repository's high-risk keyword policy before provider calls."""
    prompt = _user_prompt(request)
    if AnnabanGovernance.is_high_risk_prompt(prompt):
        _audit_event(
            action,
            "blocked",
            request,
            risk_flagged=True,
            requires_approval=True,
            response_marker="[HUMAN APPROVAL REQUIRED]",
        )
        raise HTTPException(
            status_code=409,
            detail={
                "status": "human_approval_required",
                "message": AnnabanGovernance.APPROVAL_MESSAGE,
                "policy": "HIGH_RISK_KEYWORD_GATE",
            },
        )
    _audit_event(action, "started", request)


def _provider_messages(request: ChatRequest) -> list[dict[str, str]]:
    system = TEMPO_MODES[request.tempo_mode]
    if request.preserve_agency:
        system += (
            " Preserve user agency: offer options and explain trade-offs; do not imply "
            "that the assistant can make decisions for the user. Ask before consequential actions."
        )
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    # Merge policy guidance into an existing system message or add one at the front.
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] += "\n\nAnnabanAI interaction policy: " + system
    else:
        messages.insert(0, {"role": "system", "content": "AnnabanAI interaction policy: " + system})
    return messages


def _metadata(request: ChatRequest, provenance: Provenance, elapsed_ms: int) -> dict[str, Any]:
    return {
        "tempo_applied": request.tempo_mode,
        "preserve_agency": request.preserve_agency,
        "empathy_score": None,
        "sentiment": None,
        "benefit_vector": BenefitVector().model_dump(),
        "cognitive_load": None,
        "measurement_note": "Unmeasured fields are null; no psychological inference is claimed.",
        "timing_ms": elapsed_ms,
        "provenance": provenance.model_dump(),
        "covenant_aligned": None,
        "covenant_status": "not_evaluated",
    }


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "AnnabanAI Chat API",
        "provider_configured": str(bool(os.getenv("OPENAI_API_KEY"))).lower(),
        "version": APP_VERSION,
    }


@app.get("/api/v1/chat/tempo-modes", dependencies=[Depends(authorize)], tags=["chat"])
async def tempo_modes() -> dict[str, Any]:
    return {"modes": [{"id": key, "description": value} for key, value in TEMPO_MODES.items()]}


@app.get("/api/v1/covenant", dependencies=[Depends(authorize)], tags=["governance"])
async def covenant() -> dict[str, Any]:
    return COVENANT


@app.post("/api/v1/chat/completions", response_model=ChatResponse, dependencies=[Depends(authorize)], tags=["chat"])
async def chat_completions(request: ChatRequest) -> ChatResponse:
    _preflight(request, "chat_completions")
    client = _client_for_request(request, "chat_completions")
    started = time.perf_counter()
    try:
        result = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=_provider_messages(request),
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except Exception as exc:
        _audit_event("chat_completions", "failed", request, response_marker="[PROVIDER ERROR]")
        # Do not leak provider details, credentials, or prompt content to callers.
        raise HTTPException(status_code=502, detail="Model provider request failed.") from exc
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    content = result.choices[0].message.content or ""
    now = datetime.now(timezone.utc).isoformat()
    response_id = "annaban_" + uuid.uuid4().hex
    provenance = Provenance(
        provenance_id=uuid.uuid4().hex,
        created_at=now,
        provider=os.getenv("OPENAI_BASE_URL", "openai"),
        model=MODEL_NAME,
    )
    _audit_event("chat_completions", "completed", request, response_marker="[GENERATED; CONTENT NOT RETAINED]")
    return ChatResponse(
        id=response_id,
        conversation_id=request.conversation_id or uuid.uuid4().hex,
        content=content,
        model=MODEL_NAME,
        created_at=now,
        metadata=_metadata(request, provenance, elapsed_ms),
    )


@app.post("/api/v1/chat/stream", dependencies=[Depends(authorize)], tags=["chat"])
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    _preflight(request, "chat_stream")
    client = _client_for_request(request, "chat_stream")

    async def events() -> AsyncIterator[str]:
        try:
            stream = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=_provider_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield "data: " + json.dumps({"delta": delta}, ensure_ascii=False) + "\n\n"
            _audit_event("chat_stream", "completed", request, response_marker="[STREAMED; CONTENT NOT RETAINED]")
            yield "data: [DONE]\n\n"
        except Exception:
            try:
                _audit_event("chat_stream", "failed", request, response_marker="[PROVIDER ERROR]")
            except HTTPException:
                pass
            # Avoid sending provider exceptions or sensitive request data over SSE.
            yield "event: error\ndata: " + json.dumps({"detail": "Model provider stream failed."}) + "\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@app.post("/api/v1/chat/feedback", status_code=202, dependencies=[Depends(authorize)], tags=["feedback"])
async def feedback(request: FeedbackRequest) -> dict[str, Any]:
    # Feedback text is not persisted; only a redacted governance event is recorded.
    try:
        _ledger().append(
            action="chat_feedback",
            status="accepted",
            notes="Feedback accepted but not persisted.",
            prompt="[REDACTED]",
            response="[FEEDBACK NOT RETAINED]",
            risk_flagged=False,
            requires_approval=False,
            governance_output={"response_id": request.response_id, "rating": request.rating, "content_retained": False},
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Governance audit ledger unavailable; feedback not accepted.") from exc
    return {
        "accepted": True,
        "response_id": request.response_id,
        "rating": request.rating,
        "persisted": False,
        "comment_received": request.comment is not None,
    }
