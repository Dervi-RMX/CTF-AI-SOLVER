"""
Pruebas unitarias para el gestor PacketToolsManager y su integración web.
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from ctf_ai.packet_tracer.packet_tools_manager import (
    DEFAULT_PASS,
    DEFAULT_USER,
    PACKET_TOOLS_WEB_URL,
    PacketToolsManager,
)


class TestPacketToolsManager(unittest.TestCase):

    def setUp(self):
        self.mgr = PacketToolsManager()

    def test_init_and_constants(self):
        self.assertEqual(self.mgr._cached_exe, None)
        self.assertEqual(PACKET_TOOLS_WEB_URL, "http://localhost:3000")
        self.assertEqual(DEFAULT_USER, "admin")
        self.assertEqual(DEFAULT_PASS, "admin123")

    @patch("ctf_ai.packet_tracer.packet_tools_manager.shutil.which")
    def test_find_executable_not_found(self, mock_which):
        mock_which.return_value = None
        # Si no existe en candidate paths ni en which
        with patch.object(Path, "exists", return_value=False):
            exe = self.mgr.find_executable()
            self.assertIsNone(exe)
            self.assertFalse(self.mgr.is_installed())

    @patch("ctf_ai.packet_tracer.packet_tools_manager.socket.socket")
    def test_is_port_open(self, mock_socket_cls):
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket_cls.return_value.__enter__.return_value = mock_sock

        self.assertTrue(self.mgr.is_port_open("127.0.0.1", 3000))

        mock_sock.connect_ex.return_value = 111
        self.assertFalse(self.mgr.is_port_open("127.0.0.1", 3000))

    @patch.object(PacketToolsManager, "is_web_online", return_value=True)
    def test_start_service_already_running(self, mock_web):
        ok, msg = self.mgr.start_service()
        self.assertTrue(ok)
        self.assertIn("ya se encuentra activo", msg)

    @patch.object(PacketToolsManager, "is_web_online", return_value=False)
    @patch.object(PacketToolsManager, "find_executable", return_value=None)
    def test_start_service_not_installed(self, mock_find, mock_web):
        ok, msg = self.mgr.start_service()
        self.assertFalse(ok)
        self.assertIn("no está instalado", msg)

    @patch("ctf_ai.packet_tracer.packet_tools_manager.webbrowser.open")
    def test_open_web_browser(self, mock_open):
        mock_open.return_value = True
        res = self.mgr.open_web_browser("http://localhost:3000")
        self.assertTrue(res)
        mock_open.assert_called_once_with("http://localhost:3000")

    def test_get_status_dict(self):
        with patch.object(self.mgr, "find_executable", return_value=None), \
             patch.object(self.mgr, "is_web_online", return_value=False), \
             patch.object(self.mgr, "is_api_online", return_value=False):
            diag = self.mgr.get_status()
            self.assertFalse(diag["installed"])
            self.assertFalse(diag["web_online"])
            self.assertFalse(diag["api_online"])
            self.assertEqual(diag["web_url"], "http://localhost:3000")
            self.assertEqual(diag["default_user"], "admin")


if __name__ == "__main__":
    unittest.main()
