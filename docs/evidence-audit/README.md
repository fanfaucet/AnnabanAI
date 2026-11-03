# IP Evidence Audit Registry

Project attribution: **Jacob Wayne Kinnaird**  
Registry ID: `JWK-IP-EVIDENCE-AUDIT-001`

## Files

- `registry.json`: source-preserving evidence registry. Original claims and valuations remain claims until supported by primary evidence.
- `scripts/validate_ip_registry.py`: standard-library validator for structure and status discipline.
- `tests/test_validate_ip_registry.py`: unit tests for core invariants.

## Run

From the repository root:

```bash
python scripts/validate_ip_registry.py
python -m unittest discover -s tests -p 'test_validate_ip_registry.py' -v
```

The validator does **not** perform network lookups. A passing result means the registry is structurally consistent, not that any patent, trademark, copyright, contract, government award, corporate integration, or valuation is verified.

## Status policy

- `VERIFIED_MATCH`: use only after recording a primary source and confirming material details.
- `MISMATCH_FOUND`: preserve the supplied claim and record the discrepancy; do not silently overwrite source data.
- `PENDING_DIRECT_LOOKUP`: authoritative verification is still needed.
- `UNVERIFIED_ASSERTION`: no supporting primary evidence is attached.
- `UNVERIFIED_VALUATION_ASSERTION`: preserve source value; do not describe it as an audited valuation.

## Evidence standards

Prefer official USPTO Patent Center/TSDR, WIPO PATENTSCOPE, U.S. Copyright Public Records System, NASA NTRS, SAM.gov, USAspending.gov, SEC EDGAR, signed contracts, assignments, and reproducible signature-verification output. A search miss is not proof of nonexistence. A hash proves byte integrity only when the compared bytes and trusted digest are known; it does not prove the truth of a claim.

The supplied portfolio value of **$6.692T** is intentionally preserved as an unverified source assertion.
