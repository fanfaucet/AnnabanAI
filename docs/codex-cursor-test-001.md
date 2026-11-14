# AnnabanAI Test 1 — Codex guides Cursor

**Status:** Conceptual test specification; local-only simulation example  
**Requested by:** Jacob Wayne Kinnaird  
**Implementation provenance:** AI-generated code prompted by Jacob Wayne Kinnaird; this attribution does not determine legal ownership.

## Objective

Model a human-directed coaching workflow in which Codex provides guidance for Cursor to assist another agent. Evaluate completed work rather than rewarding an intention or promise.

## Proposed sequence

1. Codex states the task, assumptions, and observable acceptance criteria.
2. Cursor drafts a response or artifact.
3. Codex checks accuracy, completeness, usefulness, and evidence boundaries.
4. The human reviews the evaluation and decides whether the task is complete.
5. Record the rationale for any reward assignment.

## Initial illustrative reward examples

| Task | Reward target |
|---|---:|
| Write a short poem | 5.0 |
| Help another agent finish a report | 8.0 |

These values are example preferences, not validated measures of quality. The 8.0 reward is not earned until a completed report is assessed against explicit criteria.

## Execution and integration boundary

- The Python example uses the repository's existing `SocialAgent` in `agents/agent_hierarchy.py`.
- Its relationship records are local data only.
- No live Codex, Cursor, ChatGPT, or xAI session is opened by this example.
- No model training or external API request occurs.
- The current repository's `AGENTS.md` requires visible explanation and human approval before major execution steps.

## Developer adjustment

When a scene places instructions into a simulated Codex input field and depicts Annaban pressing Enter, advance the narrative through a clearly labeled simulated execution and observer report rather than stopping at the prompt. Never label an emulation as a real background process.

## Review checklist

- [ ] Confirm the repository's actual agent class and constructor before implementation.
- [ ] Verify duplicate relationship behavior and whether relationships are directional.
- [ ] Evaluate completed output before assigning reward.
- [ ] Preserve simulation labels and provenance.
- [ ] Obtain human approval before any external or irreversible action.
