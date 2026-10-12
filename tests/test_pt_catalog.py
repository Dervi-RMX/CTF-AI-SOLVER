"""
Pruebas unitarias para el catálogo de hardware Cisco y layout de topología.
"""

import unittest
from ctf_ai.packet_tracer.catalog import (
    compute_smart_topology_layout,
    get_default_ports_for_model,
    normalize_cable_type,
    normalize_device_type_and_model,
)
from ctf_ai.packet_tracer.models import DeviceSpec


class TestPacketTracerCatalog(unittest.TestCase):

    def test_normalize_device_type_and_model(self):
        d_type, model = normalize_device_type_and_model("router", "2911")
        self.assertEqual(d_type, "router")
        self.assertEqual(model, "2911")

        d_type, model = normalize_device_type_and_model("switch", "2960")
        self.assertEqual(d_type, "switch")
        self.assertEqual(model, "2960-24TT")

        d_type, model = normalize_device_type_and_model("pc")
        self.assertEqual(d_type, "pc")
        self.assertEqual(model, "PC-PT")

        d_type, model = normalize_device_type_and_model("servidor")
        self.assertEqual(d_type, "server")
        self.assertEqual(model, "Server-PT")

    def test_normalize_cable_type(self):
        self.assertEqual(normalize_cable_type("straight"), "copper_straight")
        self.assertEqual(normalize_cable_type("cross"), "copper_cross")
        self.assertEqual(normalize_cable_type("crossover"), "copper_cross")
        self.assertEqual(normalize_cable_type("serial"), "serial_dce")
        self.assertEqual(normalize_cable_type("auto"), "auto")

    def test_get_default_ports_for_model(self):
        ports_2911 = get_default_ports_for_model("2911")
        self.assertIn("GigabitEthernet0/0", ports_2911)

        ports_2960 = get_default_ports_for_model("2960-24TT")
        self.assertIn("FastEthernet0/1", ports_2960)

        ports_pc = get_default_ports_for_model("PC-PT")
        self.assertIn("FastEthernet0", ports_pc)

    def test_compute_smart_topology_layout(self):
        devices = [
            DeviceSpec(name="R1", device_type="router", model="2911"),
            DeviceSpec(name="R2", device_type="router", model="2911"),
            DeviceSpec(name="S1", device_type="switch", model="2960"),
            DeviceSpec(name="PC1", device_type="pc", model="PC-PT"),
            DeviceSpec(name="PC2", device_type="pc", model="PC-PT"),
        ]
        compute_smart_topology_layout(devices, canvas_width=900, canvas_height=600)

        # Routers deben estar en nivel superior (y = 160)
        r1 = next(d for d in devices if d.name == "R1")
        r2 = next(d for d in devices if d.name == "R2")
        self.assertEqual(r1.y, 160)
        self.assertEqual(r2.y, 160)
        self.assertNotEqual(r1.x, r2.x)

        # Switches en nivel medio (y = 340)
        s1 = next(d for d in devices if d.name == "S1")
        self.assertEqual(s1.y, 340)

        # PCs en nivel inferior (y = 520)
        pc1 = next(d for d in devices if d.name == "PC1")
        pc2 = next(d for d in devices if d.name == "PC2")
        self.assertEqual(pc1.y, 520)
        self.assertEqual(pc2.y, 520)
        self.assertNotEqual(pc1.x, pc2.x)


if __name__ == "__main__":
    unittest.main()
