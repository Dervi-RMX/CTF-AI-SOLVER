"""
Unit tests for Cybersecurity Study Mentor in CTF-AI Solver Pro.
"""

from pathlib import Path
import tempfile
from unittest.mock import MagicMock
import unittest

from ctf_ai.mentor.interview import StudentProfile
from ctf_ai.mentor.resources import ResourceCatalog, VERIFIED_RESOURCES
from ctf_ai.mentor.roadmap import RoadmapGenerator, LearningPath
from ctf_ai.mentor.planner import StudyPlanner
from ctf_ai.mentor.tutor import SocraticTutor


class TestMentor(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_student_profile_persistence(self):
        profile = StudentProfile(
            level="Principiante",
            target_role="Pentester / Seguridad Ofensiva",
            weekly_hours=6,
            budget_mode="100% Gratuito",
            background="Linux básico y redes",
        )
        save_file = str(Path(self.tmp_dir.name) / "test_profile.json")
        self.assertTrue(profile.save_to_file(save_file))

        loaded = StudentProfile.load_from_file(save_file)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.weekly_hours, 6)
        self.assertEqual(loaded.level, "Principiante")
        self.assertEqual(loaded.target_role, "Pentester / Seguridad Ofensiva")

    def test_resource_catalog(self):
        catalog = ResourceCatalog()
        # Test free resources existence
        free_resources = catalog.filter_permanently_free()
        self.assertGreater(len(free_resources), 0)
        # Check verified platforms exist
        names = [r.name for r in catalog.resources]
        self.assertTrue(any("PortSwigger" in n for n in names))
        self.assertTrue(any("TryHackMe" in n for n in names))
        self.assertTrue(any("OverTheWire" in n for n in names))

        # Check skill search
        web_resources = catalog.search_by_skill("SQL Injection")
        self.assertGreater(len(web_resources), 0)

    def test_roadmap_generator_tracks(self):
        gen = RoadmapGenerator()
        profile_pentest = StudentProfile(
            level="Principiante",
            target_role="Pentester / Seguridad Ofensiva",
            weekly_hours=5,
        )
        path = gen.generate_for_profile(profile_pentest)
        self.assertIsInstance(path, LearningPath)
        self.assertGreater(len(path.modules), 0)
        self.assertIn("Pentester", path.role)

        # Reversing track
        profile_rev = StudentProfile(
            level="Intermedio",
            target_role="Ingeniería Inversa y Malware",
            weekly_hours=8,
        )
        path_rev = gen.generate_for_profile(profile_rev)
        self.assertIn("Ingeniería Inversa", path_rev.role)

    def test_study_planner_recalibration(self):
        gen = RoadmapGenerator()
        profile = StudentProfile(level="Principiante", weekly_hours=10)
        learning_path = gen.generate_for_profile(profile)

        sched_file = str(Path(self.tmp_dir.name) / "sched.json")
        planner = StudyPlanner(learning_path=learning_path, storage_path=sched_file)

        # Recalibrate down to 4 hours
        res = planner.recalibrate_weekly_hours(4)
        self.assertEqual(res["status"], "RECALIBRADO_EXITOSO")
        self.assertEqual(planner.learning_path.weekly_hours, 4)
        self.assertEqual(planner.learning_path.modules[0].estimated_hours, 4)

        # Mark module completed
        self.assertTrue(planner.mark_module_completed(1))
        self.assertTrue(planner.learning_path.modules[0].completed)

    def test_socratic_tutor(self):
        mock_router = MagicMock()
        mock_router.ask.return_value = "Pista nivel 1: Presta atención a los formatos de compresión."

        tutor = SocraticTutor(mock_router)
        hint = tutor.give_hint("Reto forense con archivo ZIP", hint_level=1)
        self.assertIn("Pista nivel 1", hint)
        mock_router.ask.assert_called_once()


if __name__ == "__main__":
    unittest.main()
