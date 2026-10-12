"""
Pruebas Unitarias para MentorAdvisor y Búsqueda Dinámica de Recursos
Verifica:
- Conversación pedagógica con el mentor a través de AIRouter.
- Retención del historial conversacional para turnos múltiples.
- Resiliencia offline ante errores de API (HTTP 429) con recomendaciones curadas de cupones de Udemy.
- Filtrado preciso en ResourceCatalog evitando listas estáticas repetitivas.
"""

import unittest
from unittest.mock import MagicMock
from ctf_ai.mentor.advisor import MentorAdvisor
from ctf_ai.mentor.interview import StudentProfile
from ctf_ai.mentor.resources import ResourceCatalog


class TestMentorAdvisor(unittest.TestCase):
    def setUp(self):
        self.mock_router = MagicMock()
        self.advisor = MentorAdvisor(self.mock_router)
        self.profile = StudentProfile(
            target_role="Pentester / Seguridad Ofensiva",
            level="Principiante",
            weekly_hours=5,
            budget_mode="100% Gratuito",
        )

    def test_consult_calls_router_with_profile(self):
        """Verifica que consult envíe la consulta y contexto del perfil al router."""
        self.mock_router.ask.return_value = "Hola, te recomiendo estos cursos de Udemy y canales..."
        history = []
        response = self.advisor.consult(
            query="busca cursos udemy",
            student_profile=self.profile,
            history=history,
        )

        self.mock_router.ask.assert_called_once()
        self.assertIn("te recomiendo estos cursos", response)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "busca cursos udemy")
        self.assertEqual(history[1]["role"], "assistant")

    def test_consult_multiturn_history(self):
        """Verifica que turnos sucesivos acumulen el contexto previo en el historial."""
        self.mock_router.ask.side_effect = [
            "Respuesta 1 sobre Udemy",
            "Respuesta 2 sobre YouTube",
        ]
        history = []
        self.advisor.consult("busca cursos udemy", self.profile, history)
        self.advisor.consult("y canales de youtube?", self.profile, history)

        self.assertEqual(len(history), 4)
        self.assertEqual(history[2]["content"], "y canales de youtube?")

    def test_offline_fallback_on_429_returns_udemy_guide(self):
        """Verifica que si la API lanza error 429, se devuelva la guía completa de cupones de Udemy."""
        self.mock_router.ask.side_effect = Exception("429 Resource has been exhausted")
        history = []
        response = self.advisor.consult(
            query="me gustaria cupones 100 gratis de udemy",
            student_profile=self.profile,
            history=history,
        )

        # Debe mencionar las plataformas clave de cupones
        self.assertIn("Discudemy", response)
        self.assertIn("Real.Discount", response)
        self.assertIn("Tutorialbar", response)
        self.assertIn("1.000 inscripciones", response)
        # El historial debe actualizarse incluso en modo offline
        self.assertEqual(len(history), 2)

    def test_offline_fallback_web_security(self):
        """Verifica que consultas offline sobre seguridad web devuelvan PortSwigger y OWASP."""
        self.mock_router.ask.side_effect = Exception("Connection Timeout")
        response = self.advisor.consult(
            query="recursos para seguridad web y owasp",
            student_profile=self.profile,
        )
        self.assertIn("PortSwigger", response)
        self.assertIn("Juice Shop", response)

    def test_resource_catalog_udemy_search_relevance(self):
        """Verifica que buscar 'udemy' devuelva específicamente recursos relacionados con Udemy."""
        catalog = ResourceCatalog()
        results = catalog.search_courses("busca cursos udemy")

        self.assertTrue(len(results) > 0)
        names = [r.name.lower() for r in results]
        # Debe contener Discudemy o Real.Discount
        self.assertTrue(any("discudemy" in n or "real.discount" in n or "tutorialbar" in n for n in names))
        # No debe devolver todos los 14 recursos
        self.assertLess(len(results), len(catalog.resources))

    def test_resource_catalog_unknown_query_does_not_dump_all(self):
        """Una consulta sin coincidencias no debe forzar la lista de 10 recursos por defecto."""
        catalog = ResourceCatalog()
        results = catalog.search_courses("astronomia cuantica y cocina")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
