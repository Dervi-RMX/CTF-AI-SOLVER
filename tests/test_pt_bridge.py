"""
Pruebas unitarias para el servidor de enlace (Bridge) de Cisco Packet Tracer.
"""

import unittest
from ctf_ai.packet_tracer.bridge import PTBridgeServer


class TestPacketTracerBridge(unittest.TestCase):

    def setUp(self):
        self.bridge = PTBridgeServer(simulated=True)

    def test_bridge_simulated_connection(self):
        self.assertTrue(self.bridge.is_connected)

    def test_add_device(self):
        res = self.bridge.add_device(dev_type="router", model="2911", x=200, y=200, name="R1")
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("deviceName"), "R1")

    def test_add_link(self):
        res = self.bridge.add_link("R1", "GigabitEthernet0/0", "PC1", "FastEthernet0", "copper_straight")
        self.assertTrue(res.get("success"))

    def test_configure_pc_ip(self):
        res = self.bridge.configure_pc_ip(name="PC1", ip="192.168.1.10", mask="255.255.255.0", gateway="192.168.1.1")
        self.assertTrue(res.get("success"))

    def test_configure_ios_device(self):
        cmds = ["hostname R1", "interface GigabitEthernet0/0", "no shutdown", "exit"]
        res = self.bridge.configure_ios_device("R1", cmds)
        self.assertTrue(res.get("success"))
        self.assertIn("results", res)
        self.assertEqual(len(res["results"]), 4)

    def test_ping_devices(self):
        res = self.bridge.ping_devices("PC1", "192.168.1.1")
        self.assertTrue(res.get("success"))
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("lossPercent"), 0.0)

    def test_clear_and_export_workspace(self):
        res_export = self.bridge.export_workspace("practica_final.pkt")
        self.assertTrue(res_export.get("success"))

        res_clear = self.bridge.clear_workspace()
        self.assertTrue(res_clear.get("success"))


if __name__ == "__main__":
    unittest.main()
