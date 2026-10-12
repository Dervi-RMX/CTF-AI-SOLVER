"""
Pruebas unitarias para el agente autónomo de bucle cerrado de Packet Tracer.
"""

import unittest
from ctf_ai.packet_tracer.agent import PacketTracerAgent
from ctf_ai.packet_tracer.bridge import PTBridgeServer
from ctf_ai.packet_tracer.desktop import PacketTracerDesktop
from ctf_ai.packet_tracer.models import (
    DeviceConfig,
    DeviceSpec,
    InterfaceConfig,
    LinkSpec,
    NetworkBlueprint,
    PingCheck,
)


class TestPacketTracerAgent(unittest.TestCase):

    def setUp(self):
        self.bridge = PTBridgeServer(simulated=True)
        self.desktop = PacketTracerDesktop()
        self.agent = PacketTracerAgent(bridge=self.bridge, desktop=self.desktop)

    def test_agent_sync_execution(self):
        bp = NetworkBlueprint(title="Test Red OSPF")
        bp.devices = [
            DeviceSpec(name="R1", device_type="router", model="2911", x=100, y=100),
            DeviceSpec(name="PC1", device_type="pc", model="PC-PT", x=100, y=300),
        ]
        bp.links = [
            LinkSpec(device1="R1", port1="GigabitEthernet0/0", device2="PC1", port2="FastEthernet0", cable_type="cross"),
        ]
        bp.configs = {
            "R1": DeviceConfig(
                device_name="R1",
                hostname="R1",
                interfaces=[InterfaceConfig("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0")],
            ),
            "PC1": DeviceConfig(
                device_name="PC1",
                is_pc=True,
                pc_ip="192.168.1.10",
                pc_mask="255.255.255.0",
                pc_gateway="192.168.1.1",
            ),
        }
        bp.verifications = [
            PingCheck(source="PC1", target="192.168.1.1", expected_success=True),
        ]

        state = self.agent.execute_blueprint_sync(bp, save_path="test_lab.pkt")

        self.assertEqual(state.status, "completed")
        self.assertEqual(state.progress_percent, 100.0)
        self.assertGreater(state.completed_steps, 0)
        self.assertIsNone(state.error_message)

    def test_agent_pause_resume_stop(self):
        self.agent.pause()
        self.assertEqual(self.agent.state.status, "paused")

        self.agent.resume()
        self.assertEqual(self.agent.state.status, "running")

        self.agent.stop()
        self.assertEqual(self.agent.state.status, "stopped")


if __name__ == "__main__":
    unittest.main()
