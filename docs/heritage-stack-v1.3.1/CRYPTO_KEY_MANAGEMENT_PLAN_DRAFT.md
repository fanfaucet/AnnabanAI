# Heritage Stack™ v1.3.1 — Cryptographic Key Management Plan

**Status:** Draft; no HSM deployment or key ceremony is claimed.

## 1. Purpose

Define the minimum design questions and controls for trusted attestations and authorization. Implementation details must be selected and reviewed before any production claim.

## 2. Key roles

Document separate key purposes for:
- Device or telemetry-source attestation.
- Service identity and inter-service authentication.
- Human authorization of consequential actions.
- Release evidence or gate-decision signing.
- Test and development environments.

Do not reuse one key across roles without an explicit, reviewed justification.

## 3. Required lifecycle controls

1. **Provisioning:** Record who or what generated the key, where, when, for which identity and purpose, and how the public key entered the trust store.
2. **Storage:** Keep private keys in an appropriately protected key store; never commit secrets to source control or test fixtures.
3. **Use:** Restrict signing operations to authorized identities and narrowly scoped actions.
4. **Rotation:** Define key lifetime, planned rotation, overlap behavior, and how old signatures remain verifiable.
5. **Revocation:** Define a trusted revocation source, update process, cache behavior, and fail-closed handling when revocation status cannot be established.
6. **Expiry:** Define clock source, validity checks, skew tolerance, and behavior when time is unavailable or untrusted.
7. **Compromise:** Define immediate containment, revocation, replacement, affected-record assessment, and incident evidence.
8. **Recovery:** Define a controlled recovery process that cannot silently bypass the normal authorization policy.
9. **Audit:** Record key identifiers and decisions, not private key material. Protect audit records against unauthorized modification.
10. **Separation:** Keep test keys separate from production keys and mark test credentials unmistakably.

## 4. Signature and payload verification

The implementation must specify:
- Approved signature algorithms and cryptographic libraries.
- Exact canonical byte representation of the signed payload.
- Schema version and domain separation in signed content.
- Key identity, trust chain or trust-store rule, validity, purpose, and revocation checks.
- Nonce, sequence number, expiry, or equivalent replay protection.
- Duplicate and out-of-order request behavior.
- Failure behavior for missing fields, malformed signatures, unknown keys, expired keys, revoked keys, unavailable trust services, and verifier errors.

A hash proves only that particular bytes produce a particular digest. It does not by itself prove who produced the bytes, whether the sensor was calibrated, or whether the reported physical event occurred.

## 5. Human authorization

The PRD must define which action classes require one human signature and which require two independent approvals. It must define the signer identity, exact action and context being authorized, expiry, veto behavior, audit event, and freeze-release procedure. No AI output is itself an authorization credential.

## 6. HSM status

HSM integration is **not established**. Any future implementation should have an integration plan, threat model, test evidence, access-control review, backup/recovery policy, and documented benchmark. Do not report HSM deployment until supported by verifiable evidence.

## 7. Approval checklist

- [ ] Key roles and trust roots defined
- [ ] Provisioning and rotation defined
- [ ] Revocation and expiry defined
- [ ] Canonicalization and replay protection defined
- [ ] Failure modes and fail-closed behavior tested
- [ ] Human approval semantics approved
- [ ] Incident and recovery procedures reviewed
- [ ] Implementation and verification owners assigned

**Approver:** Pending  
**Decision date:** Pending
