import unittest

from integrations.sourcery.annaban_sourcery_bridge import (
    EvidenceClass,
    ReviewFinding,
    ReviewRequest,
    build_review_envelope,
    normalize_finding,
)


class SourceryBridgeContractTests(unittest.TestCase):
    def setUp(self):
        self.request = ReviewRequest(
            repository="fanfaucet/AnnabanAI",
            pull_request=38,
            head_sha="d5350c00485677ff8f557e842dce078680d5ecbb",
            requested_by="Jacob Wayne Kinnaird",
        )

    def test_request_requires_human_gate_and_zero_external_effects(self):
        self.request.validate()
        with self.assertRaises(ValueError):
            ReviewRequest(
                repository="fanfaucet/AnnabanAI",
                pull_request=38,
                head_sha="abcdef123",
                requested_by="operator",
                external_effects=1,
            ).validate()

    def test_normalizer_preserves_missing_metadata_as_none(self):
        finding = normalize_finding({
            "title": "Possible edge case",
            "description": "A boundary condition may be unhandled.",
            "severity": "medium",
        })
        self.assertIsNone(finding.finding_id)
        self.assertIsNone(finding.file_path)
        self.assertIsNone(finding.line)
        self.assertEqual(finding.evidence_class, EvidenceClass.SOURCERY_REPORTED)

    def test_envelope_never_authorizes_mutations(self):
        finding = ReviewFinding(
            finding_id="F-1",
            title="Example finding",
            severity="LOW",
            message="Illustrative finding only.",
            file_path=None,
            line=None,
        )
        envelope = build_review_envelope(self.request, [finding])
        self.assertFalse(envelope["provider_connected"])
        self.assertFalse(envelope["provider_result_verified"])
        self.assertFalse(envelope["code_changes_authorized"])
        self.assertFalse(envelope["merge_authorized"])
        self.assertEqual(envelope["external_effects"], 0)
        self.assertEqual(envelope["findings"][0]["evidence_class"], "SOURCERY_REPORTED")


if __name__ == "__main__":
    unittest.main()
