import json
import tempfile
import unittest
import warnings
from pathlib import Path

from modules.lattice_metrics import LatticeMetrics


class LatticeMetricsTests(unittest.TestCase):
    def test_registry_counts_and_activity(self):
        with tempfile.TemporaryDirectory() as tmp:
            metrics = LatticeMetrics(Path(tmp) / "history.json", seed=1)
            metrics.register_agent("a", "task", True)
            metrics.register_agent("b", "task", False)
            metrics.register_agent("c", "governance", True)
            counts = metrics.get_agent_counts()
            self.assertEqual((counts.total, counts.active), (3, 2))
            self.assertEqual(counts.by_role, {"task": 2, "governance": 1})
            report = metrics.simulate()
            self.assertEqual(report.agent_counts.total, 3)
            self.assertEqual(
                report.metric_source,
                "mixed: registry counts + synthetic quality metrics",
            )

    def test_simulated_roles_reconcile_to_total(self):
        with tempfile.TemporaryDirectory() as tmp:
            metrics = LatticeMetrics(Path(tmp) / "history.json", seed=2)
            report = metrics.simulate(use_real_agents=False)
            self.assertEqual(
                sum(report.agent_counts.by_role.values()),
                report.agent_counts.total,
            )

    def test_history_round_trip_and_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            metrics = LatticeMetrics(path, seed=3, max_history=2)
            for _ in range(3):
                metrics.simulate(use_real_agents=False)
            self.assertEqual(len(metrics.history), 2)
            reloaded = LatticeMetrics(path, seed=3, max_history=2)
            self.assertEqual(len(reloaded.history), 2)
            self.assertEqual(reloaded.history[-1].metric_source, "synthetic")

    def test_corrupt_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "history.json"
            path.write_text("{bad json", encoding="utf-8")
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                LatticeMetrics(path)
            self.assertEqual(path.read_text(encoding="utf-8"), "{bad json")
            self.assertTrue(caught)

    def test_invalid_max_history_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                LatticeMetrics(Path(tmp) / "history.json", max_history=0)

    def test_unknown_agent_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            metrics = LatticeMetrics(Path(tmp) / "history.json")
            with self.assertRaises(KeyError):
                metrics.set_agent_active("missing", True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
