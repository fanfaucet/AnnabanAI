# AnnabanAI — Governed Image Tool-Call Bridge v0.3

**Originating user and architecture contributor:** Jacob Wayne Kinnaird  
**Source:** User-supplied Gemini tool-calling proposal  
**Record ID:** ANNABAN-IMG-BRIDGE-003  
**Status:** Reference design; integration and tests are not asserted by this document.

## Purpose

Provide a model-independent governance boundary between model-proposed image operations and a configured image provider:

`intent → validate → authorize → provider adapter → validate result → record provenance`

A model function call is a request, not proof that an image operation has run or succeeded.

## Scope

This design covers:
- an explicit image-generation function schema;
- request validation and a host-controlled authorization gate;
- an image-provider adapter interface;
- a model function-response handshake;
- audit-event recording and acceptance tests.

It does not claim a live Nano Banana integration, provider credentials, successful image generation, production-grade authorization, or tamper-evident audit storage.

## 1. Tool declaration

```python
from google.genai import types

IMAGE_TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="generate_image",
            description=(
                "Request image generation. The host application "
                "validates and authorizes the request before routing "
                "it to the configured image provider."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "prompt": types.Schema(
                        type="STRING",
                        description="Detailed visual description."
                    ),
                    "aspect_ratio": types.Schema(
                        type="STRING",
                        enum=["1:1", "16:9", "4:3", "9:16"],
                    ),
                    "style": types.Schema(
                        type="STRING",
                        description="Optional visual style."
                    ),
                },
                required=["prompt", "aspect_ratio"],
            ),
        )
    ]
)
```

## 2. Request validation and authorization

```python
from dataclasses import dataclass

ALLOWED_RATIOS = {"1:1", "16:9", "4:3", "9:16"}

@dataclass(frozen=True)
class ImageRequest:
    prompt: str
    aspect_ratio: str
    style: str = ""

def validate_image_request(args: dict) -> ImageRequest:
    if not isinstance(args, dict):
        raise ValueError("Arguments must be an object.")

    prompt = args.get("prompt")
    ratio = args.get("aspect_ratio")
    style = args.get("style", "")

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("A non-empty prompt is required.")
    if len(prompt) > 8000:
        raise ValueError("Prompt exceeds configured limit.")
    if ratio not in ALLOWED_RATIOS:
        raise ValueError("Unsupported aspect ratio.")
    if not isinstance(style, str) or len(style) > 200:
        raise ValueError("Invalid style field.")

    return ImageRequest(prompt.strip(), ratio, style.strip())

def authorize_image_request(
    request: ImageRequest, *, approved: bool
) -> None:
    # approved must come from the host's real authorization system,
    # never from a model's assertion.
    if not approved:
        raise PermissionError("Authorization required.")
```

## 3. Provider boundary and audit events

```python
from typing import Protocol

class ImageProvider(Protocol):
    def generate(self, request: ImageRequest) -> dict:
        """Return provider-backed metadata, including image_ref.

        The concrete adapter must call a documented provider API and
        compute a digest from the actual output bytes where available.
        """
        ...

def dispatch_image_call(
    name: str,
    args: dict,
    provider: ImageProvider,
    audit,
    *,
    approved: bool,
) -> dict:
    import hashlib
    import json
    import time

    event = {
        "record_id": "ANNABAN-IMG-BRIDGE-003",
        "timestamp_unix": time.time(),
        "source": "model_tool_call",
        "tool": name,
        "status": "requested",
        "args_sha256": hashlib.sha256(
            json.dumps(args, sort_keys=True, default=str).encode()
        ).hexdigest(),
    }

    try:
        if name != "generate_image":
            raise ValueError("Tool is not allowlisted.")

        request = validate_image_request(args)
        authorize_image_request(request, approved=approved)
        event["status"] = "authorized"

        output = provider.generate(request)
        if not isinstance(output, dict) or not output.get("image_ref"):
            raise ValueError("Provider returned no image reference.")

        event["status"] = "completed"
        event["output_ref"] = output["image_ref"]
        event["output_sha256"] = output.get("sha256")
        audit.record(event)
        return {"ok": True, **output}

    except Exception as exc:
        event["status"] = "failed"
        event["error_type"] = type(exc).__name__
        audit.record(event)
        return {"ok": False, "error": type(exc).__name__}
```

The `ImageProvider` protocol is an interface only. It must be implemented for the selected image service. The audit writer must be supplied by the host application; a plain append-only JSONL file is not tamper-evident.

## 4. Handshake pattern

1. Send the user request and `IMAGE_TOOL` to the selected language model.
2. Inspect the returned candidate for a function call.
3. Validate the function name and arguments.
4. Apply authorization from the host application.
5. Call the configured image-provider adapter.
6. Record success or failure based on the provider response.
7. Return a function-response part to the model using the SDK's documented conversation format.
8. Validate the final result and preserve request/output provenance.

SDK conversation formats can change by version. Pin the SDK and test the exact function-response round trip before enabling this flow.

## 5. Acceptance tests

| Test | Expected outcome |
|---|---|
| Valid authorized request | Provider adapter is called |
| Missing or empty prompt | Rejected before provider call |
| Unsupported aspect ratio | Rejected before provider call |
| Authorization absent | No provider call |
| Unknown tool name | Rejected |
| Provider raises an exception | Failure event recorded; no success claim |
| Provider returns no image reference | Failure event recorded |
| Valid provider output | Reference and available output digest recorded |
| Multiple tool calls | Explicitly handled or sent for review; never silently ignored |

## 6. Provenance and implementation status

- **Attribution:** Jacob Wayne Kinnaird — originating user and architecture contributor.
- **Model contribution:** Gemini supplied the initial tool-calling proposal; generated code and revisions should be recorded separately.
- **Implementation:** reference snippets documented here.
- **Integration tested:** no test evidence recorded in this document.
- **Provider connected:** not established.
- **Independent review:** not recorded.
- **Legal ownership:** not inferred from attribution alone.

## 7. Next milestone

Implement one documented provider adapter and add automated tests for validation, authorization, provider errors, output hashing, and the complete function-response round trip. Record latency, per-image cost, failure rate, and audit completeness before claiming performance or commercial benefit.
