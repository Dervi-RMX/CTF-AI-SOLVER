"""
Pruebas unitarias para el pipeline de archivos locales de la PC:
Triaje de texto/binarios, autocompletado de rutas con Tab y resolución autónoma.
"""

import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from prompt_toolkit.document import Document
from rich.console import Console

from ctf_ai.completer import CTFCommandCompleter
from ctf_ai.core.file_triage import triage_local_file, format_size, is_binary_content
from ctf_ai.ui import CTFInterface
from main import CTFApp


class TestFilePipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_size(self):
        self.assertEqual(format_size(500), "500 B")
        self.assertEqual(format_size(2048), "2.0 KB")
        self.assertEqual(format_size(1048576 * 3), "3.00 MB")

    def test_is_binary_content(self):
        self.assertFalse(is_binary_content(b"Hello world! This is plain text."))
        self.assertTrue(is_binary_content(b"ELF\x7f\x00\x00\x00\x00"))

    def test_triage_text_file_with_flag(self):
        sample_file = self.temp_path / "challenge_text.txt"
        sample_file.write_text("Reto de Cripto: Encuentra el token. flag{local_text_file_pwned_1337}\nFin", encoding="utf-8")

        triage = triage_local_file(sample_file)
        self.assertEqual(triage["name"], "challenge_text.txt")
        self.assertFalse(triage["is_binary"])
        self.assertEqual(len(triage["sha256"]), 64)
        self.assertEqual(len(triage["md5"]), 32)
        self.assertIn("flag{local_text_file_pwned_1337}", triage["found_flags"])
        self.assertIn("Reto de Cripto", triage["text_preview"])

    def test_triage_binary_file_with_embedded_flag(self):
        binary_file = self.temp_path / "firmware.bin"
        # Contenido binario con bytes nulos y string legible
        binary_data = b"\x7fELF\x02\x01\x01\x00\x00\x00\x00\x00\x00" + b"\x00" * 32 + b"SECRET_KEY=ABC flag{binary_forensics_extracted_9999}\x00" + b"\xff" * 64
        binary_file.write_bytes(binary_data)

        triage = triage_local_file(binary_file)
        self.assertEqual(triage["name"], "firmware.bin")
        self.assertTrue(triage["is_binary"])
        self.assertIn("flag{binary_forensics_extracted_9999}", triage["found_flags"])
        self.assertGreater(len(triage["strings_preview"]), 0)

    def test_triage_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            triage_local_file(self.temp_path / "archivo_inexistente_98765.dat")

    def test_ui_display_file_triage(self):
        string_io = io.StringIO()
        console = Console(file=string_io, record=True, legacy_windows=False)
        ui = CTFInterface(console=console)

        mock_triage = {
            "name": "evidence.pcap",
            "path": "C:\\fake\\path\\evidence.pcap",
            "size_str": "124.5 KB",
            "size_bytes": 127488,
            "file_type": "PCAP Network Capture",
            "is_binary": True,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "md5": "d41d8cd98f00b204e9800998ecf8427e",
            "found_flags": ["flag{pcap_flag_found}"],
            "strings_preview": ["GET /secret.php", "User-Agent: curl/7.68.0"],
            "text_preview": "",
        }

        ui.display_file_triage(mock_triage)
        rendered = string_io.getvalue()
        self.assertIn("evidence.pcap", rendered)
        self.assertIn("PCAP Network Capture", rendered)
        self.assertIn("flag{pcap_flag_found}", rendered)

    def test_completer_path_completion_for_file_command(self):
        completer = CTFCommandCompleter()

        # Al escribir 'file ' o '/file ' debe activar el PathCompleter
        doc = Document("file " + str(self.temp_path) + "/")
        completions = list(completer.get_completions(doc, None))
        self.assertIsInstance(completions, list)

    @patch("main.CTFApp.run_solve_loop")
    def test_main_handle_file_command_interactive(self, mock_solve_loop):
        sample_file = self.temp_path / "test_flag.txt"
        sample_file.write_text("Hello. flag{test_flag_main_123}", encoding="utf-8")

        string_io = io.StringIO()
        console = Console(file=string_io, record=True, legacy_windows=False)
        app = CTFApp()
        app.ui.console = console

        # Simular que el usuario no arranca el solve loop de inmediato
        app.prompt_user = MagicMock(return_value="n")

        app.handle_file_command(str(sample_file))
        self.assertIn("flag{test_flag_main_123}", app.session.found_flags)
        out = string_io.getvalue()
        self.assertIn("test_flag.txt", out)


if __name__ == "__main__":
    unittest.main()
