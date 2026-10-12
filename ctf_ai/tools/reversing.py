"""
Herramientas de Ingeniería Inversa Estructuradas para CTF-AI Solver Pro
Inspecciona cabeceras PE y ELF, calcula entropía por sección para detectar packers (UPX/ofuscación)
y comprueba la disponibilidad de herramientas de reversing en el entorno local.
"""

import math
from pathlib import Path
import shutil
import struct
from typing import Any, Dict, List, Optional

from ctf_ai.tools.base import BaseTool, ToolResult, registry


class BinaryHeaderInspectorTool(BaseTool):
    """Inspecciona cabeceras PE (Windows) y ELF (Linux) para identificar arquitectura y metadatos."""

    name = "binary_headers"
    description = "Analiza cabeceras de ejecutables PE (Windows) y ELF (Linux) sin ejecutar el binario"
    category = "reversing"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del binario sospechoso"},
    }

    def execute(self, file_path: str) -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"El archivo no existe: {p}")

        try:
            with open(p, "rb") as f:
                data = f.read(1024)

            # 1. Comprobar ELF (Linux)
            if data.startswith(b"\x7fELF"):
                ei_class = data[4]
                ei_data = data[5]
                bitness = "64-bit" if ei_class == 2 else "32-bit"
                endian = "<" if ei_data == 1 else ">"

                e_type, e_machine = struct.unpack(endian + "HH", data[16:20])
                type_map = {1: "Relocatable (ET_REL)", 2: "Executable (ET_EXEC)", 3: "Shared object / PIE (ET_DYN)"}
                machine_map = {3: "x86 (Intel 386)", 62: "x86-64 (AMD64)", 40: "ARM", 183: "AArch64 (ARM64)", 8: "MIPS"}

                entry_point = struct.unpack(endian + ("Q" if ei_class == 2 else "I"), data[24 : 24 + (8 if ei_class == 2 else 4)])[0]

                res = {
                    "format": "ELF (Linux)",
                    "architecture": bitness,
                    "endianness": "Little Endian" if ei_data == 1 else "Big Endian",
                    "binary_type": type_map.get(e_type, f"Tipo {e_type}"),
                    "machine": machine_map.get(e_machine, f"Machine {e_machine}"),
                    "entry_point": hex(entry_point),
                }
                return ToolResult(
                    success=True,
                    output=res,
                    raw_text=f"ELF {res['architecture']} | {res['machine']} | {res['binary_type']} | Entry: {res['entry_point']}",
                )

            # 2. Comprobar PE (Windows)
            if data.startswith(b"MZ"):
                if len(data) >= 64:
                    e_lfanew = struct.unpack("<I", data[60:64])[0]
                    if e_lfanew + 24 <= len(data) and data[e_lfanew : e_lfanew + 4] == b"PE\x00\x00":
                        pe_header = data[e_lfanew + 4 : e_lfanew + 24]
                        machine, num_sections, timedate = struct.unpack("<HHI", pe_header[:8])
                        machine_str = "x86-64 (AMD64)" if machine == 0x8664 else ("x86 (Intel 386)" if machine == 0x14C else hex(machine))

                        res = {
                            "format": "PE (Windows Portable Executable)",
                            "architecture": machine_str,
                            "sections_count": num_sections,
                            "timestamp_raw": timedate,
                        }
                        return ToolResult(
                            success=True,
                            output=res,
                            raw_text=f"PE {machine_str} | Secciones: {num_sections}",
                        )

            return ToolResult(
                success=True,
                output={"format": "No es un ejecutable estándar PE ni ELF"},
                raw_text="El archivo no tiene cabeceras estándar PE (MZ) ni ELF.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class SectionEntropyInspectorTool(BaseTool):
    """Calcula la entropía de bloques del archivo para detectar empaquetadores (packers/UPX) o cifrado."""

    name = "section_entropy"
    description = "Calcula la entropía de bloques del binario para detectar empaquetamiento (UPX) o cifrado"
    category = "reversing"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del binario"},
        "block_size": {"type": "int", "required": False, "default": 1024, "help": "Tamaño de bloque en bytes"},
    }

    def execute(self, file_path: str, block_size: int = 1024) -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"El archivo no existe: {p}")

        try:
            with open(p, "rb") as f:
                data = f.read()

            if not data:
                return ToolResult(success=False, error="Archivo vacío")

            # Cálculo de entropía en bloques
            entropies = []
            high_entropy_blocks = 0
            for i in range(0, len(data), block_size):
                chunk = data[i : i + block_size]
                if not chunk:
                    continue
                counts = {}
                for b in chunk:
                    counts[b] = counts.get(b, 0) + 1
                ent = 0.0
                chunk_len = len(chunk)
                for count in counts.values():
                    p_x = count / chunk_len
                    ent += -p_x * math.log2(p_x)

                entropies.append(ent)
                if ent >= 7.2:
                    high_entropy_blocks += 1

            avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0
            is_packed = avg_entropy >= 7.1 or (high_entropy_blocks / max(1, len(entropies)) > 0.4)

            # Comprobar firma UPX explícita
            has_upx = b"UPX0" in data or b"UPX1" in data or b"UPX!" in data

            res = {
                "file_name": p.name,
                "average_entropy": round(avg_entropy, 3),
                "high_entropy_blocks_ratio": round(high_entropy_blocks / max(1, len(entropies)), 3),
                "is_likely_packed": is_packed,
                "upx_signature_detected": has_upx,
                "diagnosis": "Empaquetado / Cifrado (UPX detectado)" if has_upx else ("Probable empaquetado/cifrado" if is_packed else "Código normal no empaquetado"),
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"Entropía promedio: {res['average_entropy']}/8.0 | Diagnóstico: {res['diagnosis']}",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ReversingToolsDetectorTool(BaseTool):
    """Detecta qué herramientas de ingeniería inversa y desensamblado están instaladas en el sistema."""

    name = "reversing_env"
    description = "Comprueba qué herramientas de ingeniería inversa (objdump, ghidra, radare2, gdb) están en PATH"
    category = "reversing"
    arguments_schema = {}

    def execute(self) -> ToolResult:
        known_tools = ["objdump", "readelf", "strings", "gdb", "radare2", "r2", "cutter", "ghidra", "x64dbg", "ida64"]
        detected = {}
        for tool in known_tools:
            bin_path = shutil.which(tool)
            detected[tool] = {
                "available": bin_path is not None,
                "path": bin_path if bin_path else "No encontrado",
            }

        available_count = sum(1 for d in detected.values() if d["available"])
        return ToolResult(
            success=True,
            output=detected,
            raw_text=f"Herramientas de reversing disponibles: {available_count}/{len(known_tools)}",
        )


# Registrar herramientas de reversing
registry.register(BinaryHeaderInspectorTool)
registry.register(SectionEntropyInspectorTool)
registry.register(ReversingToolsDetectorTool)
