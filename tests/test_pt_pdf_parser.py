"""
Pruebas unitarias para el extractor de PDF y analizador de prácticas.
"""

import unittest
from unittest.mock import MagicMock
from ctf_ai.config import Config
from ctf_ai.ai_providers import AIRouter
from ctf_ai.packet_tracer.pdf_parser import PracticeAnalyzer


class TestPracticeAnalyzer(unittest.TestCase):

    def setUp(self):
        self.config = Config()
        self.router = AIRouter(self.config)
        self.analyzer = PracticeAnalyzer(self.router)

    def test_extract_text_from_nonexistent_pdf(self):
        ok, msg = self.analyzer.extract_text_from_pdf("archivo_fantasma.pdf")
        self.assertFalse(ok)
        self.assertIn("no existe", msg)

    def test_generate_fallback_blueprint(self):
        bp = self.analyzer._build_fallback_blueprint(
            "Configurar 2 routers con OSPF y 2 PCs",
            title="Práctica Fallback",
        )
        self.assertEqual(bp.title, "Práctica Fallback")
        self.assertEqual(len(bp.devices), 4)
        self.assertEqual(len(bp.links), 3)
        self.assertIn("R1", bp.configs)
        self.assertIn("PC1", bp.configs)
        self.assertEqual(len(bp.verifications), 1)

    def test_build_blueprint_from_dict(self):
        sample_json = {
            "title": "Lab Red",
            "description": "Prueba",
            "devices": [
                {"name": "R1", "device_type": "router", "model": "2911"},
                {"name": "S1", "device_type": "switch", "model": "2960"},
                {"name": "PC1", "device_type": "pc", "model": "PC-PT"},
            ],
            "links": [
                {"device1": "R1", "port1": "GigabitEthernet0/0", "device2": "S1", "port2": "GigabitEthernet0/1", "cable_type": "straight"},
                {"device1": "S1", "port1": "FastEthernet0/1", "device2": "PC1", "port2": "FastEthernet0", "cable_type": "straight"},
            ],
            "configs": {
                "R1": {
                    "hostname": "R1",
                    "interfaces": [{"name": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0"}],
                    "custom_commands": ["router ospf 1"],
                },
                "PC1": {
                    "is_pc": True,
                    "pc_ip": "192.168.1.10",
                    "pc_mask": "255.255.255.0",
                    "pc_gateway": "192.168.1.1",
                },
            },
            "verifications": [
                {"source": "PC1", "target": "192.168.1.1", "expected_success": True},
            ],
        }

        bp = self.analyzer._build_blueprint_from_dict(sample_json)
        self.assertEqual(bp.title, "Lab Red")
        self.assertEqual(len(bp.devices), 3)
        self.assertEqual(len(bp.links), 2)
        self.assertEqual(len(bp.configs), 2)
        self.assertEqual(len(bp.verifications), 1)


if __name__ == "__main__":
    unittest.main()
