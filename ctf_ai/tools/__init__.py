"""
Módulo de Herramientas Estructuradas de CTF-AI Solver Pro
Exporta el registro centralizado y asegura la carga de todas las familias de herramientas.
"""

from ctf_ai.tools.base import BaseTool, ToolResult, ToolRegistry, registry
import ctf_ai.tools.crypto
import ctf_ai.tools.forensics
import ctf_ai.tools.reversing
import ctf_ai.tools.web
import ctf_ai.tools.network

import base64
import codecs
import os
from pathlib import Path
import re
from typing import Dict, List, Optional


def decode_base64(data: str) -> str:
    """Decodifica una cadena Base64 (función de compatibilidad)."""
    try:
        cleaned = re.sub(r"\s+", "", data)
        return base64.b64decode(cleaned).decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error: {e}"


def encode_base64(data: str) -> str:
    """Codifica texto a Base64."""
    try:
        return base64.b64encode(data.encode("utf-8")).decode("utf-8")
    except Exception as e:
        return f"Error: {e}"


def decode_hex(data: str) -> str:
    """Decodifica una cadena hexadecimal a texto."""
    try:
        cleaned = re.sub(r"[^0-9a-fA-F]", "", data)
        return bytes.fromhex(cleaned).decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error: {e}"


def encode_hex(data: str) -> str:
    """Codifica texto a representación hexadecimal."""
    try:
        return data.encode("utf-8").hex()
    except Exception as e:
        return f"Error: {e}"


def rot13(text: str) -> str:
    """Aplica o revierte el cifrado ROT13."""
    return codecs.decode(text, "rot_13")


def caesar_bruteforce(text: str) -> Dict[int, str]:
    """Genera las 25 posibles rotaciones del cifrado César."""
    results = {}
    for shift in range(1, 26):
        shifted = []
        for c in text:
            if "a" <= c <= "z":
                shifted.append(chr((ord(c) - ord("a") + shift) % 26 + ord("a")))
            elif "A" <= c <= "Z":
                shifted.append(chr((ord(c) - ord("A") + shift) % 26 + ord("A")))
            else:
                shifted.append(c)
        results[shift] = "".join(shifted)
    return results


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    """Descifra cifrado Vigenère con la clave proporcionada."""
    if not key:
        return ciphertext
    res = []
    key_clean = [ord(k.lower()) - ord("a") for k in key if k.isalpha()]
    if not key_clean:
        return ciphertext
    key_idx = 0
    for c in ciphertext:
        if "a" <= c <= "z":
            shift = key_clean[key_idx % len(key_clean)]
            res.append(chr((ord(c) - ord("a") - shift) % 26 + ord("a")))
            key_idx += 1
        elif "A" <= c <= "Z":
            shift = key_clean[key_idx % len(key_clean)]
            res.append(chr((ord(c) - ord("A") - shift) % 26 + ord("A")))
            key_idx += 1
        else:
            res.append(c)
    return "".join(res)


def from_binary(data: str) -> str:
    """Convierte cadena de ceros y unos a texto ASCII."""
    try:
        cleaned = re.sub(r"[^01]", "", data)
        bytes_list = [int(cleaned[i : i + 8], 2) for i in range(0, len(cleaned), 8) if len(cleaned[i : i + 8]) == 8]
        return bytes(bytes_list).decode("utf-8", errors="replace")
    except Exception as e:
        return f"Error: {e}"


MORSE_DICT = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E",
    "..-.": "F", "--.": "G", "....": "H", "..": "I", ".---": "J",
    "-.-": "K", ".-..": "L", "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X", "-.--": "Y",
    "--..": "Z", "-----": "0", ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6", "--...": "7", "---..": "8",
    "----.": "9",
}


def from_morse(data: str) -> str:
    """Decodifica código Morse delimitado por espacios."""
    words = data.strip().split("   ")
    decoded_words = []
    for word in words:
        letters = word.split()
        decoded_letters = [MORSE_DICT.get(letter, "?") for letter in letters]
        decoded_words.append("".join(decoded_letters))
    return " ".join(decoded_words)


def identify_hash(hash_str: str) -> List[str]:
    """Identifica algoritmos posibles para un hash hexadecimal."""
    h = hash_str.strip()
    length = len(h)
    if length == 32:
        return ["MD5", "NTLM"]
    elif length == 40:
        return ["SHA-1"]
    elif length == 64:
        return ["SHA-256"]
    elif length == 128:
        return ["SHA-512"]
    return ["Hash no identificado"]


def find_flags(text: str) -> List[str]:
    """Busca patrones de banderas CTF en el texto."""
    return re.findall(r"(?:flag|ctf|picoctf|htb|thm)\{[^}]+\}", text, re.IGNORECASE)


def analyze_file_magic(file_path: str) -> str:
    """Ejecuta inspección de magic bytes delegando en el registro."""
    res = registry.execute_tool("magic_inspector", file_path=file_path)
    return res.raw_text if res.success else res.error or "Error"


def extract_strings(file_path: str, min_len: int = 4, max_results: int = 30) -> List[str]:
    """Extrae cadenas ASCII y UTF-16."""
    res = registry.execute_tool("deep_strings", file_path=file_path, min_len=min_len)
    if res.success and isinstance(res.output, dict):
        return res.output.get("preview_sample", [])[:max_results]
    return []


def extract_exif_metadata(file_path: str) -> str:
    """Inspección básica de metadatos."""
    p = Path(file_path.strip("\"'"))
    if not p.exists():
        return f"Archivo no existe: {file_path}"
    stat = p.stat()
    return f"Tamaño: {stat.st_size} bytes | Modificado: {stat.st_mtime}"


def analyze_url(url: str) -> str:
    """Inspecciona cabeceras web delegando en el registro."""
    res = registry.execute_tool("web_headers", url=url)
    return res.raw_text if res.success else res.error or "Error"


def reverse_string(text: str) -> str:
    """Invierte una cadena de texto."""
    return text[::-1]


__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "registry",
    "decode_base64",
    "encode_base64",
    "decode_hex",
    "encode_hex",
    "rot13",
    "caesar_bruteforce",
    "vigenere_decrypt",
    "from_binary",
    "from_morse",
    "identify_hash",
    "find_flags",
    "analyze_file_magic",
    "extract_strings",
    "extract_exif_metadata",
    "analyze_url",
    "reverse_string",
]
