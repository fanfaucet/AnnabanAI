# Heritage Stack™ v1.3.1 — Risk Register

**Status:** Draft; owners and ratings require human review.  
**Lifecycle:** Gate 1 — DEFINE.

| ID | Risk | Initial rating | Owner | Mitigation / next action | Closure evidence |
|---|---|---|---|---|---|
| R-001 | Thermal model does not capture edge losses, thermal bridges, cavity effects, degradation, or actual heat-flux distribution | High | TBD | Define intended environment and specimen; review model assumptions; approve physical test protocol | Independent review plus complete physical test report and raw measurements |
| R-002 | A nominal 720°C source temperature is mistaken for a complete thermal exposure specification | High | TBD | Specify heat flux, geometry, exposure time, boundary conditions, sensor placement, and uncertainty | Approved TP-THERMAL-01 |
| R-003 | Steady acceleration, vibration, and shock are conflated | High | TBD | Maintain separate procedures and profiles; justify each profile against intended mounting/use | Approved mechanical test plan and separate results |
| R-004 | Hash equality is incorrectly treated as proof of source identity or measurement accuracy | High | TBD | Separate integrity, signature authenticity, sensor calibration, and physical validity claims | Security design review and test evidence |
| R-005 | Key compromise, revocation failure, replay, or canonicalization ambiguity permits unauthorized action | High | TBD | Specify key lifecycle, trusted roots, signed bytes, expiry, nonce/sequence, revocation and fail-closed behavior | Approved key-management plan and negative-path test report |
| R-006 | Single-key and dual-approval rules conflict or leave an undocumented override path | High | TBD | Define action classes, signer requirements, veto behavior, and recovery rules in PRD | Approved authorization table and tests |
| R-007 | Latency target is stated without a reproducible benchmark definition | Medium | TBD | Define hardware, load, payloads, persistence, network conditions, sample size and percentiles | Reproducible benchmark report |
| R-008 | AI-generated documents or simulation outputs are presented as completed implementation or independent verification | High | TBD | Require status labels and evidence links; separate proposed, implemented, tested and verified states | Review checklist and evidence manifest |
| R-009 | Funding target is mistaken for secured or disbursed capital | Medium | TBD | Label USD 250,000 as planning target until financial evidence supports a change | Dated funding evidence and approved ledger update |
| R-010 | Attribution is incorrectly treated as proof of legal ownership or patent rights | Medium | TBD | Record contributors, licenses, assignments and legal review separately | Counsel-reviewed IP and contribution records |
| R-011 | Standards are selected by name without checking edition, scope, applicability, or lab capability | High | TBD | Record exact edition, clauses, deviations, rationale and test-lab acceptance | Approved standards rationale |
| R-012 | Missing artifact or missing reviewer is treated as implicit approval | High | TBD | Default to no gate transition without a complete package and recorded human decision | Gate checklist and signed decision record |

## Risk acceptance

No risk owner, residual rating, or acceptance decision is inferred by this draft. The human project authority and designated technical reviewers must assign owners and decide whether residual risks are acceptable before Gate 1 closure.
