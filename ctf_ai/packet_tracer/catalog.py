"""
Catálogo de modelos de hardware Cisco, mapeo de interfaces, cables y layout visual en Packet Tracer.
"""

from typing import Dict, List, Optional, Tuple
from ctf_ai.packet_tracer.models import DeviceSpec


# Modelos estándar soportados en Cisco Packet Tracer
ROUTER_MODELS = {
    "2911": {"pt_model": "2911", "pt_type": "router", "ports": ["GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2"]},
    "1941": {"pt_model": "1941", "pt_type": "router", "ports": ["GigabitEthernet0/0", "GigabitEthernet0/1"]},
    "4321": {"pt_model": "4321", "pt_type": "router", "ports": ["GigabitEthernet0/0/0", "GigabitEthernet0/0/1"]},
    "4331": {"pt_model": "4331", "pt_type": "router", "ports": ["GigabitEthernet0/0/0", "GigabitEthernet0/0/1", "GigabitEthernet0/0/2"]},
    "2811": {"pt_model": "2811", "pt_type": "router", "ports": ["FastEthernet0/0", "FastEthernet0/1"]},
    "router-pt": {"pt_model": "Router-PT", "pt_type": "router", "ports": ["FastEthernet0/0", "FastEthernet1/0"]},
}

SWITCH_MODELS = {
    "2960": {
        "pt_model": "2960-24TT",
        "pt_type": "switch",
        "ports": [f"FastEthernet0/{i}" for i in range(1, 25)] + ["GigabitEthernet0/1", "GigabitEthernet0/2"],
    },
    "3560": {
        "pt_model": "3560-24PS",
        "pt_type": "switch",
        "ports": [f"FastEthernet0/{i}" for i in range(1, 25)] + [f"GigabitEthernet0/{i}" for i in range(1, 5)],
    },
    "3650": {
        "pt_model": "3650-24PS",
        "pt_type": "switch",
        "ports": [f"GigabitEthernet1/0/{i}" for i in range(1, 25)],
    },
    "switch-pt": {
        "pt_model": "Switch-PT",
        "pt_type": "switch",
        "ports": [f"FastEthernet0/{i}" for i in range(1, 25)],
    },
}

END_DEVICE_MODELS = {
    "pc": {"pt_model": "PC-PT", "pt_type": "pc", "ports": ["FastEthernet0"]},
    "laptop": {"pt_model": "Laptop-PT", "pt_type": "laptop", "ports": ["FastEthernet0"]},
    "server": {"pt_model": "Server-PT", "pt_type": "server", "ports": ["FastEthernet0", "GigabitEthernet0"]},
}

CABLE_MAPPING = {
    "straight": "copper_straight",
    "crossover": "copper_cross",
    "cross": "copper_cross",
    "serial": "serial_dce",
    "serial_dce": "serial_dce",
    "serial_dte": "serial_dte",
    "fiber": "fiber",
    "console": "console",
    "auto": "auto",
}


def normalize_device_type_and_model(raw_type: str, raw_model: Optional[str] = None) -> Tuple[str, str]:
    """
    Normaliza el tipo de dispositivo y modelo hacia identificadores reconocidos por Cisco Packet Tracer.
    """
    r_type = (raw_type or "").lower().strip()
    r_model = (raw_model or "").lower().strip()

    # Si el usuario dice "router 2911" o type es "2911"
    if "router" in r_type or r_type in ROUTER_MODELS or r_model in ROUTER_MODELS:
        for m in ROUTER_MODELS:
            if m in r_model or m in r_type:
                return "router", ROUTER_MODELS[m]["pt_model"]
        return "router", "2911"

    if "switch" in r_type or r_type in SWITCH_MODELS or r_model in SWITCH_MODELS:
        for m in SWITCH_MODELS:
            if m in r_model or m in r_type:
                return "switch", SWITCH_MODELS[m]["pt_model"]
        return "switch", "2960-24TT"

    if "server" in r_type or "servidor" in r_type or "server" in r_model:
        return "server", "Server-PT"

    if "laptop" in r_type or "portatil" in r_type or "laptop" in r_model:
        return "laptop", "Laptop-PT"

    # Default a PC
    return "pc", "PC-PT"


def normalize_cable_type(raw_cable: str) -> str:
    """Normaliza el tipo de cable a la nomenclatura esperada por Packet Tracer."""
    c = (raw_cable or "").lower().strip()
    return CABLE_MAPPING.get(c, "copper_straight")


def get_default_ports_for_model(model: str) -> List[str]:
    """Retorna la lista de puertos por defecto disponibles para un modelo."""
    m_clean = model.lower()
    for cat in (ROUTER_MODELS, SWITCH_MODELS, END_DEVICE_MODELS):
        for k, v in cat.items():
            if k in m_clean or v["pt_model"].lower() == m_clean:
                return list(v["ports"])
    return ["FastEthernet0/1", "GigabitEthernet0/1"]


def compute_smart_topology_layout(devices: List[DeviceSpec], canvas_width: int = 900, canvas_height: int = 600) -> None:
    """
    Asigna coordenadas espaciales automáticas (x, y) en cuadrícula jerárquica limpia:
    Nivel 1 (Arriba): Routers (WAN / Core / Distribución)
    Nivel 2 (Centro): Switches (Acceso / VLANs)
    Nivel 3 (Abajo): PCs, Laptops y Servidores (Hosts)
    """
    routers = [d for d in devices if d.device_type == "router"]
    switches = [d for d in devices if d.device_type == "switch"]
    hosts = [d for d in devices if d.device_type not in ("router", "switch")]

    def layout_row(group: List[DeviceSpec], y_coord: int) -> None:
        count = len(group)
        if count == 0:
            return
        step = canvas_width // (count + 1)
        for i, dev in enumerate(group):
            dev.x = step * (i + 1)
            dev.y = y_coord

    # Distribución vertical en tres alturas limpias
    layout_row(routers, y_coord=160)
    layout_row(switches, y_coord=340)
    layout_row(hosts, y_coord=520)
