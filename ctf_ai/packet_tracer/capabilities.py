"""Detección verificable de las capacidades disponibles de Packet Tracer."""

from __future__ import annotations

import socket
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from ctf_ai.packet_tracer.desktop import PacketTracerDesktop


@dataclass(frozen=True)
class PacketTracerCapabilities:
    """Resultado de una inspección local; no afirma capacidades no comprobadas."""

    installed: bool
    executable_path: Optional[str]
    version_hint: Optional[str]
    ipc_documented: bool
    ptmp_port_open: bool
    extension_bridge_connected: bool
    supported_operations: Dict[str, bool] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "installed": self.installed,
            "executable_path": self.executable_path,
            "version_hint": self.version_hint,
            "ipc_documented": self.ipc_documented,
            "ptmp_port_open": self.ptmp_port_open,
            "extension_bridge_connected": self.extension_bridge_connected,
            "supported_operations": dict(self.supported_operations),
            "limitations": list(self.limitations),
        }


class PacketTracerCapabilityDetector:
    """Inspecciona la instalación y separa IPC oficial de puentes opcionales."""

    def __init__(
        self,
        desktop: Optional[PacketTracerDesktop] = None,
        ipc_port: int = 39000,
    ):
        self.desktop = desktop or PacketTracerDesktop()
        self.ipc_port = ipc_port

    def detect(self, bridge_connected: bool = False) -> PacketTracerCapabilities:
        status = self.desktop.get_status()
        exe = Path(status["executable_path"]) if status["executable_path"] else None
        install_dir = exe.parent.parent if exe else None
        ipc_doc = bool(
            install_dir
            and (install_dir / "help" / "default" / "IpcAPI").is_dir()
            and (install_dir / "help" / "default" / "files" / "CiscoPacketTracerPTMPSpecification.pdf").exists()
        )
        ptmp_open = self._is_port_open("127.0.0.1", self.ipc_port)
        limitations: list[str] = []
        if not status["installed"]:
            limitations.append("No se encontró PacketTracer.exe.")
        if not ipc_doc:
            limitations.append("No se encontró la documentación local de IPC/PTMP.")
        if not ptmp_open:
            limitations.append(f"No hay un listener TCP verificable en 127.0.0.1:{self.ipc_port}.")
        elif ipc_doc:
            limitations.append(
                "El listener PTMP está abierto, pero aún no se ha autenticado ni confirmado una operación IPC."
            )
        if not bridge_connected:
            limitations.append(
                "El puente externo de extensión no está conectado; no se habilitan operaciones de edición."
            )

        return PacketTracerCapabilities(
            installed=bool(status["installed"]),
            executable_path=status["executable_path"],
            version_hint=status["version_hint"],
            ipc_documented=ipc_doc,
            ptmp_port_open=ptmp_open,
            extension_bridge_connected=bridge_connected,
            supported_operations={
                "launch": bool(status["installed"]),
                "ipc_documentation_present": ipc_doc,
                "ptmp_listener_detected": ptmp_open,
                "extension_tool_calls": bridge_connected,
            },
            limitations=limitations,
        )

    @staticmethod
    def _is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False
