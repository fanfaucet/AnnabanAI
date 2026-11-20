# Heritage Stack™ v1.3.1 — Standards Rationale

**Status:** Draft for technical review. The standards below are candidates or guidance references, not proof of compliance.

## General rule

Before selecting a standard for qualification, record the exact edition, applicable clauses/methods, intended environment, specimen configuration, deviations, laboratory capability, and pass/fail criteria. A standard's name alone does not demonstrate applicability or compliance.

| Reference | Intended role in this project | Limits and work still required |
|---|---|---|
| ASTM E285, edition to be confirmed (the review notes cite E285-08 (2020)) | Candidate screening method for ablative thermal-insulation materials | Does not by itself qualify a complete sensor assembly for every 720°C environment. Confirm the current edition, scope, specimen details, burner/heat-flux conditions, and relevance to the intended use. |
| MIL-STD-810H Method 501.7 | Candidate high-temperature environmental test method | Ambient high-temperature exposure is not equivalent to a short, intense thermal-protection event. Select procedure and severity based on intended lifecycle environment. |
| IEC 60068-2-7 | Candidate steady-acceleration test | Distinct from random vibration and mechanical shock. Confirm edition, applicability, axes, duration, mounting, and severity. |
| MIL-STD-810H Method 514.8 | Candidate vibration test method | A vibration category/profile must be justified by the actual platform and mounting location. A frequency range alone does not define a test; PSD, duration, axis, and fixture are required. |
| NIST SP 800-218 (SSDF) | Secure software development practices | Map selected practices to actual development processes and evidence. It is not a product certification. |
| NIST SP 800-218A | SSDF profile for generative AI and dual-use foundation models | Apply only to relevant development/use contexts; do not treat it as interchangeable with the AI RMF. |
| NIST AI 100-1 (AI RMF) | AI risk-management framework | Organizes risk work; it is not itself a physical or software test procedure. |

## Thermal test definition needed

TP-THERMAL-01 must define at least: source and calibrated incident heat flux; specimen construction and dimensions; boundary conditions; exposure duration; sensor location; temperature measurement method and uncertainty; sampling rate; pass/fail rule; post-exposure functional test; and safe test termination criteria.

A “720°C exposure” is incomplete unless it states what reaches 720°C (source, gas, surface, or test chamber) and what the measured thermal load at the specimen is.

## Mechanical test definition needed

TP-MECH-01 must define the acceleration profile, three axes and orientations, fixture, ramp rate, dwell, instrumentation, baseline and post-test continuity measurement, tolerance, inspection criteria, and report format.

Random vibration must have a separate protocol and a justified PSD profile. Passing a steady 10G test does not imply passing vibration or shock.

## Security and AI risk mapping

- Use SP 800-218 for secure software development controls and evidence.
- Use SP 800-218A only where its generative-AI/dual-use-foundation-model profile is applicable.
- Use NIST AI 100-1 for AI risk identification, assessment, treatment, and monitoring.
- Define cryptographic verification independently: key trust, signature checks, canonicalization, expiry, revocation, replay protection, and failure behavior.

## Approval

Exact editions and test applicability remain **pending technical review**. No compliance or qualification claim is made by this document.
