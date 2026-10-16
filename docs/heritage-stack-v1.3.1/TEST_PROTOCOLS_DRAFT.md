# Heritage Stack™ v1.3.1 — Draft Test Protocols

**Status:** Draft templates only. Do not use for formal qualification until reviewed and approved by qualified personnel and the selected laboratory.

## TP-THERMAL-01 — Thermal protection screening

### Objective
Determine whether the specified sensor location remains at or below 70.0°C throughout a defined thermal exposure and whether the assembly remains functional afterward.

### Preconditions to approval
- Identify what the proposed 720°C value represents; it is not a substitute for heat-flux measurement.
- Define incident heat flux, exposure duration, specimen geometry, materials, edge conditions, mounting, sensor position, and thermal boundary conditions.
- Specify calibrated measurement devices, calibration status, uncertainty, sampling rate, and sensor attachment method.
- Define the required number of specimens and repeat runs.
- Establish safety limits and stop conditions with the laboratory.

### Procedure outline
1. Record specimen ID, revision, build history, photographs, and instrumentation.
2. Measure baseline function and sensor readings.
3. Verify calibration and record ambient conditions.
4. Apply the approved exposure profile and continuously log temperatures and applied conditions.
5. Stop safely if any pre-defined safety or equipment limit is exceeded.
6. Record anomalies and all deviations.
7. Inspect and function-test the specimen after exposure.
8. Preserve raw data, calibration records, setup photos, test configuration, and signed report.

### Proposed pass/fail rule
The designated internal sensor location must not exceed 70.0°C at any point in the defined exposure, accounting for agreed measurement uncertainty. Post-exposure function must meet separately approved criteria. Final acceptance rule pending laboratory and engineering review.

## TP-MECH-01 — Steady acceleration

### Objective
Evaluate structural integrity and electrical continuity during a defined steady 10G acceleration test.

### Preconditions to approval
Define the applicable standard and edition, test fixture, assembly orientation, three orthogonal axes, acceleration ramp, five-minute dwell per axis, instrumentation, continuity tolerance, number of specimens, and safety limits.

### Procedure outline
1. Record assembly identity, revision, baseline inspection, dimensions, photographs, and electrical resistance.
2. Verify fixture and instrumentation calibration.
3. Apply the approved acceleration profile in each specified orientation.
4. Record acceleration and continuity throughout the test where feasible.
5. Inspect for fractures, displacement, loosening, and other defined failures.
6. Repeat electrical measurements using the same documented method.
7. Archive raw data, calibration records, photos, deviations, and signed report.

### Proposed pass/fail rule
No defined structural failure; electrical continuity remains within the approved tolerance of baseline. The proposed ±2% resistance tolerance requires engineering approval and confirmation that the measurement setup can resolve it.

## TP-MECH-02 — Random vibration (separate test)

This is not the 10G acceleration test. Before execution, define the mounting location, justified platform-specific PSD, frequency bands, duration, axes, fixture, control/response accelerometers, functional monitoring, inspection criteria, and laboratory report requirements. A generic 20–2000 Hz range alone is insufficient.

## TP-SOFT-01 — Software and policy verification

### Objective
Verify that schema, hash, signature, authorization, and gate-transition controls behave as specified.

### Required test groups
- Schema: valid payloads accepted; malformed or incompatible payloads rejected.
- Attestation: missing, invalid, expired, revoked, or untrusted signatures rejected.
- Integrity: independently recompute hashes from documented canonical bytes.
- Replay: duplicate, stale, or out-of-sequence requests handled according to the specification.
- Authorization: consequential mutations freeze when required authorization is absent or invalid.
- Recovery: frozen execution resumes only through the explicitly approved recovery path.
- Audit: decision, evidence references, policy version, and human authorization are recorded.

### Evidence
Versioned test fixtures, code and policy revision, tool versions, reproducible command, raw test output, coverage report, and reviewer sign-off. A successful hash comparison does not establish physical sensor accuracy or source authenticity by itself.

## Approval status

All protocols are **drafts**. They must be reviewed, made specific to the actual device and intended environment, assigned owners, and approved before formal testing. No test is claimed completed.
