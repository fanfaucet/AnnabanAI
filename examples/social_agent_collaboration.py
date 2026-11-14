"""Small, local-only demonstration of AnnabanAI's SocialAgent collaboration model.

This is a simulation example. It does not contact Codex, Cursor, ChatGPT, or xAI.
"""

from __future__ import annotations

import json

from agents.agent_hierarchy import SocialAgent


# ChatGPT self-review note during the Codex push:
# The repository's real SocialAgent lives in agents.agent_hierarchy and expects
# (agent_id, name=None); do not use the earlier illustrative BaseAgent signature.
# Relationship records model local state only; they are not live agent connections.
REWARD_EXAMPLES = [
    {"task": "Write a short poem", "reward": 5.0},
    {"task": "Help another agent finish a report", "reward": 8.0},
]


def main() -> None:
    annaban = SocialAgent(agent_id="annaban", name="Annaban")

    # Directional records: Annaban records interactions with each named peer.
    codex_relationship = annaban.interact("codex")
    cursor_relationship = annaban.interact("cursor")

    result = {
        "mode": "simulation_only",
        "live_connections": False,
        "human_authority": "Jacob Wayne Kinnaird",
        "relationships": [
            {
                "agent_id": codex_relationship.agent_id,
                "trust": codex_relationship.trust,
                "interactions": codex_relationship.interactions,
            },
            {
                "agent_id": cursor_relationship.agent_id,
                "trust": cursor_relationship.trust,
                "interactions": cursor_relationship.interactions,
            },
        ],
        "reward_examples": REWARD_EXAMPLES,
        "reward_status": "illustrative_targets_not_earned_rewards",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
