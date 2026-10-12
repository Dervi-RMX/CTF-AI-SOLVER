"""
Generador y formateador de sintaxis Cisco IOS para routers y switches.
Produce listas de comandos limpias para interfaces, direccionamiento, enrutamiento (OSPF, estático),
VLANs y guardado de configuración.
"""

from typing import List, Optional
from ctf_ai.packet_tracer.models import DeviceConfig, InterfaceConfig


class CiscoIOSGenerator:
    """Genera bloques de comandos Cisco IOS estructurados listos para ser aplicados."""

    @staticmethod
    def generate_interface_block(iface: InterfaceConfig) -> List[str]:
        """Genera comandos para configurar una interfaz individual."""
        cmds = [f"interface {iface.name}"]
        if iface.description:
            cmds.append(f"description {iface.description}")
        if iface.ip and iface.mask:
            cmds.append(f"ip address {iface.ip} {iface.mask}")
        if iface.no_shutdown:
            cmds.append("no shutdown")
        for extra in iface.extra_commands:
            cmds.append(extra)
        cmds.append("exit")
        return cmds

    @staticmethod
    def generate_device_ios_script(config: DeviceConfig) -> List[str]:
        """
        Genera la secuencia completa de comandos para un dispositivo Cisco IOS:
        hostname, configuración de interfaces, comandos personalizados y guardado.
        """
        cmds = []
        if config.hostname:
            cmds.append(f"hostname {config.hostname}")

        # Configuración de interfaces
        for iface in config.interfaces:
            cmds.extend(CiscoIOSGenerator.generate_interface_block(iface))

        # Comandos personalizados (OSPF, rutas estáticas, VLANs, etc.)
        for c in config.custom_commands:
            cleaned = c.strip()
            if cleaned and not cleaned.startswith("!"):
                cmds.append(cleaned)

        # Cierre y guardado en NVRAM
        cmds.append("end")
        cmds.append("write memory")
        return cmds

    @staticmethod
    def generate_ospf_block(process_id: int, networks: List[tuple[str, str, int]], router_id: Optional[str] = None) -> List[str]:
        """
        Genera comandos para OSPFv2:
        networks: lista de tuplas (red, wildcard, area)
        """
        cmds = [f"router ospf {process_id}"]
        if router_id:
            cmds.append(f"router-id {router_id}")
        for net, wildcard, area in networks:
            cmds.append(f"network {net} {wildcard} area {area}")
        cmds.append("exit")
        return cmds

    @staticmethod
    def generate_static_route(destination_net: str, mask: str, next_hop_or_exit_if: str) -> str:
        """Genera una ruta estática en formato 'ip route <red> <mascara> <salto>'."""
        return f"ip route {destination_net} {mask} {next_hop_or_exit_if}"
