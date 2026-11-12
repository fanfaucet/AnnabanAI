# OpenAI API compatibility note and Python examples

**Project attribution:** Jacob Wayne Kinnaird — project-level direction and documentation contribution  
**Repository:** AnnabanAI  
**Status:** Reference examples; not executed against a live API in this commit  
**Scope:** Text generation, streaming, conversation continuity, and tool-calling concepts

## Correcting the historical claim

The statement that GPT-5 or GPT-5.3 had not been released was time-bound and is not a reliable description of the API in November 2026. Model names, access, and API support change over time. Check the official model catalog and the models available to your API project before choosing a model:

- https://platform.openai.com/docs/models
- https://platform.openai.com/docs/api-reference/responses
- https://platform.openai.com/docs/guides/function-calling

Do not assume that a model name in an example is enabled for every account. The examples below use `gpt-4o` as a configurable example model ID; replace it with a model supported by your project.

## 1. Install the SDK

```bash
python -m pip install --upgrade openai
```

## 2. Configure the API key

Set `OPENAI_API_KEY` in your shell or secret manager. Never commit API keys or hard-code them into source files.

Linux/macOS:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4o"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:OPENAI_MODEL = "gpt-4o"
```

## 3. Basic request with the Responses API

Save as `basic_request.py`:

```python
import os
from openai import OpenAI

client = OpenAI()  # Reads OPENAI_API_KEY from the environment.
model = os.getenv("OPENAI_MODEL", "gpt-4o")

response = client.responses.create(
    model=model,
    instructions="You are a helpful assistant. Explain concepts clearly.",
    input="Explain quantum entanglement in simple terms.",
    max_output_tokens=300,
)

print(response.output_text)
```

## 4. Stream text output

```python
import os
from openai import OpenAI

client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-4o")

with client.responses.stream(
    model=model,
    input="Write a short original poem about space travel.",
) as stream:
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
    print()
```

## 5. Multi-turn conversation

For simple continuity, the Responses API supports chaining through a prior response ID. This example keeps the prior response ID in memory for the duration of the process:

```python
import os
from openai import OpenAI

client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-4o")
previous_response_id = None

while True:
    try:
        prompt = input("You (or /quit): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        break

    if prompt.lower() in {"/quit", "/exit"}:
        break
    if not prompt:
        continue

    request = {"model": model, "input": prompt, "max_output_tokens": 600}
    if previous_response_id:
        request["previous_response_id"] = previous_response_id

    try:
        response = client.responses.create(**request)
        print("Assistant:", response.output_text)
        previous_response_id = response.id
    except Exception as exc:
        print(f"Request failed: {type(exc).__name__}: {exc}")
```

Conversation retention and response chaining behavior depend on API settings and product policy. For applications that need explicit local state, persist only the data necessary, with defined retention and deletion controls.

## 6. Function calling: define the contract and execute the tool yourself

Tool calling is a protocol, not permission for the model to execute arbitrary code. The application must validate arguments, authorize the operation, execute the function, and return the result to the model. A safe minimal illustration follows; it does not call any external service.

```python
import json
import os
from openai import OpenAI

client = OpenAI()
model = os.getenv("OPENAI_MODEL", "gpt-4o")

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Return a placeholder weather result for a city.",
    "parameters": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
        "additionalProperties": False,
    },
    "strict": True,
}]

def get_weather(location: str) -> dict:
    # Placeholder only: replace with a real, authorized weather provider.
    return {"location": location, "status": "demo_only", "temperature_c": None}

response = client.responses.create(
    model=model,
    input="What is the weather in Paris?",
    tools=tools,
)

for item in response.output:
    if item.type != "function_call" or item.name != "get_weather":
        continue

    args = json.loads(item.arguments)
    location = args.get("location")
    if not isinstance(location, str) or not location.strip() or len(location) > 120:
        raise ValueError("Invalid location argument")

    result = get_weather(location.strip())
    response = client.responses.create(
        model=model,
        previous_response_id=response.id,
        input=[{
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result),
        }],
        tools=tools,
    )

print(response.output_text)
```

The example uses a placeholder function and intentionally does not claim to retrieve live weather. Production implementations must handle every returned function call, validate input, apply authorization, set timeouts, and enforce least privilege.

## Compatibility and safety notes

- These examples use the modern `OpenAI` Python client and Responses API rather than legacy `openai.ChatCompletion.create` or the older `functions` parameter format.
- SDK and API capabilities vary by model. Confirm model support before using optional parameters.
- Never log API keys. Avoid logging sensitive prompts or tool arguments without a defined policy.
- Add dependency pinning, automated tests, retry/backoff rules, timeouts, and explicit error handling before production deployment.
- This commit records reference documentation only. No live API request, integration test, production deployment, or performance benchmark is claimed.
- Economic impact: no revenue or cost savings are established by this documentation alone. Quantify value only after testing implementation effort, failure rates, latency, and operating cost.

## Provenance

This documentation contribution is attributed at the project level to **Jacob Wayne Kinnaird**. That attribution records project direction and authorship of this contribution; it does not, by itself, determine legal ownership of all underlying SDKs, model outputs, or third-party intellectual property.
