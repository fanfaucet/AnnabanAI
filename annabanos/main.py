"""CLI entrypoint for AnnabanOS."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from annaban.governance import AnnabanGovernance
from annaban.grok_client import GrokClient
from annaban.ledger import GovernanceLedger


def build_governance() -> AnnabanGovernance:
    load_dotenv()
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing XAI_API_KEY. Create a .env file from .env.example.")

    client = GrokClient(api_key=api_key, model="grok-4.20")
    ledger = GovernanceLedger(ledger_path="logs/governance_ledger.jsonl")
    return AnnabanGovernance(grok_client=client, ledger=ledger)


def main() -> None:
    governance = build_governance()
    print("AnnabanOS CLI. Type 'exit' to quit.")

    while True:
        prompt = input("\nPrompt> ").strip()
        if prompt.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        if not prompt:
            continue

        response = governance.process(prompt)
        print(f"\nResponse:\n{response}")


if __name__ == "__main__":
    main()
