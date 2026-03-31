import unittest

from annabanos_lite.kernel import AnnabanOSLiteKernel
from modules.jacob_node_module import JacobNodeModule


class JacobNodeModuleTests(unittest.TestCase):
    def test_jacob_node_state_updates_and_preserves_principal(self) -> None:
        kernel = AnnabanOSLiteKernel()
        module = JacobNodeModule(
            nasa_drawdown_usd=500_000.0,
            monthly_burn_rate_usd=100_000.0,
            ip_royalties_usd=120_000.0,
            passive_inflows_usd=90_000.0,
        )

        result = kernel.execute_module(module)
        jacob_node = kernel.shared_state["jacob_node"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(jacob_node["funding"]["award_id"], "NASA STMDA-AG-2026-007")
        self.assertEqual(jacob_node["funding"]["drawdown_usd"], 500_000.0)
        self.assertEqual(jacob_node["funding"]["drawdown_remaining_usd"], 2_100_000.0)
        self.assertTrue(jacob_node["liquidity"]["self_sustaining_threshold_reached"])
        self.assertFalse(jacob_node["signals"]["ftdt_principal_touched"])
        self.assertEqual(jacob_node["signals"]["allocation_mode"], "yield_signal_only")
        self.assertEqual(len(jacob_node["milestones"]), 2)
        self.assertIn("Self-sustaining threshold reached", jacob_node["alerts"][0])
        self.assertTrue(any("NASA drawdown" in entry for entry in jacob_node["logs"]))
        self.assertEqual(kernel.execution_log[-1].module_name, "jacob_node_module")


if __name__ == "__main__":
    unittest.main()
