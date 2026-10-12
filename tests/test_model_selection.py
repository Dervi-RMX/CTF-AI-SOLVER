"""
Pruebas unitarias para el catálogo de modelos, comando /model y selección interactiva.
"""

import unittest
from unittest.mock import MagicMock, patch

from ctf_ai.ai_providers import AIRouter, GeminiProvider, OpenAIProvider, ClaudeProvider
from ctf_ai.config import Config
from ctf_ai.ui import CTFInterface
from ctf_ai.completer import CTFCommandCompleter, COMMANDS_REGISTRY
from prompt_toolkit.document import Document


class TestModelSelection(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.gemini_api_key = "mock_gemini_key"
        self.mock_config.openai_api_key = "mock_openai_key"
        self.mock_config.anthropic_api_key = "mock_claude_key"
        self.mock_config.default_provider = "gemini"
        self.mock_config.default_model = "gemini-3.8-flash"
        self.router = AIRouter(config=self.mock_config)

    def test_gemini_models_catalog(self):
        gemini = GeminiProvider("fake_key")
        models = gemini.get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

        ids = [m["id"] for m in models]
        self.assertIn("gemini-3.8-flash", ids)
        self.assertIn("gemini-3.7-flash", ids)
        self.assertIn("gemini-3.5-flash", ids)

        # Verificar que el recomendado esté marcado
        rec = next(m for m in models if m["id"] == "gemini-3.8-flash")
        self.assertTrue(rec["recommended"])

    def test_openai_models_catalog(self):
        openai = OpenAIProvider("fake_key")
        models = openai.get_available_models()
        self.assertIsInstance(models, list)
        ids = [m["id"] for m in models]
        self.assertIn("gpt-4o", ids)
        self.assertIn("gpt-4o-mini", ids)
        self.assertIn("o3-mini", ids)

    def test_claude_models_catalog(self):
        claude = ClaudeProvider("fake_key")
        models = claude.get_available_models()
        self.assertIsInstance(models, list)
        ids = [m["id"] for m in models]
        self.assertIn("claude-3-5-sonnet-latest", ids)
        self.assertIn("claude-3-5-haiku-latest", ids)

    def test_router_get_available_models(self):
        # Proveedor activo por defecto es Gemini
        models = self.router.get_available_models()
        self.assertGreater(len(models), 0)
        self.assertEqual(models[0]["id"], "gemini-3.8-flash")

        # Consultar modelos de Claude específicamente
        claude_models = self.router.get_available_models("claude")
        self.assertEqual(claude_models[0]["id"], "claude-3-5-sonnet-latest")

        # Cambiar proveedor a OpenAI y verificar catálogo activo
        self.router.set_provider("openai")
        openai_models = self.router.get_available_models()
        self.assertEqual(openai_models[0]["id"], "gpt-4o")

    def test_router_set_model_by_index(self):
        self.router.set_provider("gemini")
        models = self.router.get_available_models()

        # Seleccionar índice 2 (gemini-3.7-flash)
        selected = self.router.set_model_by_index(2)
        self.assertEqual(selected, models[1]["id"])
        self.assertEqual(self.router.get_active_model_name(), models[1]["id"])

        # Índice inválido
        out_of_range = self.router.set_model_by_index(999)
        self.assertIsNone(out_of_range)
        self.assertEqual(self.router.get_active_model_name(), models[1]["id"])

    def test_router_set_model_by_name(self):
        self.router.set_model("gemini-3.5-flash")
        self.assertEqual(self.router.get_active_model_name(), "gemini-3.5-flash")

    def test_ui_display_models_menu(self):
        from rich.console import Console
        test_console = Console(record=True)
        ui = CTFInterface(console=test_console)
        models = self.router.get_available_models()
        # Verificar que se ejecuta sin lanzar excepciones
        try:
            ui.display_models_menu("gemini", models, "gemini-3.8-flash")
            ui.display_models_menu("desconocido", [], "")
            rendered = test_console.export_text()
            self.assertIn("gemini-3.8-flash", rendered)
            self.assertIn("ACTIVO", rendered)
        except Exception as e:
            self.fail(f"display_models_menu lanzó una excepción inesperada: {e}")

    def test_completer_registry_has_model(self):
        cmd_names = [name for name, aliases, desc, cat in COMMANDS_REGISTRY]
        self.assertIn("model", cmd_names)

    def test_completer_model_command_suggestions(self):
        completer = CTFCommandCompleter(router=self.router)

        # Caso 1: Escribir '/m' debe sugerir '/model'
        doc1 = Document("/m")
        completions1 = list(completer.get_completions(doc1, None))
        texts1 = [c.text for c in completions1]
        self.assertIn("/model", texts1)

        # Caso 2: Escribir '/model ' debe sugerir opciones dinámicas
        doc2 = Document("/model ")
        completions2 = list(completer.get_completions(doc2, None))
        texts2 = [c.text for c in completions2]
        self.assertIn("1", texts2)
        self.assertIn("gemini-3.8-flash", texts2)
        self.assertIn("claude", texts2)

    def test_main_handle_model_command(self):
        from main import CTFApp
        from rich.console import Console
        test_console = Console(record=True)
        app = CTFApp()
        app.ui.console = test_console

        # 1. /model sin argumentos -> muestra menú de gemini
        app.handle_model_command("")
        out1 = test_console.export_text()
        self.assertIn("gemini-3.8-flash", out1)

        # 2. /model 2 -> cambia a gemini-3.7-flash
        app.handle_model_command("2")
        self.assertEqual(app.router.get_active_model_name(), "gemini-3.7-flash")

        # 3. /model claude -> muestra catálogo de Claude
        app.handle_model_command("claude")
        out2 = test_console.export_text()
        self.assertIn("claude-3-5-sonnet-latest", out2)

        # 4. /model gpt-4o -> establece modelo por nombre
        app.handle_model_command("gpt-4o")
        self.assertEqual(app.router.get_active_model_name(), "gpt-4o")

    def test_banner_and_demon_credits(self):
        import io
        from rich.console import Console
        string_io = io.StringIO()
        test_console = Console(file=string_io, record=True, legacy_windows=False)
        ui = CTFInterface(console=test_console)
        ui.display_banner()
        rendered = string_io.getvalue()
        self.assertIn("Demon", rendered)
        self.assertIn("CTF-AI SOLVER PRO", rendered)

    def test_clear_screen_execution(self):
        from rich.console import Console
        ui = CTFInterface(console=Console(record=True, legacy_windows=False))
        try:
            ui.clear_screen()
        except Exception as e:
            self.fail(f"clear_screen lanzó un error inesperado: {e}")


if __name__ == "__main__":
    unittest.main()
