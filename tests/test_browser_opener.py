"""
Pruebas Unitarias para el Comando 'open' y la Especialización de SOC / Blue Team
"""

import unittest
from unittest.mock import MagicMock, patch
from ctf_ai.mentor.resources import ResourceCatalog
from ctf_ai.mentor.advisor import MentorAdvisor
from ctf_ai.mentor.interview import StudentProfile


class TestBrowserOpenerAndSOC(unittest.TestCase):
    def setUp(self):
        self.catalog = ResourceCatalog()
        self.mock_router = MagicMock()
        self.advisor = MentorAdvisor(self.mock_router)
        self.profile = StudentProfile(
            target_role="Pentester / Seguridad Ofensiva",
            level="Principiante",
        )

    def test_search_courses_soc_blue_team(self):
        """Verifica que buscar 'soc' o 'blue team' devuelva recursos especializados de defensa."""
        results = self.catalog.search_courses("como empezar en soc")
        self.assertTrue(len(results) > 0)
        names = [r.name.lower() for r in results]
        has_soc = any("letsdefend" in n or "blue team" in n or "splunk" in n or "cyberdefenders" in n for n in names)
        self.assertTrue(has_soc, f"No se encontró recurso de SOC en: {names}")

    def test_offline_advice_soc_not_pentester(self):
        """Verifica que consultas offline sobre SOC devuelvan contenido de Blue Team, no de Pentesting."""
        advice = self.advisor.get_offline_advice("como empezar en soc", self.profile)
        self.assertIn("SOC", advice)
        self.assertIn("Blue Team", advice)
        self.assertIn("LetsDefend", advice)
        self.assertIn("SIEM", advice)

    def test_offline_advice_general_cybersecurity(self):
        """Verifica que consultas generales sobre inicio en ciberseguridad den visión equilibrada."""
        advice = self.advisor.get_offline_advice("como empezar en ciberseguridad", self.profile)
        self.assertIn("Fundamentos", advice)
        self.assertIn("Defensiva", advice)
        self.assertIn("Ofensiva", advice)

    @patch("webbrowser.open")
    def test_handle_open_command_logic(self, mock_web_open):
        """Simula la lógica del comando open con índice y URL."""
        from main import CTFApp
        app = CTFApp()
        app.last_links = ["https://letsdefend.io/", "https://securityblue.team/"]

        # Abrir enlace [1]
        app.handle_open_command("1")
        mock_web_open.assert_called_with("https://letsdefend.io/")

        # Abrir enlace [2]
        app.handle_open_command("2")
        mock_web_open.assert_called_with("https://securityblue.team/")

        # Abrir URL directa
        app.handle_open_command("https://google.com")
        mock_web_open.assert_called_with("https://google.com")


if __name__ == "__main__":
    unittest.main()
