"""
Unit and simulation tests for response_calibration module.
Authored under Jacob Wayne Kinnaird · AnnabanAI
"""

import unittest
from response_calibration import (
    ResponseCalibrationPolicy,
    ResponseCalibrationEngine,
    AuthorityMode,
    run_simulation_suite,
)


class TestResponseCalibrationPolicy(unittest.TestCase):
    def test_default_policy(self):
        policy = ResponseCalibrationPolicy()
        self.assertEqual(policy.objective, "Preserve user intent while improving responsiveness")
        self.assertEqual(policy.authority.mode, AuthorityMode.ADVISORY)
        self.assertEqual(policy.authority.external_effects, 0)
        self.assertTrue(policy.authority.human_authorization_required)
        self.assertEqual(policy.authored_by, "Jacob Wayne Kinnaird")

    def test_fingerprint_stable(self):
        """Identical policy content must produce identical fingerprints."""
        p1 = ResponseCalibrationPolicy()
        p2 = ResponseCalibrationPolicy()
        self.assertEqual(p1.fingerprint(), p2.fingerprint())
        self.assertEqual(len(p1.fingerprint()), 64)
        self.assertIn("response_calibration", p1.to_yaml_like())


class TestResponseCalibrationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ResponseCalibrationEngine()

    def test_intent_clarity_action(self):
        clear, action = self.engine.evaluate_intent_clarity(
            "Molly, leave the delegates' meeting with me now.", {}
        )
        self.assertTrue(clear)
        self.assertEqual(action, "advance_scene")

    def test_frustration_signal(self):
        clear, action = self.engine.evaluate_intent_clarity(
            "That's not what I meant. Just move the scene.", {}
        )
        self.assertTrue(clear)
        self.assertEqual(action, "change_behavior_immediately")

    def test_authorization_gate(self):
        self.assertFalse(self.engine.is_authorized())
        # Reject weak tokens
        self.assertFalse(self.engine.authorize("short"))
        self.assertFalse(self.engine.authorize("no-prefix-but-long-enough-token-123456"))
        # Accept correctly structured token
        valid = "ANNABAN-AUTH-2026-kinnaird-001"
        self.assertTrue(self.engine.authorize(valid))
        self.assertTrue(self.engine.is_authorized())

    def test_advisory_guidance(self):
        guidance = self.engine.generate_advisory_guidance(
            "Have her stand and leave with him."
        )
        self.assertTrue(guidance["advisory"])
        self.assertEqual(guidance["external_effects"], 0)
        self.assertEqual(guidance["authority_mode"], "ADVISORY")


class TestSimulationSuite(unittest.TestCase):
    def test_simulation_passes(self):
        result = run_simulation_suite()
        self.assertTrue(result["simulation_pass"])
        self.assertIn("intent_following_rate", result)
        self.assertEqual(result["external_effects"], 0)
        self.assertTrue(result["scenario_results"]["repeated_clarification_detected"])
        self.assertTrue(result["scenario_results"]["recovery_after_feedback"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
