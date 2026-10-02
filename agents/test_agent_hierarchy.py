import unittest

from agent_hierarchy import (
    AgentState,
    EnhancedBaseAgent,
    EmpathAgent,
    MemorySystem,
    SocialAgent,
    TaskAgent,
)


class AgentHierarchyTests(unittest.TestCase):
    def test_memory_add_recall_and_consolidation(self):
        memory = MemorySystem(capacity=2, short_term_limit=2)
        memory.add_memory("Annaban governance", source="test", importance=0.9)
        memory.add_memory("transport safety", source="test", importance=0.8)
        self.assertEqual(len(memory.short_term_memory), 0)
        self.assertEqual(len(memory.long_term_memory), 2)
        self.assertEqual(memory.recall("governance")[0].content, "Annaban governance")

    def test_base_agent_intent_reflection_and_safe_hold(self):
        agent = EnhancedBaseAgent("base-1")
        intent = agent.track_intent("research", 0.75)
        self.assertEqual(intent.confidence, 0.75)
        self.assertIn("research", agent.intents[0].name)
        self.assertTrue(agent.reflect("observe, verify, authorize"))
        agent.enter_safe_hold("missing human authorization")
        self.assertEqual(agent.state, AgentState.SAFE_HOLD)
        agent.resume()
        self.assertEqual(agent.state, AgentState.IDLE)

    def test_specialized_agents(self):
        empath = EmpathAgent("empath-1")
        self.assertTrue(empath.assess_context("I am excited about this")["cues"]["positive"])

        task = TaskAgent("task-1")
        queued = task.enqueue("run tests", priority=10)
        self.assertEqual(task.next_task().id, queued.id)
        self.assertTrue(task.complete(queued.id))
        self.assertEqual(queued.status, "completed")

        social = SocialAgent("social-1")
        relationship = social.interact("agent-2", trust_delta=0.1)
        self.assertAlmostEqual(relationship.trust, 0.6)
        self.assertEqual(relationship.interactions, 1)

    def test_snapshot_is_deterministic_in_shape(self):
        agent = EnhancedBaseAgent("snapshot-1", name="Test Agent")
        snapshot = agent.snapshot()
        self.assertEqual(snapshot["agent_id"], "snapshot-1")
        self.assertEqual(snapshot["state"], "idle")
        self.assertIn("memory", " ".join(snapshot.keys()))


if __name__ == "__main__":
    unittest.main()
