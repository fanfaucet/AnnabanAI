"""Tests for the simulation-first AnnabanAI research prototype."""
import asyncio
import tempfile
import unittest
from pathlib import Path

from research.annaban_frontier_orchestrator import (
    DelegationRouter,
    NanoBananaInterface,
    ResponseIntegrator,
    SharedPortfolio,
    SimulationAgent,
    Task,
    TaskResult,
    TaskType,
    run_independent_tasks,
)


class OrchestratorTests(unittest.TestCase):
    def test_router_selects_capable_agent(self):
        agent = SimulationAgent("analysis", [TaskType.ANALYZE])
        router = DelegationRouter([agent])
        task = Task("a1", TaskType.ANALYZE, "test")
        self.assertIs(router.route(task), agent)

    def test_missing_dependency_rejected(self):
        router = DelegationRouter([SimulationAgent("analysis", [TaskType.ANALYZE])])
        task = Task("a1", TaskType.ANALYZE, "test", dependencies=("missing",))
        with self.assertRaisesRegex(ValueError, "unknown dependencies"):
            asyncio.run(run_independent_tasks([task], router))

    def test_dependency_scheduling_is_not_misrepresented(self):
        router = DelegationRouter([SimulationAgent("analysis", [TaskType.ANALYZE])])
        task = Task("a1", TaskType.ANALYZE, "test", dependencies=("a0",))
        with self.assertRaises(NotImplementedError):
            asyncio.run(run_independent_tasks([task], router))

    def test_creative_adapter_is_simulation_only(self):
        agent = NanoBananaInterface(api_key="placeholder")
        result = asyncio.run(agent.process(Task("v1", TaskType.CREATIVE, "visual test")))
        self.assertTrue(result.simulated)
        self.assertIn("no image bytes", " ".join(result.warnings).lower())

    def test_portfolio_record_preserves_governance_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "portfolio.jsonl"
            integrator = ResponseIntegrator(SharedPortfolio(path))
            record = integrator.integrate(
                "test request",
                [TaskResult("t1", "analyze", "simulated", "output", "test-agent")],
            )
            self.assertEqual(record["authority"], "ADVISORY_ONLY")
            self.assertEqual(record["external_effects"], 0)
            self.assertTrue(record["human_review_required"])
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
