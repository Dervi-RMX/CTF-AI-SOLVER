"""Validaciones deterministas del plano antes de tocar Packet Tracer."""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import List

from ctf_ai.packet_tracer.catalog import (
    END_DEVICE_MODELS,
    ROUTER_MODELS,
    SWITCH_MODELS,
    get_default_ports_for_model,
)
from ctf_ai.packet_tracer.models import NetworkBlueprint


@dataclass(frozen=True)
class BlueprintIssue:
    severity: str
    code: str
    message: str
    device: str = ""
    link_index: int = -1

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "device": self.device,
            "link_index": self.link_index,
        }


def validate_blueprint(blueprint: NetworkBlueprint) -> List[BlueprintIssue]:
    """Devuelve errores y advertencias; no modifica el plano."""
    issues: List[BlueprintIssue] = []
    devices = {d.name: d for d in blueprint.devices}

    if not devices:
        issues.append(BlueprintIssue("error", "no_devices", "El plano no contiene dispositivos."))

    if len(devices) != len(blueprint.devices):
        issues.append(BlueprintIssue("error", "duplicate_device", "Hay nombres de dispositivos duplicados."))

    networks: list[tuple[ipaddress._BaseNetwork, str]] = []
    addresses: dict[str, str] = {}
    for name, config in blueprint.configs.items():
        if name not in devices:
            issues.append(BlueprintIssue("error", "config_unknown_device", f"La configuración de {name} no tiene dispositivo.", name))
        for iface in config.interfaces:
            if iface.ip and iface.mask:
                try:
                    address = ipaddress.ip_interface(f"{iface.ip}/{iface.mask}")
                    if iface.ip in addresses:
                        issues.append(BlueprintIssue("error", "duplicate_ip", f"{iface.ip} está repetida en {addresses[iface.ip]} y {name}.", name))
                    addresses[iface.ip] = f"{name}:{iface.name}"
                    networks.append((address.network, f"{name}:{iface.name}"))
                except ValueError as exc:
                    issues.append(BlueprintIssue("error", "invalid_address", f"Dirección inválida en {name}:{iface.name}: {exc}.", name))
        if config.is_pc and config.pc_ip and config.pc_mask:
            try:
                ipaddress.ip_interface(f"{config.pc_ip}/{config.pc_mask}")
                if config.pc_ip in addresses:
                    issues.append(BlueprintIssue("error", "duplicate_ip", f"{config.pc_ip} está repetida.", name))
                addresses[config.pc_ip] = name
                if config.pc_gateway:
                    gateway = ipaddress.ip_address(config.pc_gateway)
                    if gateway not in ipaddress.ip_interface(f"{config.pc_ip}/{config.pc_mask}").network:
                        issues.append(BlueprintIssue("error", "invalid_gateway", f"El gateway {config.pc_gateway} no pertenece a la subred de {name}.", name))
            except ValueError as exc:
                issues.append(BlueprintIssue("error", "invalid_host_address", f"Direccionamiento inválido en {name}: {exc}.", name))

    for i, link in enumerate(blueprint.links):
        for endpoint, device_name, port in (
            ("origen", link.device1, link.port1),
            ("destino", link.device2, link.port2),
        ):
            device = devices.get(device_name)
            if not device:
                issues.append(BlueprintIssue("error", "link_unknown_device", f"El enlace usa un dispositivo inexistente ({device_name}).", link_index=i))
                continue
            allowed = get_default_ports_for_model(device.model)
            if port and port not in allowed:
                issues.append(BlueprintIssue("error", "unknown_interface", f"{endpoint.capitalize()} {device_name}:{port} no pertenece al modelo {device.model}.", device_name, i))

    for i, (left, left_src) in enumerate(networks):
        for right, right_src in networks[i + 1:]:
            if left.overlaps(right) and left != right:
                issues.append(BlueprintIssue("error", "overlapping_subnets", f"Las subredes {left_src} ({left}) y {right_src} ({right}) se superponen."))

    return issues


def blueprint_is_executable(blueprint: NetworkBlueprint) -> bool:
    return not any(issue.severity == "error" for issue in validate_blueprint(blueprint))
