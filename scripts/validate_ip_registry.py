#!/usr/bin/env python3
"""Validate the AnnabanAI IP evidence registry using only the Python standard library.

This tool validates structure and evidence-status discipline. It does not contact
USPTO, WIPO, NASA, SEC, Copyright Office, or other registries.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ALLOWED_STATUSES = {
    "VERIFIED_MATCH",
    "MISMATCH_FOUND",
    "PENDING_DIRECT_LOOKUP",
    "UNVERIFIED_ASSERTION",
    "UNVERIFIED_VALUATION_ASSERTION",
    "UNVERIFIED_LEGAL_ASSERTION",
    "PENDING_LICENSE_TEXT_REVIEW",
    "UNVERIFIED_CRYPTOGRAPHIC_ASSERTION",
    "UNVERIFIED_TECHNICAL_AND_LEGAL_ASSERTION",
}
COLLECTIONS = (
    "patents", "copyrights", "trademarks", "government_claims",
    "corporate_integrations", "software_and_trade_secrets",
    "other_claims", "valuation_components",
)

def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]
    for key in ("registry_id", "project_attribution", "source_document", "audit_baseline"):
        if not data.get(key):
            errors.append(f"missing required root field: {key}")
    if data.get("project_attribution") != "Jacob Wayne Kinnaird":
        errors.append("project_attribution must preserve the full name 'Jacob Wayne Kinnaird'")
    valuation = data.get("portfolio_value", {})
    if valuation.get("source_claim") != "$6.692T":
        errors.append("source valuation must preserve the supplied '$6.692T' value")
    if valuation.get("status") != "UNVERIFIED_VALUATION_ASSERTION":
        errors.append("portfolio valuation must remain explicitly unverified")
    if not data.get("guardrails"):
        errors.append("guardrails must be present")
    for collection_name in COLLECTIONS:
        collection = data.get(collection_name, [])
        if not isinstance(collection, list):
            errors.append(f"{collection_name} must be a list")
            continue
        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                errors.append(f"{collection_name}[{index}] must be an object")
                continue
            status = item.get("audit_status")
            if status not in ALLOWED_STATUSES:
                errors.append(f"{collection_name}[{index}] has missing/unknown audit_status: {status!r}")
            if status == "VERIFIED_MATCH" and not (item.get("sources") or item.get("source")):
                errors.append(f"{collection_name}[{index}] claims VERIFIED_MATCH without a source field")
    if not isinstance(data.get("audit_trail"), list) or not data["audit_trail"]:
        errors.append("audit_trail must be a non-empty list")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", default="docs/evidence-audit/registry.json")
    args = parser.parse_args()
    path = Path(args.registry)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: unable to read valid JSON at {path}: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        print("REGISTRY VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    counts: dict[str, int] = {}
    for collection_name in COLLECTIONS:
        for item in data.get(collection_name, []):
            status = item.get("audit_status", "UNKNOWN")
            counts[status] = counts.get(status, 0) + 1
    print("REGISTRY VALIDATION PASSED")
    print(f"Registry: {data['registry_id']}")
    print(f"Portfolio value retained as unverified: {data['portfolio_value']['source_claim']}")
    print("Claim status counts:")
    for status, count in sorted(counts.items()):
        print(f"  {status}: {count}")
    print("NOTE: structural validation only; no live public-registry lookup was performed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
