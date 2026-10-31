# Annaban Retrieval API — Local Test Report

**Record ID:** ANNABAN-API-TEST-REPORT-001  
**Report status:** LOCAL TESTS PASSED; PRODUCTION READINESS NOT ESTABLISHED  
**Test date:** 2026-10-31  
**Classification:** Engineering test report for a prototype  
**Repository target:** `fanfaucet/AnnabanAI`  
**Branch:** `annaban/retrieval-api-test-report`

## 1. Scope and environment

The prototype was run in an isolated Python environment available to ChatGPT, not on Jacob Wayne Kinnaird's device, not in a production environment, and not against any external Annaban service. This report records actual tests run in that environment; it is not a hypothetical pass claim.

Environment observed:

- Python 3.13.5
- FastAPI 0.128.2
- Pydantic 2.13.5
- Starlette 0.50.0
- pytest 9.0.2
- HTTPX 0.28.1

The implementation uses in-memory dictionaries for records and audit events. It is a prototype and loses data when the process restarts.

## 2. Results summary

| Check | Result | Evidence |
|---|---|---|
| Unit/integration tests | **11 passed, 0 failed** | `pytest -q`: `11 passed in 0.35s` |
| Python compilation | **Passed** | `python -m compileall -q app.py test_app.py` exited successfully |
| Missing-token startup guard | **Passed** | Import without `ANNABAN_API_TOKEN` exited non-zero with the expected `RuntimeError` |
| Live local health endpoint | **Passed** | Uvicorn served `/health` with HTTP 200 and `{"status":"ok","service":"annaban-retrieval-api","version":"0.1.0"}` |
| Live local protected endpoint | **Passed** | Unauthenticated `GET /api/v1/records` returned HTTP 401 |
| External deployment / Codex runtime | **Not tested** | No deployment or Codex runtime was invoked |

## 3. Test cases

| # | Test | Expected behavior | Observed result |
|---:|---|---|---|
| 1 | Health endpoint | Returns status `ok` without authentication | PASS |
| 2 | Missing authentication | Returns 401 | PASS |
| 3 | Create and retrieve record | Returns 201, initial lifecycle `PROPOSED`, revision 1, source verification remains false | PASS |
| 4 | Duplicate record ID | Returns 409 | PASS |
| 5 | Unknown record ID | Returns 404 | PASS |
| 6 | Passed tests exceed tests run | Returns 422 | PASS |
| 7 | Client attempts to set validation status to `VERIFIED` | Rejected with 422 | PASS |
| 8 | Client attempts to set lifecycle to `DEPLOYED` | Rejected with 422 | PASS |
| 9 | Search for a matching record | Returns matching record and unverified status | PASS |
| 10 | Pagination limit exceeds maximum | Returns 422 | PASS |
| 11 | Audit endpoint after record creation | Returns a `RECORD_CREATED` event | PASS |

## 4. Interpretation

The tested prototype satisfies the 11 listed acceptance checks. It also fails closed at startup if the API token is missing and rejects unauthenticated access to protected routes.

These results establish only the tested behavior of this prototype in the stated environment. They do not establish security certification, production readiness, multi-user authorization, durable auditability, source authenticity, cryptographic integrity, scalability, or independent verification of record content.

## 5. Known limitations and required follow-up

1. **In-memory storage:** records and audit events are lost at restart. Use a transactional persistent database before deployment.
2. **Audit immutability:** the event list is not a tamper-evident ledger. Add append-only persistence, hash chaining or signatures, and verification tests.
3. **Authentication and authorization:** the bearer token is a single shared secret. Add managed secret handling, rotation, per-user identity, project-scoped access, and rate limiting.
4. **Review workflow:** client submissions cannot self-mark `VERIFIED` or `DEPLOYED`, but a trusted review service and authorized reviewer workflow are not implemented yet.
5. **Search:** current search is basic case-insensitive substring matching, not semantic or relevance-ranked retrieval.
6. **Source validation:** `source_verified` is a declared field and is not independently verified by this prototype. Treat it as untrusted input until evidence is checked.
7. **Operational controls:** add structured logs, request-size limits, observability, backup/restore tests, dependency scanning, and production server configuration.
8. **Coverage:** 11 tests passed, but this is a small acceptance suite, not exhaustive security, concurrency, fuzz, load, or resilience testing.

## 6. Reproduction

Install dependencies and set a test token:

```bash
python -m pip install -r requirements.txt
export ANNABAN_API_TOKEN='replace-with-a-strong-secret'
pytest -q
python -m compileall -q app.py test_app.py
uvicorn app:app --host 127.0.0.1 --port 8000
```

Then verify health:

```bash
curl -i http://127.0.0.1:8000/health
```

Verify that a protected route rejects missing credentials:

```bash
curl -i http://127.0.0.1:8000/api/v1/records
```

Expected protected-route status: `401 Unauthorized`.

## 7. Provenance and status

- **Artifact:** Annaban Retrieval API prototype and its local acceptance tests.
- **Test method:** pytest/TestClient, Python compilation, and a local Uvicorn/HTTP smoke test.
- **Evidence:** test command output and HTTP responses observed during this run.
- **Not established:** production deployment, Codex-side execution, third-party audit, external source verification, or legal ownership.
- **Attribution:** This report concerns the AnnabanAI project context associated with Jacob Wayne Kinnaird; attribution does not independently establish legal ownership.

**Final disposition:** `LOCAL_ACCEPTANCE_TESTS_PASS / PRODUCTION_READINESS_NOT_ESTABLISHED`
