import json
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "evidence-audit" / "registry.json"
VALIDATOR = ROOT / "scripts" / "validate_ip_registry.py"
spec = importlib.util.spec_from_file_location("validate_ip_registry", VALIDATOR)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_registry_is_structurally_valid(self):
        self.assertEqual(module.validate(self.data), [])

    def test_source_valuation_is_preserved_and_unverified(self):
        self.assertEqual(self.data["portfolio_value"]["source_claim"], "$6.692T")
        self.assertEqual(self.data["portfolio_value"]["status"], "UNVERIFIED_VALUATION_ASSERTION")

    def test_no_claim_is_falsely_marked_verified(self):
        for collection in module.COLLECTIONS:
            for item in self.data.get(collection, []):
                self.assertNotEqual(item.get("audit_status"), "VERIFIED_MATCH")

    def test_bad_valuation_status_fails(self):
        altered = json.loads(json.dumps(self.data))
        altered["portfolio_value"]["status"] = "VERIFIED_MATCH"
        self.assertTrue(any("valuation must remain explicitly unverified" in e
                            for e in module.validate(altered)))

    def test_unknown_record_status_fails(self):
        altered = json.loads(json.dumps(self.data))
        altered["patents"][0]["audit_status"] = "ALL_CLEAR"
        self.assertTrue(any("unknown audit_status" in e for e in module.validate(altered)))

if __name__ == "__main__":
    unittest.main()
