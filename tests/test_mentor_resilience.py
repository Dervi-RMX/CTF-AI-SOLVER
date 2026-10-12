"""
Pruebas de Resiliencia para Cybersecurity Study Mentor:
- Búsqueda en lenguaje natural en ResourceCatalog.
- Fallback offline de SocraticTutor ante errores de cuota (HTTP 429) o fallos de red.
- Extracción de horas semanales para recalibración.
"""

import unittest
from unittest.mock import MagicMock
import re
from ctf_ai.mentor.resources import ResourceCatalog
from ctf_ai.mentor.tutor import SocraticTutor


class TestMentorResilience(unittest.TestCase):
    def setUp(self):
        self.catalog = ResourceCatalog()

    def test_search_courses_natural_language_beginner(self):
        """Verifica que la búsqueda en lenguaje natural priorice cursos para principiantes."""
        results = self.catalog.search_courses("me gustaria cursos de ciberseguridad pa empezar")
        self.assertTrue(len(results) > 0)
        names = [r.name.lower() for r in results]
        has_intro = any("cisco" in n or "linux" in n or "tryhackme" in n or "bandit" in n for n in names)
        self.assertTrue(has_intro, f"No beginner course found in: {names}")

    def test_search_courses_web(self):
        """Verifica búsqueda por temática web."""
        results = self.catalog.search_courses("vulnerabilidades web owasp")
        self.assertTrue(len(results) > 0)
        names = [r.name.lower() for r in results]
        self.assertTrue(any("web security academy" in n for n in names))

    def test_search_courses_empty_returns_all(self):
        """Una búsqueda vacía devuelve la lista completa de recursos."""
        results = self.catalog.search_courses("")
        self.assertEqual(len(results), len(self.catalog.resources))

    def test_tutor_offline_fallback_on_429_quota(self):
        """Verifica que si la API de IA lanza 429 ResourceExhausted, tutor devuelva un drill offline."""
        mock_router = MagicMock()
        mock_router.ask.side_effect = Exception("429 Resource has been exhausted (e.g. check quota).")

        tutor = SocraticTutor(mock_router)
        response = tutor.generate_quiz_question("seguridad web")

        self.assertIn("A)", response)
        self.assertIn("B)", response)
        self.assertIn("Banco Offline", response)

    def test_tutor_normal_ai_response(self):
        """Verifica que si la IA responde normalmente, se devuelva su salida."""
        mock_router = MagicMock()
        mock_router.ask.return_value = "Pregunta: ¿Qué es XSS?\nA) Cross-Site Scripting\nB) XML Scripting"

        tutor = SocraticTutor(mock_router)
        response = tutor.generate_quiz_question("web")
        self.assertIn("¿Qué es XSS?", response)

    def test_plan_study_regex_extraction(self):
        """Verifica que la extracción numérica funcione con lenguaje natural."""
        test_inputs = [
            ("3", 3),
            ("que hago 3", 3),
            ("tengo 5 horas semanales", 5),
            ("10h", 10),
        ]
        for inp, expected in test_inputs:
            nums = re.findall(r"\d+", inp)
            self.assertTrue(bool(nums))
            self.assertEqual(int(nums[0]), expected)


if __name__ == "__main__":
    unittest.main()
