"""
Módulo de Automatización en Tiempo Real de Cisco Packet Tracer.
Inspirado en Packet Tools AI (by Demon Hacker).
"""

from ctf_ai.packet_tracer.agent import PacketTracerAgent
from ctf_ai.packet_tracer.bridge import PTBridgeServer
from ctf_ai.packet_tracer.cli import PacketTracerCLIHandler
from ctf_ai.packet_tracer.desktop import PacketTracerDesktop
from ctf_ai.packet_tracer.ios_generator import CiscoIOSGenerator
from ctf_ai.packet_tracer.models import (
    AgentState,
    DeviceConfig,
    DeviceSpec,
    InterfaceConfig,
    LinkSpec,
    NetworkBlueprint,
    PingCheck,
)
from ctf_ai.packet_tracer.pdf_parser import PracticeAnalyzer
from ctf_ai.packet_tracer.plugin_installer import PTPluginInstaller
from ctf_ai.packet_tracer.capabilities import PacketTracerCapabilities, PacketTracerCapabilityDetector
from ctf_ai.packet_tracer.validator import BlueprintIssue, blueprint_is_executable, validate_blueprint
from ctf_ai.packet_tracer.workflow import PacketTracerSolveResult, PacketTracerWorkflow

__all__ = [
    "PacketTracerAgent",
    "PTBridgeServer",
    "PacketTracerCLIHandler",
    "PacketTracerDesktop",
    "CiscoIOSGenerator",
    "AgentState",
    "DeviceConfig",
    "DeviceSpec",
    "InterfaceConfig",
    "LinkSpec",
    "NetworkBlueprint",
    "PingCheck",
    "PracticeAnalyzer",
    "PTPluginInstaller",
    "PacketTracerCapabilities",
    "PacketTracerCapabilityDetector",
    "BlueprintIssue",
    "blueprint_is_executable",
    "validate_blueprint",
    "PacketTracerSolveResult",
    "PacketTracerWorkflow",
]
