# Heritage Stack™ v1.3.1 — Product Requirements Document

**Document ID:** HS-PRD-1.0-DRAFT  
**Status:** Draft — not approved or baselined  
**Lifecycle:** Gate 1 — DEFINE  
**Project attribution:** Jacob Wayne Kinnaird (`faucet_fan`), project originator and attributed architect

## 1. Purpose

Define the intended boundaries and initial acceptance requirements for a governance-focused system that processes telemetry, evaluates policies, verifies evidence, and blocks consequential actions unless the required human authorization is present.

This document captures a proposed design. It does not certify an implementation or claim that any requirement has passed.

## 2. System boundaries

### In scope for the proposed baseline

- Ingesting versioned telemetry payloads.
- Validating payload structure and provenance.
- Recomputing hashes from explicitly defined canonical bytes.
- Evaluating authorization policies using explicit, testable evidence inputs.
- Blocking consequential state changes when required signatures or approvals are absent, invalid, expired, or revoked.
- Recording evidence and human release decisions for each project gate.
- Keeping simulations separate from external actions.

### Out of scope unless separately approved

- Autonomous consequential actions without human authorization.
- Claims of physical qualification based only on simulation or numerical modelling.
- Claims of legal ownership, patent status, funding, government approval, or third-party endorsement without documentary evidence.
- Treating a valid hash as proof that a sensor measurement is physically accurate.
- Treating AI-generated recommendations as approval or execution.

## 3. Governance principles

1. **Human authority:** A named human reviewer approves release-gate transitions and consequential actions.
2. **Default deny:** Missing or invalid required evidence blocks the protected action.
3. **Veto and freeze:** A defined high-risk condition enters a deterministic blocked/frozen state.
4. **Evidence before claims:** Status claims link to artifacts, test logs, signatures, or external records.
5. **Separation of duties:** Authoring, implementation, and independent verification are recorded separately when different people or organizations perform them.
6. **Simulation boundary:** Internal simulations have `external_effect = 0`; they must not be represented as real-world execution.
7. **Recoverability:** Key loss, revocation, or integrity failure must not silently bypass authorization controls.

## 4. Proposed functional requirements

The controlled requirements and acceptance criteria are listed in [RTVM_v1.0.csv](RTVM_v1.0.csv). The initial set covers schema validation, attestation rejection, hash recomputation, thermal performance, steady acceleration, authorization freeze, and evidence-backed gate transitions.

## 5. Authorization semantics — unresolved design decision

The phrases “single-key Sovereign Command override” and “dual approval” must not be used interchangeably. Before implementation, define:

- Which action classes require one signature and which require two independent approvals.
- Whether any override can bypass a safety veto (default: no bypass unless a formally reviewed exception is defined).
- Signer identity, key purpose, trust root, validity period, revocation behavior, and signature algorithm.
- Replay protection, request expiry, nonce or sequence-number handling, and canonical signed content.
- Fail-closed behavior during verifier, clock, network, or key-service failure.
- Recovery and reauthorization after a freeze.
- Required audit events and the identity of the human decision-maker.

Until resolved and approved, consequential authorization behavior is **not ready for production implementation**.

## 6. Performance target

A processing-latency target below 45 ms has been mentioned in project discussions. It is **not a verified performance result**. Before it becomes a requirement, define the measured path, hardware, payload size, network conditions, persistence behavior, cryptographic operations, concurrency, sample size, percentile (for example p95/p99), and failure thresholds.

## 7. Physical test boundaries

The 720°C exposure and internal sensor temperature limit of 70°C are proposed test goals, not established performance. The thermal protocol must define the heat flux, specimen construction, exposure duration, measurement location, instrumentation, uncertainty, and post-exposure function. A nominal source temperature alone is insufficient to define the test.

The 10G steady-acceleration test is separate from random vibration and shock tests. Passing one does not imply passing the others.

No physical test may be described as passed until a complete report and raw supporting evidence have been reviewed.

## 8. Gate 1 exit conditions

Gate 1 may be proposed for closure only when all of the following are complete:

- This PRD is reviewed, versioned, and approved by the human project authority.
- The controlled RTVM maps each requirement to a procedure, owner, and evidence artifact.
- The risk register records risk owners and acceptance/mitigation decisions.
- Candidate standards and project-specific test procedures have documented applicability.
- Authorization semantics and cryptographic trust boundaries are explicit.
- Missing implementation and verification owners are assigned.
- The human reviewer records an auditable decision.

Gate 2 requires a separate recorded approval; completing documentation alone does not establish that hardware or software is verified.

## 9. Attribution and contribution

Jacob Wayne Kinnaird is identified as the project originator and attributed architect based on the project record supplied for this document. AI tools contributed drafting and review assistance. Actual implementation contributors, test operators, and independent verifiers must be named when their work is performed. Legal rights remain subject to applicable law, agreements, licenses, and evidence.

## 10. Approval record

- Human project authority: Jacob Wayne Kinnaird
- Decision: **Pending**
- Date: **Pending**
- Signature / repository evidence: **Pending**
