"""
Pruebas unitarias para el generador de sintaxis Cisco IOS.
"""

import unittest
from ctf_ai.packet_tracer.ios_generator import CiscoIOSGenerator
from ctf_ai.packet_tracer.models import DeviceConfig, InterfaceConfig


class TestCiscoIOSGenerator(unittest.TestCase):

    def test_generate_interface_block(self):
        iface = InterfaceConfig(
            name="GigabitEthernet0/0",
            ip="192.168.1.1",
            mask="255.255.255.0",
            description="Enlace LAN",
            no_shutdown=True,
        )
        cmds = CiscoIOSGenerator.generate_interface_block(iface)

        self.assertIn("interface GigabitEthernet0/0", cmds)
        self.assertIn("description Enlace LAN", cmds)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", cmds)
        self.assertIn("no shutdown", cmds)
        self.assertEqual(cmds[-1], "exit")

    def test_generate_device_ios_script(self):
        iface1 = InterfaceConfig(name="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0")
        iface2 = InterfaceConfig(name="GigabitEthernet0/1", ip="10.0.0.1", mask="255.255.255.252")
        cfg = DeviceConfig(
            device_name="R1",
            hostname="R1-Core",
            interfaces=[iface1, iface2],
            custom_commands=["router ospf 1", "network 192.168.1.0 0.0.0.255 area 0", "exit"],
        )
        script = CiscoIOSGenerator.generate_device_ios_script(cfg)

        self.assertEqual(script[0], "hostname R1-Core")
        self.assertIn("interface GigabitEthernet0/0", script)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", script)
        self.assertIn("interface GigabitEthernet0/1", script)
        self.assertIn("ip address 10.0.0.1 255.255.255.252", script)
        self.assertIn("router ospf 1", script)
        self.assertIn("network 192.168.1.0 0.0.0.255 area 0", script)
        self.assertIn("end", script)
        self.assertIn("write memory", script)

    def test_generate_ospf_block(self):
        networks = [
            ("192.168.1.0", "0.0.0.255", 0),
            ("10.0.0.0", "0.0.0.3", 0),
        ]
        cmds = CiscoIOSGenerator.generate_ospf_block(process_id=1, networks=networks, router_id="1.1.1.1")
        self.assertIn("router ospf 1", cmds)
        self.assertIn("router-id 1.1.1.1", cmds)
        self.assertIn("network 192.168.1.0 0.0.0.255 area 0", cmds)
        self.assertIn("network 10.0.0.0 0.0.0.3 area 0", cmds)
        self.assertEqual(cmds[-1], "exit")

    def test_generate_static_route(self):
        route = CiscoIOSGenerator.generate_static_route("192.168.2.0", "255.255.255.0", "10.0.0.2")
        self.assertEqual(route, "ip route 192.168.2.0 255.255.255.0 10.0.0.2")


if __name__ == "__main__":
    unittest.main()
