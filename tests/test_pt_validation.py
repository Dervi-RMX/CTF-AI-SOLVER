import unittest

from ctf_ai.packet_tracer.models import (
    DeviceConfig,
    DeviceSpec,
    InterfaceConfig,
    LinkSpec,
    NetworkBlueprint,
)
from ctf_ai.packet_tracer.validator import validate_blueprint


class TestPacketTracerValidation(unittest.TestCase):
    def test_duplicate_ip_is_rejected(self):
        blueprint = NetworkBlueprint(
            devices=[
                DeviceSpec("R1", "router", "2911"),
                DeviceSpec("R2", "router", "2911"),
            ],
            configs={
                "R1": DeviceConfig(
                    "R1",
                    interfaces=[InterfaceConfig("GigabitEthernet0/0", "10.0.0.1", "255.255.255.0")],
                ),
                "R2": DeviceConfig(
                    "R2",
                    interfaces=[InterfaceConfig("GigabitEthernet0/0", "10.0.0.1", "255.255.255.0")],
                ),
            },
        )
        issues = validate_blueprint(blueprint)
        self.assertTrue(any(issue.code == "duplicate_ip" for issue in issues))

    def test_unknown_interface_is_rejected(self):
        blueprint = NetworkBlueprint(
            devices=[DeviceSpec("R1", "router", "1941"), DeviceSpec("PC1", "pc", "PC-PT")],
            links=[LinkSpec("R1", "GigabitEthernet0/2", "PC1", "FastEthernet0")],
        )
        issues = validate_blueprint(blueprint)
        self.assertTrue(any(issue.code == "unknown_interface" for issue in issues))

    def test_valid_small_topology_has_no_errors(self):
        blueprint = NetworkBlueprint(
            devices=[DeviceSpec("R1", "router", "1941"), DeviceSpec("PC1", "pc", "PC-PT")],
            links=[LinkSpec("R1", "GigabitEthernet0/0", "PC1", "FastEthernet0")],
            configs={
                "R1": DeviceConfig(
                    "R1",
                    interfaces=[InterfaceConfig("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0")],
                ),
                "PC1": DeviceConfig(
                    "PC1",
                    is_pc=True,
                    pc_ip="192.168.1.10",
                    pc_mask="255.255.255.0",
                    pc_gateway="192.168.1.1",
                ),
            },
        )
        self.assertFalse([issue for issue in validate_blueprint(blueprint) if issue.severity == "error"])


if __name__ == "__main__":
    unittest.main()
