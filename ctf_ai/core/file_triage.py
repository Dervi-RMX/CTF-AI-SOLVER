"""
Módulo de Triaje Inteligente de Archivos Locales para CTF-AI Solver Pro.
Inspecciona tanto archivos de texto plano como binarios (imágenes, ejecutables, pcap, zips).
Extrae metadatos, hashes MD5/SHA256, cadenas clave y busca banderas automáticamente.
"""

import hashlib
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

import ctf_ai.tools as ctf_tools

FLAG_REGEX = re.compile(r"(?:flag|ctf|picoctf|htb|thm)\{[^}]+\}", re.IGNORECASE)


def format_size(size_bytes: int) -> str:
    """Retorna tamaño formateado en B, KB, MB, GB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_binary_content(byte_data: bytes) -> bool:
    """Determina si un buffer de bytes corresponde a un binario o texto plano."""
    if not byte_data:
        return False
    # Si contiene bytes nulos en los primeros 8KB, es binario
    if b"\x00" in byte_data[:8192]:
        return True
    # Comprobar porcentaje de caracteres no imprimibles
    non_text = byte_data[:1024].translate(None, bytes(range(32, 127)) + b"\n\r\t\b")
    return len(non_text) / max(len(byte_data[:1024]), 1) > 0.30


def triage_local_file(file_path: Union[Path, str]) -> Dict[str, Any]:
    """
    Realiza un triaje forense y estructural completo sobre un archivo local del sistema.
    """
    p = Path(str(file_path).strip("\"'"))
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"El archivo no existe o no es accesible: {p}")

    size_bytes = p.stat().st_size
    size_str = format_size(size_bytes)

    # Calcular hashes SHA-256 y MD5
    hasher_sha = hashlib.sha256()
    hasher_md5 = hashlib.md5()
    header = b""

    with open(p, "rb") as f:
        header = f.read(8192)
        hasher_sha.update(header)
        hasher_md5.update(header)
        while chunk := f.read(65536):
            hasher_sha.update(chunk)
            hasher_md5.update(chunk)

    sha256_hash = hasher_sha.hexdigest()
    md5_hash = hasher_md5.hexdigest()

    # Detección de binario
    is_binary = is_binary_content(header)

    # Inspección de magic bytes
    magic_info = ctf_tools.analyze_file_magic(str(p))

    found_flags: List[str] = []
    text_content = ""
    preview_strings: List[str] = []

    if not is_binary:
        # Archivo de texto plano o código fuente
        try:
            text_content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            text_content = header.decode("utf-8", errors="replace")
        found_flags.extend(FLAG_REGEX.findall(text_content))
    else:
        # Archivo binario (ELF, PE, PCAP, imagen, ZIP)
        strings_list = ctf_tools.extract_strings(str(p), min_len=4, max_results=50)
        preview_strings = strings_list[:15]
        for s in strings_list:
            matches = FLAG_REGEX.findall(s)
            for m in matches:
                if m not in found_flags:
                    found_flags.append(m)

        # Buscar banderas también en el header crudo
        try:
            raw_header_text = header.decode("latin-1", errors="ignore")
            for m in FLAG_REGEX.findall(raw_header_text):
                if m not in found_flags:
                    found_flags.append(m)
        except Exception:
            pass

    return {
        "path": str(p.resolve()),
        "name": p.name,
        "extension": p.suffix.lower(),
        "size_bytes": size_bytes,
        "size_str": size_str,
        "is_binary": is_binary,
        "file_type": magic_info,
        "sha256": sha256_hash,
        "md5": md5_hash,
        "found_flags": list(dict.fromkeys(found_flags)),  # Deduplicar
        "text_preview": text_content[:1500] if text_content else "",
        "strings_preview": preview_strings,
    }
