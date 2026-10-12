"""
Pruebas unitarias para los modelos de datos de Cisco Packet Tracer.
"""

import unittest
from ctf_ai.packet_tracer.models import (
    AgentState,
    CableType,
    DeviceConfig,
    DeviceSpec,
    DeviceType,
    InterfaceConfig,
    LinkSpec,
    NetworkBlueprint,
    PingCheck,
)


class TestPacketTracerModels(unittest.TestCase):

    def test_device_spec_to_dict(self):
        dev = DeviceSpec(name="R1", device_type=DeviceType.ROUTER, model="2911", x=150, y=200)
        data = dev.to_dict()
        self.assertEqual(data["name"], "R1")
        self.assertEqual(data["device_type"], "router")
        self.assertEqual(data["model"], "2911")
        self.assertEqual(data["x"], 150)
        self.assertEqual(data["y"], 200)

    def test_link_spec_to_dict(self):
        link = LinkSpec(device1="R1", port1="GigabitEthernet0/0", device2="S1", port2="FastEthernet0/1", cable_type=CableType.STRAIGHT)
        data = link.to_dict()
        self.assertEqual(data["device1"], "R1")
        self.assertEqual(data["port1"], "GigabitEthernet0/0")
        self.assertEqual(data["device2"], "S1")
        self.assertEqual(data["port2"], "FastEthernet0/1")
        self.assertEqual(data["cable_type"], "straight")

    def test_interface_and_device_config(self):
        iface = InterfaceConfig(name="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0", description="LAN Principal")
        dev_cfg = DeviceConfig(device_name="R1", hostname="Router1", interfaces=[iface], custom_commands=["router ospf 1"])
        
        self.assertEqual(len(dev_cfg.interfaces), 1)
        self.assertEqual(dev_cfg.interfaces[0].ip, "192.168.1.1")
        self.assertIn("router ospf 1", dev_cfg.custom_commands)
        
        d_dict = dev_cfg.to_dict()
        self.assertEqual(d_dict["hostname"], "Router1")
        self.assertEqual(d_dict["interfaces"][0]["name"], "GigabitEthernet0/0")

    def test_network_blueprint_assembly(self):
        bp = NetworkBlueprint(title="Test Blueprint", description="Laboratorio de prueba")
        bp.devices.append(DeviceSpec(name="R1", device_type="router", model="2911"))
        bp.devices.append(DeviceSpec(name="PC1", device_type="pc", model="PC-PT"))
        bp.links.append(LinkSpec("R1", "GigabitEthernet0/0", "PC1", "FastEthernet0", "cross"))
        bp.verifications.append(PingCheck(source="PC1", target="192.168.1.1", expected_success=True))

        bp_dict = bp.to_dict()
        self.assertEqual(bp_dict["title"], "Test Blueprint")
        self.assertEqual(len(bp_dict["devices"]), 2)
        self.assertEqual(len(bp_dict["links"]), 1)
        self.assertEqual(len(bp_dict["verifications"]), 1)

    def test_agent_state_logging_and_progress(self):
        st = AgentState(total_steps=10)
        st.completed_steps = 5
        st.progress_percent = (st.completed_steps / st.total_steps) * 100.0
        st.add_log("Iniciando paso 1")
        st.add_log("Iniciando paso 2")
        
        self.assertEqual(st.progress_percent, 50.0)
        self.assertEqual(len(st.logs), 2)
        self.assertEqual(st.to_dict()["progress_percent"], 50.0)


if __name__ == "__main__":
    unittest.main()
