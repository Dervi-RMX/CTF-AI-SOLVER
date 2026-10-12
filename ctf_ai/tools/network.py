"""
Herramientas de Diagnóstico y Análisis de Red Estructuradas para CTF-AI Solver Pro
Resolución DNS, verificación de servicios remotos de retos (netcat/puertos) y conectividad.
"""

import socket
import time
from typing import Any, Dict, List, Optional

from ctf_ai.tools.base import BaseTool, ToolResult, registry


class DnsAnalyzerTool(BaseTool):
    """Resuelve registros DNS y obtiene información de direccionamiento de objetivos de retos."""

    name = "dns_analyze"
    description = "Resuelve registros DNS A y PTR básico de un dominio de reto CTF"
    category = "network"
    arguments_schema = {
        "domain": {"type": "str", "required": True, "help": "Nombre de dominio a resolver"},
    }

    def execute(self, domain: str) -> ToolResult:
        cleaned = domain.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
        try:
            ip = socket.gethostbyname(cleaned)
            hostname = "Desconocido"
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                pass

            res = {
                "domain": cleaned,
                "ip_address": ip,
                "reverse_hostname": hostname,
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"Dominio: {cleaned} -> IP: {ip} (Reverse: {hostname})",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Fallo DNS: {str(e)}")


class PortConnectivityCheckTool(BaseTool):
    """Comprueba si un servicio de reto remoto (ej. netcat / socat / web) está accesible en un puerto."""

    name = "service_check"
    description = "Comprueba si el puerto de un servicio de reto remoto está abierto y respondiendo"
    category = "network"
    arguments_schema = {
        "host": {"type": "str", "required": True, "help": "Host o IP del reto"},
        "port": {"type": "int", "required": True, "help": "Puerto del servicio"},
        "timeout": {"type": "int", "required": False, "default": 5, "help": "Tiempo de espera en segundos"},
    }

    def execute(self, host: str, port: int, timeout: int = 5) -> ToolResult:
        cleaned_host = host.strip().replace("http://", "").replace("https://", "").split("/")[0]
        port = int(port)

        start = time.perf_counter()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            code = s.connect_ex((cleaned_host, port))
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            s.close()

            is_open = (code == 0)
            status_desc = "Abierto / Accesible" if is_open else f"Cerrado o Filtrado (Código {code})"

            res = {
                "host": cleaned_host,
                "port": port,
                "is_open": is_open,
                "latency_ms": round(elapsed_ms, 1),
                "status": status_desc,
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"{cleaned_host}:{port} -> {status_desc} ({res['latency_ms']}ms)",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Fallo de conexión: {str(e)}")


# Registrar herramientas de red
registry.register(DnsAnalyzerTool)
registry.register(PortConnectivityCheckTool)
