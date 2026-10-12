"""
Extractor y analizador de prácticas de redes en PDF y lenguaje natural.
Utiliza pypdf y AIRouter para convertir requerimientos en un NetworkBlueprint estructurado.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from ctf_ai.ai_providers import AIRouter
from ctf_ai.packet_tracer.catalog import (
    compute_smart_topology_layout,
    normalize_cable_type,
    normalize_device_type_and_model,
)
from ctf_ai.packet_tracer.models import (
    DeviceConfig,
    DeviceSpec,
    InterfaceConfig,
    LinkSpec,
    NetworkBlueprint,
    PingCheck,
)


BLUEPRINT_PROMPT_SYSTEM = """Eres un arquitecto senior de redes Cisco y experto en Cisco Packet Tracer.
Tu misión es analizar la descripción de una práctica de laboratorio o el texto extraído de un PDF
y generar un plano de red estructurado en formato JSON EXACTO, sin texto conversacional adicional ni explicaciones.

El JSON debe tener la siguiente estructura:
{
  "title": "Nombre de la práctica",
  "description": "Objetivo de la topología",
  "devices": [
    {"name": "R1", "device_type": "router", "model": "2911"},
    {"name": "S1", "device_type": "switch", "model": "2960"},
    {"name": "PC1", "device_type": "pc", "model": "PC-PT"}
  ],
  "links": [
    {"device1": "R1", "port1": "GigabitEthernet0/0", "device2": "S1", "port2": "GigabitEthernet0/1", "cable_type": "straight"},
    {"device1": "S1", "port1": "FastEthernet0/1", "device2": "PC1", "port2": "FastEthernet0", "cable_type": "straight"}
  ],
  "configs": {
    "R1": {
      "hostname": "R1",
      "interfaces": [
        {"name": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0", "description": "LAN R1"}
      ],
      "custom_commands": [
        "router ospf 1",
        "network 192.168.1.0 0.0.0.255 area 0",
        "exit"
      ]
    },
    "PC1": {
      "is_pc": true,
      "pc_ip": "192.168.1.10",
      "pc_mask": "255.255.255.0",
      "pc_gateway": "192.168.1.1",
      "pc_dns": "8.8.8.8"
    }
  },
  "verifications": [
    {"source": "PC1", "target": "192.168.1.1", "expected_success": true}
  ]
}
"""


class PracticeAnalyzer:
    """Extrae y parsea requerimientos de prácticas desde PDF o texto."""

    def __init__(self, router: AIRouter):
        self.router = router

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Tuple[bool, str]:
        """Extrae el contenido textual completo de un archivo PDF usando pypdf."""
        p = Path(pdf_path)
        if not p.exists():
            return False, f"El archivo PDF '{pdf_path}' no existe."

        if not HAS_PYPDF:
            return False, "La biblioteca 'pypdf' no está disponible en el entorno."

        try:
            reader = pypdf.PdfReader(str(p))
            full_text = []
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                full_text.append(f"--- Página {idx + 1} ---\n{text}")

            combined = "\n\n".join(full_text).strip()
            if not combined:
                return False, "El archivo PDF no contiene texto legible (posible documento escaneado/imagen)."
            return True, combined
        except Exception as e:
            return False, f"Error al leer el archivo PDF: {e}"

    def generate_blueprint_from_text(self, text_content: str, title_hint: str = "Práctica") -> NetworkBlueprint:
        """
        Envía el texto de la práctica a la IA y construye un NetworkBlueprint con coordenadas geométricas automáticas.
        """
        prompt = (
            f"{BLUEPRINT_PROMPT_SYSTEM}\n\n"
            f"REQUERIMIENTOS DEL LABORATORIO / TEXTO DEL PDF:\n"
            f"{text_content}\n\n"
            f"Devuelve ÚNICAMENTE el bloque JSON."
        )

        try:
            ai_resp = self.router.ask(prompt=prompt, system_prompt=BLUEPRINT_PROMPT_SYSTEM)
            # Extraer JSON de bloques markdown o texto plano
            json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", ai_resp, re.DOTALL)
            raw_json = json_match.group(1) if json_match else ai_resp.strip()
            # Limpiar posible basura antes de {
            start_brace = raw_json.find("{")
            end_brace = raw_json.rfind("}")
            if start_brace != -1 and end_brace != -1:
                raw_json = raw_json[start_brace : end_brace + 1]

            data = json.loads(raw_json)
            return self._build_blueprint_from_dict(data)
        except Exception:
            # Nunca inventar una topología cuando el análisis estructurado no está disponible.
            return self._build_unresolved_blueprint(text_content, title_hint)

    def extract_documents(self, pdf_paths: List[str], inline_text: str = "") -> Tuple[bool, str]:
        """Combina varios PDF y texto introducido por el usuario sin ejecutar su contenido."""
        chunks = [inline_text.strip()] if inline_text.strip() else []
        errors = []
        for pdf_path in pdf_paths:
            ok, content = self.extract_text_from_pdf(pdf_path)
            if ok:
                chunks.append(f"--- Documento: {Path(pdf_path).name} ---\n{content}")
            else:
                errors.append(content)
        if not chunks:
            return False, "No se pudo extraer texto de la práctica."
        if errors:
            chunks.append("--- Advertencias de extracción ---\n" + "\n".join(errors))
        return True, "\n\n".join(chunks)

    def _build_blueprint_from_dict(self, data: Dict[str, Any]) -> NetworkBlueprint:
        """Convierte el diccionario JSON validado en el objeto fuertemente tipado NetworkBlueprint."""
        bp = NetworkBlueprint(
            title=data.get("title", "Laboratorio Cisco"),
            description=data.get("description", ""),
        )

        # 1. Dispositivos
        for d in data.get("devices", []):
            d_type, model = normalize_device_type_and_model(d.get("device_type", ""), d.get("model", ""))
            spec = DeviceSpec(
                name=d.get("name", "Dev"),
                device_type=d_type,
                model=model,
            )
            bp.devices.append(spec)

        # 2. Asignar coordenadas espaciales automáticas limpias (grid)
        compute_smart_topology_layout(bp.devices)

        # 3. Enlaces
        for l in data.get("links", []):
            bp.links.append(
                LinkSpec(
                    device1=l.get("device1", ""),
                    port1=l.get("port1", ""),
                    device2=l.get("device2", ""),
                    port2=l.get("port2", ""),
                    cable_type=normalize_cable_type(l.get("cable_type", "straight")),
                )
            )

        # 4. Configuraciones
        for dev_name, cfg in data.get("configs", {}).items():
            ifaces = []
            for if_data in cfg.get("interfaces", []):
                ifaces.append(
                    InterfaceConfig(
                        name=if_data.get("name", ""),
                        ip=if_data.get("ip"),
                        mask=if_data.get("mask"),
                        description=if_data.get("description"),
                        no_shutdown=if_data.get("no_shutdown", True),
                        extra_commands=if_data.get("extra_commands", []),
                    )
                )

            bp.configs[dev_name] = DeviceConfig(
                device_name=dev_name,
                hostname=cfg.get("hostname", dev_name),
                interfaces=ifaces,
                custom_commands=cfg.get("custom_commands", []),
                is_pc=cfg.get("is_pc", False),
                pc_ip=cfg.get("pc_ip"),
                pc_mask=cfg.get("pc_mask"),
                pc_gateway=cfg.get("pc_gateway"),
                pc_dns=cfg.get("pc_dns"),
            )

        # 5. Verificaciones
        for v in data.get("verifications", []):
            bp.verifications.append(
                PingCheck(
                    source=v.get("source", ""),
                    target=v.get("target", ""),
                    expected_success=v.get("expected_success", True),
                    description=v.get("description"),
                )
            )

        return bp

    def _build_fallback_blueprint(self, text: str, title: str) -> NetworkBlueprint:
        """Generador histórico conservado para compatibilidad con clientes existentes."""
        bp = NetworkBlueprint(title=title, description=text[:120])
        bp.devices = [
            DeviceSpec(name="R1", device_type="router", model="2911"),
            DeviceSpec(name="R2", device_type="router", model="2911"),
            DeviceSpec(name="PC1", device_type="pc", model="PC-PT"),
            DeviceSpec(name="PC2", device_type="pc", model="PC-PT"),
        ]
        compute_smart_topology_layout(bp.devices)
        bp.links = [
            LinkSpec("R1", "GigabitEthernet0/0", "PC1", "FastEthernet0", "cross"),
            LinkSpec("R1", "GigabitEthernet0/1", "R2", "GigabitEthernet0/1", "cross"),
            LinkSpec("R2", "GigabitEthernet0/0", "PC2", "FastEthernet0", "cross"),
        ]
        bp.configs = {
            "R1": DeviceConfig(
                device_name="R1",
                hostname="R1",
                interfaces=[
                    InterfaceConfig("GigabitEthernet0/0", "192.168.1.1", "255.255.255.0"),
                    InterfaceConfig("GigabitEthernet0/1", "10.0.0.1", "255.255.255.252"),
                ],
                custom_commands=["router ospf 1", "network 192.168.1.0 0.0.0.255 area 0", "network 10.0.0.0 0.0.0.3 area 0", "exit"],
            ),
            "R2": DeviceConfig(
                device_name="R2",
                hostname="R2",
                interfaces=[
                    InterfaceConfig("GigabitEthernet0/0", "192.168.2.1", "255.255.255.0"),
                    InterfaceConfig("GigabitEthernet0/1", "10.0.0.2", "255.255.255.252"),
                ],
                custom_commands=["router ospf 1", "network 192.168.2.0 0.0.0.255 area 0", "network 10.0.0.0 0.0.0.3 area 0", "exit"],
            ),
            "PC1": DeviceConfig(device_name="PC1", is_pc=True, pc_ip="192.168.1.10", pc_mask="255.255.255.0", pc_gateway="192.168.1.1"),
            "PC2": DeviceConfig(device_name="PC2", is_pc=True, pc_ip="192.168.2.10", pc_mask="255.255.255.0", pc_gateway="192.168.2.1"),
        }
        bp.verifications = [
            PingCheck(source="PC1", target="192.168.2.10", expected_success=True, description="Ping PC1 a PC2"),
        ]
        return bp

    def _build_unresolved_blueprint(self, text: str, title: str) -> NetworkBlueprint:
        """Plano seguro cuando faltan datos o el proveedor no pudo analizar la práctica."""
        return NetworkBlueprint(
            title=title,
            description=text[:500],
            notes=[
                "No se generó una topología automáticamente porque el análisis estructurado no fue confirmado.",
                "Requiere un proveedor de IA disponible o datos explícitos de dispositivos, enlaces y direccionamiento.",
            ],
        )
