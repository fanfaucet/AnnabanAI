# GPT-5.3-family API example for AnnabanAI

**Status:** implementation example; not executed against a live API in this commit.  
**Purpose:** a small Python reference for a text request, streaming output, and process-local multi-turn history.

## Model ID

The currently documented GPT-5.3-family model ID surfaced in OpenAI's API pricing documentation is `gpt-5.3-codex`. Model availability can depend on API account access. Set `OPENAI_MODEL` to a model ID enabled for your project; do not assume `gpt-5.3-mini` or `gpt-5.3-large` are valid model IDs.

## 1. Install

```bash
python -m pip install --upgrade openai
```

## 2. Configure credentials

Set the API key in your shell or deployment secret manager. Do not hard-code it, commit it, or print it in logs.

Linux/macOS:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-5.3-codex"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:OPENAI_MODEL = "gpt-5.3-codex"
```

## 3. Basic request

Save as `basic_request.py`:

```python
import os
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from the environment
model = os.getenv("OPENAI_MODEL", "gpt-5.3-codex")

response = client.responses.create(
    model=model,
    instructions="You are a helpful assistant. Be clear and concise.",
    input="Explain quantum entanglement in simple terms.",
    max_output_tokens=300,
)

print(response.output_text)
```

Run it with:

```bash
python basic_request.py
```

## 4. Streaming

Save as `stream_response.py`:

```python
import os
from openai import OpenAI

client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-5.3-codex")

with client.responses.stream(
    model=model,
    input="Write a short original poem about space travel.",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()
```

## 5. Minimal multi-turn loop

This example keeps history in process memory only. It is lost when the program exits and is not a persistent memory system. For production, define retention, access controls, deletion, and storage policies before persisting conversation data.

Save as `chat_loop.py`:

```python
import os
from openai import OpenAI

client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-5.3-codex")
instructions = "You are a helpful assistant. Be clear and concise."

# Process-local history: user and assistant turns for this run only.
history = []

def ask(user_text: str) -> str:
    history.append({"role": "user", "content": user_text})
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=history,
        max_output_tokens=600,
    )
    answer = response.output_text
    history.append({"role": "assistant", "content": answer})
    return answer

def main() -> None:
    print("Chat started. Type /quit to exit.")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_text.lower() in {"/quit", "/exit"}:
            break
        if not user_text:
            continue

        try:
            print(f"Assistant: {ask(user_text)}")
        except Exception as exc:
            # Avoid logging credentials or full request payloads.
            print(f"API request failed: {type(exc).__name__}: {exc}")
            # Remove the failed user turn so a retry doesn't duplicate it.
            if history and history[-1].get("role") == "user":
                history.pop()

if __name__ == "__main__":
    main()
```

## 6. Tools are explicit

The old example's `tools=["python"]` is not a valid generic tool configuration. A model does not gain arbitrary Python execution just because the prompt says it can calculate. Configure a documented tool supported by the selected API/model, implement any required tool-call handling, and apply least-privilege controls. Never execute model-generated code on the host without a deliberate sandbox and authorization boundary.

## Notes and limits

- This uses the OpenAI Python SDK's **Responses API**, rather than the legacy `openai.ChatCompletion.create` / `ChatCompletion.stream` calls.
- `max_output_tokens` limits generated output; it is not the legacy `max_tokens` parameter.
- Temperature support and other generation parameters vary by model. Add parameters only after confirming that the selected model supports them.
- This file is a reference implementation, not a claim that a live request or integration test passed.
- Official references: [OpenAI API pricing and model IDs](https://platform.openai.com/pricing), [OpenAI API documentation](https://platform.openai.com/docs).
