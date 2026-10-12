"""
Herramientas de Análisis Forense Digital Estructuradas para CTF-AI Solver Pro
Incluye inspección de Magic Bytes, extracción profunda de cadenas (ASCII y UTF-16),
inspección segura de archivos ZIP y parser nativo de capturas de red PCAP sin dependencias externas.
"""

import collections
import os
from pathlib import Path
import re
import struct
import zipfile
from typing import Any, Dict, List, Optional

from ctf_ai.tools.base import BaseTool, ToolResult, registry


EXTENDED_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "PNG Image",
    b"\xff\xd8\xff": "JPEG Image",
    b"GIF87a": "GIF87a Image",
    b"GIF89a": "GIF89a Image",
    b"PK\x03\x04": "ZIP Archive / DOCX / APK / JAR",
    b"PK\x05\x06": "ZIP Archive (Empty)",
    b"\x1f\x8b\x08": "GZIP Compressed File",
    b"BZh": "BZIP2 Archive",
    b"7z\xbc\xaf\x27\x1c": "7-Zip Archive",
    b"Rar!\x1a\x07\x00": "RAR v4 Archive",
    b"Rar!\x1a\x07\x01\x00": "RAR v5 Archive",
    b"%PDF": "PDF Document",
    b"\x7fELF": "ELF Executable (Linux)",
    b"MZ": "PE Executable / DLL (Windows DOS MZ)",
    b"\xca\xfe\xba\xbe": "Java Class / Mach-O Fat Binary",
    b"\xfe\xed\xfa\xce": "Mach-O 32-bit Binary",
    b"\xfe\xed\xfa\xcf": "Mach-O 64-bit Binary",
    b"OggS": "OGG Audio/Video Container",
    b"RIFF": "RIFF Multimedia (WAV / AVI / WEBP)",
    b"SQLite format 3\x00": "SQLite 3 Database",
    b"\xd4\xc3\xb2\xa1": "PCAP Network Capture (Little Endian)",
    b"\xa1\xb2\xc3\xd4": "PCAP Network Capture (Big Endian)",
    b"\x0a\x0d\x0d\x0a": "PCAPNG Network Capture",
    b"\xed\xab\xee\xdb": "RPM Package",
    b"ustar": "TAR Archive",
    b"\x49\x49\x2a\x00": "TIFF Image (Little Endian)",
    b"\x4d\x4d\x00\x2a": "TIFF Image (Big Endian)",
}


class MagicBytesInspectorTool(BaseTool):
    """Inspecciona los primeros bytes de un archivo para determinar su tipo real y detectar corrupción."""

    name = "magic_inspector"
    description = "Analiza firmas binarias (magic bytes) para identificar tipo real y posibles corrupciones"
    category = "forensics"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del archivo a inspeccionar"},
    }

    def execute(self, file_path: str) -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"El archivo no existe: {p}")

        file_size = p.stat().st_size
        try:
            with open(p, "rb") as f:
                header = f.read(32)

            detected_type = "Desconocido / Binario Genérico"
            matched_sig = None

            for sig, desc in EXTENDED_SIGNATURES.items():
                if header.startswith(sig):
                    detected_type = desc
                    matched_sig = sig.hex()
                    break

            # Comprobar si parece un PNG con cabecera alterada (común en CTF)
            corruption_notes = []
            if b"PNG" in header and not header.startswith(b"\x89PNG"):
                corruption_notes.append("Aviso: Contiene 'PNG' pero los magic bytes iniciales están alterados.")

            res = {
                "file_name": p.name,
                "size_bytes": file_size,
                "header_hex": header[:16].hex(),
                "detected_type": detected_type,
                "matched_signature": matched_sig,
                "anomalies": corruption_notes,
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"Tipo detectado: {detected_type} (Header: {res['header_hex']})",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class DeepStringsTool(BaseTool):
    """Extrae cadenas imprimibles tanto en ASCII como en codificación UTF-16."""

    name = "deep_strings"
    description = "Extrae cadenas ASCII y UTF-16 (Unicode LE/BE) buscando patrones de banderas CTF"
    category = "forensics"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del archivo"},
        "min_len": {"type": "int", "required": False, "default": 4, "help": "Longitud mínima"},
        "pattern": {"type": "str", "required": False, "default": "", "help": "Patrón regex para filtrar"},
    }

    def execute(self, file_path: str, min_len: int = 4, pattern: str = "") -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"Archivo no encontrado: {p}")

        try:
            with open(p, "rb") as f:
                data = f.read()

            # 1. Extracción ASCII
            ascii_re = re.compile(rb"[\x20-\x7e]{" + str(min_len).encode() + rb",}")
            ascii_matches = [m.decode("ascii", errors="ignore") for m in ascii_re.findall(data)]

            # 2. Extracción UTF-16 LE (común en binarios Windows y volcados de memoria)
            utf16_matches = []
            utf16_re = re.compile(rb"(?:[\x20-\x7e]\x00){" + str(min_len).encode() + rb",}")
            for m in utf16_re.findall(data):
                try:
                    utf16_matches.append(m.decode("utf-16-le", errors="ignore"))
                except Exception:
                    pass

            combined = ascii_matches + utf16_matches

            # Búsqueda de flags
            flag_re = re.compile(r"(?:flag|ctf|picoctf|htb)\{[^}]+\}", re.IGNORECASE)
            found_flags = []
            for s in combined:
                m = flag_re.findall(s)
                for f_str in m:
                    if f_str not in found_flags:
                        found_flags.append(f_str)

            filtered = combined
            if pattern:
                pat_compiled = re.compile(pattern, re.IGNORECASE)
                filtered = [s for s in combined if pat_compiled.search(s)]

            res = {
                "total_strings_found": len(combined),
                "ascii_count": len(ascii_matches),
                "utf16_count": len(utf16_matches),
                "potential_flags": found_flags,
                "preview_sample": filtered[:50],
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"Cadenas encontradas: {len(combined)} (Banderas potenciales: {found_flags})",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class ZipInspectorTool(BaseTool):
    """Inspecciona archivos ZIP sin extraerlos, previniendo zip-bombs y path traversal."""

    name = "zip_inspector"
    description = "Inspecciona el contenido interno de un ZIP con protección contra zip-bombs y traversal"
    category = "forensics"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del archivo ZIP"},
    }

    def execute(self, file_path: str) -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"El archivo no existe: {p}")

        if not zipfile.is_zipfile(p):
            return ToolResult(success=False, error=f"El archivo no es un archivo ZIP válido: {p}")

        try:
            with zipfile.ZipFile(p, "r") as zf:
                infolist = zf.infolist()
                files = []
                total_uncompressed = 0
                total_compressed = 0
                security_warnings = []

                for info in infolist:
                    total_uncompressed += info.file_size
                    total_compressed += info.compress_size

                    # Chequeo de Path Traversal
                    if ".." in info.filename or info.filename.startswith("/"):
                        security_warnings.append(f"Peligro: '{info.filename}' contiene intento de Path Traversal")

                    files.append({
                        "filename": info.filename,
                        "size": info.file_size,
                        "compressed_size": info.compress_size,
                        "is_dir": info.is_dir(),
                    })

                # Detección de Zip-Bomb (ratio > 100 y tamaño descomprimido > 50MB)
                ratio = total_uncompressed / max(1, total_compressed)
                if ratio > 100 and total_uncompressed > 50 * 1024 * 1024:
                    security_warnings.append(f"Alerta de Zip-Bomb: ratio de compresión anómalo {ratio:.1f}:1")

                res = {
                    "file_count": len(files),
                    "total_uncompressed_bytes": total_uncompressed,
                    "compression_ratio": round(ratio, 2),
                    "security_warnings": security_warnings,
                    "files": files,
                }
                return ToolResult(
                    success=True,
                    output=res,
                    raw_text=f"ZIP con {len(files)} archivos. Descomprimido: {total_uncompressed} bytes. Avisos: {security_warnings}",
                )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class PcapParserTool(BaseTool):
    """Analizador de paquetes PCAP clásico en Python puro sin dependencias externas."""

    name = "pcap_parser"
    description = "Analiza capturas PCAP: lista conversaciones IP, protocolos y busca banderas en payloads"
    category = "forensics"
    arguments_schema = {
        "file_path": {"type": "str", "required": True, "help": "Ruta del archivo PCAP"},
        "max_packets": {"type": "int", "required": False, "default": 2000, "help": "Límite de paquetes a leer"},
    }

    def execute(self, file_path: str, max_packets: int = 2000) -> ToolResult:
        p = Path(file_path.strip("\"'"))
        if not p.exists():
            return ToolResult(success=False, error=f"Archivo no encontrado: {p}")

        try:
            with open(p, "rb") as f:
                header = f.read(24)
                if len(header) < 24:
                    return ToolResult(success=False, error="Archivo demasiado pequeño para ser PCAP")

                magic = header[:4]
                if magic == b"\xd4\xc3\xb2\xa1":
                    endian = "<"
                elif magic == b"\xa1\xb2\xc3\xd4":
                    endian = ">"
                else:
                    return ToolResult(success=False, error=f"Formato no reconocido como PCAP clásico (Magic: {magic.hex()})")

                packets_read = 0
                ip_conversations = collections.Counter()
                found_flags = []
                flag_re = re.compile(rb"(?:flag|ctf|picoctf)\{[^}]+\}", re.IGNORECASE)

                while packets_read < max_packets:
                    pkt_header = f.read(16)
                    if len(pkt_header) < 16:
                        break

                    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(endian + "IIII", pkt_header)
                    pkt_data = f.read(incl_len)
                    if len(pkt_data) < incl_len:
                        break

                    packets_read += 1

                    # Buscar flags en el payload crudo
                    matches = flag_re.findall(pkt_data)
                    for m in matches:
                        f_decoded = m.decode("ascii", errors="ignore")
                        if f_decoded not in found_flags:
                            found_flags.append(f_decoded)

                    # Intento de extracción IPv4 simple (Ethernet type 0x0800 en offset 12)
                    if len(pkt_data) >= 34 and pkt_data[12:14] == b"\x08\x00":
                        src_ip = ".".join(str(b) for b in pkt_data[26:30])
                        dst_ip = ".".join(str(b) for b in pkt_data[30:34])
                        ip_conversations[f"{src_ip} -> {dst_ip}"] += 1

                res = {
                    "packets_analyzed": packets_read,
                    "top_conversations": dict(ip_conversations.most_common(10)),
                    "potential_flags": found_flags,
                }
                return ToolResult(
                    success=True,
                    output=res,
                    raw_text=f"Paquetes analizados: {packets_read}. Conversaciones: {len(ip_conversations)}. Flags encontradas: {found_flags}",
                )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


# Registrar herramientas forenses
registry.register(MagicBytesInspectorTool)
registry.register(DeepStringsTool)
registry.register(ZipInspectorTool)
registry.register(PcapParserTool)
