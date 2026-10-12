"""
Unit tests for Core Engine, Evidence Inventory, and Operational Planner in CTF-AI Solver Pro.
"""

from unittest.mock import MagicMock
import unittest

from ctf_ai.core.evidence import EvidenceInventory, EvidenceItem, EvidenceType
from ctf_ai.core.planner import OperationalPlanner, Task, TaskStatus
from ctf_ai.core.engine import AutonomousCTFEngine
from ctf_ai.tools.base import registry


class TestCoreEngine(unittest.TestCase):

    def setUp(self):
        self.evidence = EvidenceInventory()
        self.planner = OperationalPlanner(max_iterations=5)

    def test_evidence_inventory_classification(self):
        # 1. Hypothesis
        h = self.evidence.add(
            evidence_type=EvidenceType.HYPOTHESIS,
            description="The file might be a corrupted PNG header",
            confidence=0.4,
        )
        self.assertEqual(h.evidence_type, EvidenceType.HYPOTHESIS)
        self.assertEqual(len(self.evidence.get_by_type(EvidenceType.HYPOTHESIS)), 1)

        # 2. Observed fact
        fact = self.evidence.add(
            evidence_type=EvidenceType.OBSERVED_FACT,
            description="Found string CTF{mock_flag_123}",
            source="deep_strings",
            confidence=0.9,
        )
        self.assertEqual(fact.evidence_type, EvidenceType.OBSERVED_FACT)

        # 3. Candidate flag
        flag_item = self.evidence.add_candidate_flag("CTF{mock_flag_123}", source="deep_strings")
        self.assertIsNotNone(flag_item)
        self.assertEqual(flag_item.evidence_type, EvidenceType.CANDIDATE_FLAG)

        # Verify candidate flag
        verified = self.evidence.verify_flag("CTF{mock_flag_123}", corroborating_fact="Confirmed in memory dump")
        self.assertTrue(verified)
        self.assertEqual(self.evidence.get_verified_flag(), "CTF{mock_flag_123}")

    def test_evidence_serialization(self):
        self.evidence.add(
            evidence_type=EvidenceType.OBSERVED_FACT,
            description="Serial test",
            confidence=0.8,
        )
        data = self.evidence.to_list()
        self.assertEqual(len(data), 1)

        new_inv = EvidenceInventory.from_list(data)
        self.assertEqual(len(new_inv.items), 1)
        self.assertEqual(new_inv.items[0].description, "Serial test")

    def test_planner_task_lifecycle_and_priority(self):
        t1 = self.planner.add_task(
            title="Inspect Headers",
            tool_name="magic_inspector",
            priority=8,
        )
        t2 = self.planner.add_task(
            title="Bruteforce PIN",
            priority=2,
        )

        # Next pending task should be t1 due to higher priority (8 > 2)
        next_t = self.planner.get_next_pending_task()
        self.assertIsNotNone(next_t)
        self.assertEqual(next_t.id, t1.id)

        # Mark t1 as running then completed
        t1.status = TaskStatus.RUNNING
        self.planner.complete_task(t1.id, result="Valid PNG header found")
        self.assertEqual(t1.status, TaskStatus.SUCCESS)

        # Next task should now be t2
        next_t2 = self.planner.get_next_pending_task()
        self.assertIsNotNone(next_t2)
        self.assertEqual(next_t2.id, t2.id)

    def test_planner_replanning_on_failure(self):
        t_fail = self.planner.add_task(
            title="Extract non-existent key",
            tool_name="rsa_math",
            priority=9,
        )
        self.planner.fail_task(t_fail.id, error_reason="Factorization timed out")
        self.assertEqual(t_fail.status, TaskStatus.FAILED)

        # Replan should generate alternative tasks
        new_tasks = self.planner.replan_on_failure(t_fail)
        self.assertGreater(len(new_tasks), 0)

    def test_engine_initialization_and_step(self):
        mock_router = MagicMock()
        mock_router.ask.return_value = "Categoría: Criptografía\nDificultad: Fácil\nHipótesis: Es una sustitución básica\nTarea: multi_decoder"

        engine = AutonomousCTFEngine(
            ai_router=mock_router,
            challenge_id="unit_test_chal",
            max_iterations=3,
            tool_registry=registry,
        )

        init_res = engine.initialize_challenge("El reto contiene ciphertext 'Q1RGe2F1dG9fdGVzdH0='")
        self.assertIn("category", init_res)
        self.assertEqual(init_res["category"], "Criptografía")
        self.assertGreater(len(engine.planner.tasks), 0)

        # Add a task that can be executed by registered tool
        task = engine.planner.add_task(
            title="Decode base64 string",
            tool_name="multi_decoder",
            tool_args={"data": "Q1RGe2F1dG9fdGVzdH0="},
            priority=10,
        )

        step_res = engine.step()
        self.assertEqual(step_res["status"], "PASO_EJECUTADO")
        self.assertEqual(step_res["task"], task.title)
        # Check that candidate flag was found and verified
        self.assertIn("CTF{auto_test}", str(engine.evidence.to_list()))


if __name__ == "__main__":
    unittest.main()
