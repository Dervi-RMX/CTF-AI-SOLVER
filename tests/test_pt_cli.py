"""
Pruebas unitarias para el controlador de comandos CLI de Packet Tracer.
"""

import unittest
from unittest.mock import MagicMock
from ctf_ai.config import Config
from ctf_ai.ai_providers import AIRouter
from ctf_ai.packet_tracer.cli import PacketTracerCLIHandler
from ctf_ai.packet_tracer.models import NetworkBlueprint, DeviceSpec


class TestPacketTracerCLI(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.router = AIRouter(self.config)
        self.cli = PacketTracerCLIHandler(self.router)
        self.cli.agent.bridge.simulated = True

    def test_cmd_status(self):
        # No debe lanzar excepción
        self.cli.handle_command("status")
        self.assertIn(self.cli.agent.state.status, ["idle", "running", "completed"])

    def test_cmd_pause_resume_stop(self):
        self.cli.handle_command("pause")
        self.assertEqual(self.cli.agent.state.status, "paused")

        self.cli.handle_command("resume")
        self.assertEqual(self.cli.agent.state.status, "running")

        self.cli.handle_command("stop")
        self.assertEqual(self.cli.agent.state.status, "stopped")

    def test_cmd_help(self):
        # No debe lanzar excepción
        self.cli.handle_command("help")

    def test_cmd_save(self):
        self.cli.handle_command("save test_out.pkt")

    def test_cmd_verify_empty(self):
        self.cli.handle_command("verify")


if __name__ == "__main__":
    unittest.main()
