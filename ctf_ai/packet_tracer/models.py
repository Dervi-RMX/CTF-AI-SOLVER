"""
Modelos y estructuras de datos para la automatización de Cisco Packet Tracer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class DeviceType(str, Enum):
    ROUTER = "router"
    SWITCH = "switch"
    PC = "pc"
    SERVER = "server"
    LAPTOP = "laptop"
    CLOUD = "cloud"


class CableType(str, Enum):
    STRAIGHT = "straight"       # Cable directo de cobre
    CROSS = "cross"             # Cable cruzado
    SERIAL = "serial"           # Serial DCE/DTE
    CONSOLE = "console"         # Consola
    AUTO = "auto"               # Auto-conexión inteligente


@dataclass
class DeviceSpec:
    """Especificación de un dispositivo físico o lógico en la topología."""
    name: str
    device_type: str = "router"
    model: str = "2911"
    x: int = 200
    y: int = 200
    display_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "device_type": self.device_type,
            "model": self.model,
            "x": self.x,
            "y": self.y,
            "display_name": self.display_name or self.name,
        }


@dataclass
class LinkSpec:
    """Especificación de un cable o enlace entre dos interfaces."""
    device1: str
    port1: str
    device2: str
    port2: str
    cable_type: str = "straight"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device1": self.device1,
            "port1": self.port1,
            "device2": self.device2,
            "port2": self.port2,
            "cable_type": self.cable_type,
        }


@dataclass
class InterfaceConfig:
    """Configuración IP y parámetros de una interfaz de red."""
    name: str
    ip: Optional[str] = None
    mask: Optional[str] = None
    description: Optional[str] = None
    no_shutdown: bool = True
    extra_commands: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ip": self.ip,
            "mask": self.mask,
            "description": self.description,
            "no_shutdown": self.no_shutdown,
            "extra_commands": self.extra_commands,
        }


@dataclass
class DeviceConfig:
    """Configuración completa para un dispositivo Cisco IOS o Host."""
    device_name: str
    hostname: Optional[str] = None
    interfaces: List[InterfaceConfig] = field(default_factory=list)
    custom_commands: List[str] = field(default_factory=list)
    is_pc: bool = False
    pc_ip: Optional[str] = None
    pc_mask: Optional[str] = None
    pc_gateway: Optional[str] = None
    pc_dns: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_name": self.device_name,
            "hostname": self.hostname or self.device_name,
            "interfaces": [iface.to_dict() for iface in self.interfaces],
            "custom_commands": self.custom_commands,
            "is_pc": self.is_pc,
            "pc_ip": self.pc_ip,
            "pc_mask": self.pc_mask,
            "pc_gateway": self.pc_gateway,
            "pc_dns": self.pc_dns,
        }


@dataclass
class PingCheck:
    """Prueba de verificación de conectividad."""
    source: str
    target: str
    expected_success: bool = True
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "expected_success": self.expected_success,
            "description": self.description or f"{self.source} -> {self.target}",
        }


@dataclass
class NetworkBlueprint:
    """Plano completo de la red para su ejecución y verificación."""
    title: str = "Topología de Red"
    description: str = ""
    devices: List[DeviceSpec] = field(default_factory=list)
    links: List[LinkSpec] = field(default_factory=list)
    configs: Dict[str, DeviceConfig] = field(default_factory=dict)
    verifications: List[PingCheck] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "devices": [d.to_dict() for d in self.devices],
            "links": [link.to_dict() for link in self.links],
            "configs": {k: v.to_dict() for k, v in self.configs.items()},
            "verifications": [v.to_dict() for v in self.verifications],
            "notes": self.notes,
        }


@dataclass
class AgentState:
    """Estado en tiempo real del agente de automatización."""
    status: str = "idle"  # idle, planning, running, paused, stopped, verifying, correcting, completed, error
    current_step: str = ""
    progress_percent: float = 0.0
    total_steps: int = 0
    completed_steps: int = 0
    logs: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    active_device: Optional[str] = None

    def add_log(self, message: str) -> None:
        self.logs.append(message)
        if len(self.logs) > 500:
            self.logs.pop(0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "current_step": self.current_step,
            "progress_percent": round(self.progress_percent, 1),
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "error_message": self.error_message,
            "active_device": self.active_device,
            "log_count": len(self.logs),
        }
