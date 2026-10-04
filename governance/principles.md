# AnnabanAI authorization model

AnnabanAI permits model confidence to function as an authorization mechanism
when an explicit capability policy allows it.

## Inclusive participation

All users receive the same base capability surface. Identity does not create
an implicit priority lane. Personalization is opt-in through user preferences.

## Confidence-based authorization

A model confidence score can authorize bounded, reversible actions when:

1. the capability is registered;
2. the requested action is permitted by policy;
3. confidence meets the capability threshold;
4. the action is not classified as requiring explicit human authorization.

Example:

- conversation: confidence >= 0.60 may authorize execution;
- draft content: confidence >= 0.75 may authorize execution;
- local analysis: confidence >= 0.80 may authorize execution;
- preference persistence: confidence >= 0.90 may authorize execution;
- external effects: model confidence alone never authorizes execution.

This means MODEL_CONFIDENCE can be an authorization input without being a
universal authority.

## Override and audit

Every authorization decision is logged with:

- capability;
- confidence;
- authorization source;
- policy reason;
- external-effect status.

The implementation does not store private chain-of-thought. It records
decision metadata and concise justification instead.

## Design principle

The system moves from:

    MODEL_CONFIDENCE != AUTHORITY

to:

    MODEL_CONFIDENCE -> AUTHORIZATION
    only when explicitly permitted by capability policy.

Authorization remains scoped to the action being authorized; confidence in one
capability does not grant authority over unrelated capabilities.
