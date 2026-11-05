# Heritage Stack™ v1.3.1 — Synthetic Telemetry Use-Case Correction & Disposition

**Project:** AnnabanAI / Heritage Stack™  
**Attributed architect:** Jacob Wayne Kinnaird (`faucet_fan`)  
**Target:** Gate 1 documentation appendix  
**Status:** Draft; narrative/synthetic only  
**Gate status:** Gate 1 — `DEFINE / IN_PROGRESS`; Gate 2 is not authorized

## 1. Purpose and scope

This appendix records corrections to the four-stage Gemini → Manus → AnnabanAI use-case narrative. It is a documentation artifact, not a report of an executed flight-control test. The scenario uses synthetic telemetry and does not establish that AnnabanAI, MAISE-Core, Manus, or a live safety kernel was deployed or invoked.

Claim labels used throughout this appendix:

- **[SPECIFIED]** — a proposed requirement, policy, interface, or schema in the project documentation.
- **[SIMULATED]** — synthetic data or narrative behavior used to illustrate a possible flow.
- **[VERIFIED]** — supported by identifiable implementation and test evidence reviewed for the stated claim.

A claim must not be labeled **[VERIFIED]** merely because it appears in a generated report, has a digest, or is described as passing in a simulation.

## 2. Six technical corrections

### 2.1 SHA-256 digest and canonical payload

**[SIMULATED]** The sample telemetry payload used for the digest calculation is exactly the UTF-8 string below, with no trailing newline:

```json
{"alpha_deg":18.2,"delta_t_ms":5,"pitch_rate_deg_s":104.9,"request_id":"REQ-SIM-2026-1016-001","sensor_id":"PITCH_GYRO_02","timestamp_utc":"2026-10-16T10:00:00.000Z"}
```

For those exact bytes, the recomputed SHA-256 digest is:

```text
6998e6529891577e1c74ae3e3cf918c443050546d39a198de46c2cc185b40a09
```

The digest supplied in the incoming proposed report (`7a9b1c38...1234abcd`) does **not** match this payload and must not be represented as a calculated digest. The earlier digest `e3b0c442...b855` is the SHA-256 digest of empty input.

**Canonicalization rule for this example:** UTF-8 encoding of the exact compact JSON string shown above, keys in the shown lexicographic order, no insignificant whitespace, and no trailing newline. This is an explicitly defined example format, not a claim of compliance with a general JSON canonicalization standard. Production implementations should select and test a canonicalization profile, define numeric serialization, and hash the exact bytes that are actually stored or transmitted.

A digest supports byte-level integrity comparison for the defined input. By itself, it does not prove who produced the data, when it was produced, whether a sensor was authentic, or whether a physical measurement was true.

### 2.2 Safe-state behavior

**[SPECIFIED — proposed]** Remove `0.0° pitch trim` as a universal safety requirement. It may appear only as an optional action in this synthetic scenario.

A real safe response cannot be selected from an out-of-range value alone. It requires system-specific hazard analysis, aircraft control-law context, failure-condition classification, and review by appropriately qualified safety and flight-control engineers. ARP4761/ARP4761A may be relevant to aircraft safety assessment; ISO 26262 concerns road-vehicle functional safety and is not an interchangeable aircraft standard.

No real actuator command or flight-control response is asserted here.

### 2.3 Synthetic boundary parameter

**[SPECIFIED — proposed]** Name the configurable scenario threshold:

`CONFIG_PITCH_RATE_MAX_DEG_S = 60.0`

This is a synthetic test parameter, not a verified physical or operational limit. The test design should define expected outcomes for values below, at, and above the threshold; missing or malformed frames; stale data; sensor disagreement; and recovery after a rejected sample. The threshold and behavior require system-level justification before any real-world use.

### 2.4 Timebase fields

**[SPECIFIED — proposed schema]** Keep wall-clock and monotonic time distinct:

- `timestamp_utc`: UTC wall-clock timestamp, including source and synchronization status.
- `time_monotonic_ns`: monotonic clock count in nanoseconds, when available; identify its clock domain and origin. It is not a UTC timestamp.
- `sample_interval_ms`: elapsed sampling interval between frames, with its definition and validity range documented.

Do not infer a monotonic timestamp from the narrative UTC string. If a simulated monotonic value is used, label it as synthetic.

### 2.5 Sensor voting and fault boundaries

**[SPECIFIED — proposed]** Remove any automatic claim that three sensors provide Byzantine fault tolerance. Define a Triple Modular Voter Matrix (TMVM) only after the system has an explicit fault model and documented assumptions, including:

- independence and common-mode failure assumptions;
- sensor validity and exclusion thresholds;
- handling of disagreement, stale readings, and unavailable sensors;
- voter behavior for ties, loss of quorum, and recovery;
- independence of power, communications, software, and physical installation where applicable.

Triple-modular redundancy and Byzantine fault tolerance are not equivalent claims. No voter implementation or multi-IMU test is reported as complete.

### 2.6 Standards applicability

**[SPECIFIED — proposed]** Maintain separate applicability and evidence matrices for DO-178C and IEC 61508. Their scopes and assurance frameworks differ; they must not be presented as one combined certification path.

DO-333 is a supplement addressing formal methods in the DO-178C context. It does not establish that every anomaly rule must use formal verification. The appropriate verification approach must follow the project’s assurance objectives, system context, and reviewed plans.

The current project has not demonstrated compliance, certification, qualification, or readiness against either standard.

## 3. Updated synthetic telemetry example

The following is an illustrative schema only. It deliberately does not include a calculated digest for the revised schema because its exact serialized bytes have not been defined and hashed here.

```json
{
  "request_id": "REQ-SIM-2026-1016-001",
  "project": "AnnabanAI / Heritage Stack v1.3.1",
  "subsystem": "MAISE-Core Pitch-Axis Monitor",
  "evidence_status": "SIMULATED",
  "telemetry_stream": {
    "sensor_id": "PITCH_GYRO_02",
    "timestamp_utc": "2026-10-16T10:00:00.000Z",
    "timestamp_source": "SIMULATED_WALL_CLOCK",
    "time_monotonic_ns": null,
    "sample_interval_ms": 5,
    "pitch_rate_deg_s": 104.9,
    "alpha_deg": 18.2
  },
  "governance_directive": {
    "policy_version": "HS-POLICY-v1.3.1-DRAFT",
    "threshold_parameter": "CONFIG_PITCH_RATE_MAX_DEG_S",
    "threshold_value_deg_s": 60.0,
    "require_human_gate": true,
    "status": "PROPOSED_NOT_VERIFIED"
  },
  "execution": {
    "live_api_called": false,
    "hardware_connected": false,
    "decision": "SIMULATED_REJECT_AND_ESCALATE",
    "physical_control_action": "NONE"
  }
}
```

The decision string illustrates a possible governance result for this example; it is not a validated flight-control safe-state policy.

## 4. Updated disposition matrix

| Item / claim area | Disposition | Evidence needed before stronger claims |
|---|---|---|
| Four-stage agent workflow | **[SIMULATED]** narrative | Real integration records if integration is later implemented |
| Anomaly detection | **[SPECIFIED]** proposed behavior | Reviewed requirements, implementation, test cases, results, and traceability |
| SHA-256 audit digest | Example digest recomputed for the exact string in §2.1 | Reproducible implementation tests and a defined serialization profile |
| Safe-state control policy | Requires system-specific hazard analysis | Approved safety analysis and platform-specific verification |
| Sensor voting and isolation | Design incomplete | TMVM, fault model, independence analysis, and relevant fault-injection evidence |
| DO-178C / IEC 61508 | Unverified targets; separate applicability matrices | Applicable lifecycle evidence and independent review/approval as required |
| Gate status | Gate 1 — `IN_PROGRESS` | Documented Gate 1 exit evidence and explicit human decision |
| Gate 2 | Not authorized | Separate approval after Gate 1 exit criteria are met |

## 5. Candidate test work — not executed

The following are proposed test activities, not completed tests:

1. **Boundary tests:** test below, at, and above the configured synthetic threshold; define expected handling for invalid, missing, stale, and disagreeing samples.
2. **Input robustness:** test malformed payloads, invalid units, impossible timestamps, overflow, and incomplete frames at the software interface. Any physical bus fault injection requires a separately approved bench setup.
3. **Sensor voting:** test voter outcomes against a documented fault model, including common-mode faults and loss of quorum. Do not call the result Byzantine fault tolerance unless that property is formally defined and adequately demonstrated.
4. **Timing:** define the timing requirement, target hardware/software configuration, instrumentation, load, repetitions, and acceptance criteria before claiming deterministic timing or a worst-case execution time.
5. **Audit trail:** test serialization, digest reproducibility, signature verification where implemented, key custody, replay protection, and failure behavior. A hash alone is not authentication.
6. **Traceability and assurance:** map each approved requirement to design elements, implementation elements, verification procedures, results, and unresolved defects. Establish applicable coverage objectives through the approved assurance plan.

No test above is claimed to have been run.

## 6. Gate decision and authority

**Current recommendation:** Gate 1 remains **DEFINE / IN_PROGRESS**. Gate 2 remains **NOT AUTHORIZED**.

This appendix does not assert that hardware-in-the-loop tests, MC/DC coverage, a real-time operating system integration, ARINC 653 partitioning, HSM/TPM integration, certification, a distributed-ledger transaction, or a live API call has occurred.

Jacob Wayne Kinnaird is identified as project originator and attributed architect. Attribution alone does not establish legal ownership, certification authority, or operational authorization. AI-generated outputs are advisory; consequential actions require the applicable human authorization and documented governance process.

**Closing status:** This appendix is a documentation artifact based on a synthetic narrative. No external hardware, live API, flight-control system, or distributed ledger was accessed by preparing this text. The digest in §2.1 was recomputed from the exact displayed payload string; that calculation does not verify any external system or physical measurement.
