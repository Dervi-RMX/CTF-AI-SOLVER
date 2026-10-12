"""
Módulo de Herramientas de Análisis y Criptografía para CTF
Contiene funciones de decodificación, criptoanálisis, esteganografía y análisis forense.
"""

import base64
import binascii
import collections
import os
import re
import socket
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


# ==========================================
# 1. CODIFICACIONES Y CIFRADOS CLÁSICOS
# ==========================================

def decode_base64(text: str) -> str:
    """Decodifica una cadena Base64 a texto legible o hex si es binario."""
    cleaned = "".join(text.split())
    # Agregar padding si es necesario
    missing_padding = len(cleaned) % 4
    if missing_padding:
        cleaned += "=" * (4 - missing_padding)

    try:
        raw_bytes = base64.b64decode(cleaned)
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Binario / Hex]: {raw_bytes.hex()}"
    except Exception as e:
        return f"[Error decodificando Base64]: {str(e)}"


def encode_base64(text: str) -> str:
    """Codifica texto a Base64."""
    try:
        return base64.b64encode(text.encode("utf-8")).decode("utf-8")
    except Exception as e:
        return f"[Error codificando Base64]: {str(e)}"


def decode_hex(hex_str: str) -> str:
    """Convierte una cadena hexadecimal a texto UTF-8 o representación legible."""
    cleaned = re.sub(r"[^0-9a-fA-F]", "", hex_str)
    if len(cleaned) % 2 != 0:
        cleaned = "0" + cleaned

    try:
        raw_bytes = bytes.fromhex(cleaned)
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Binario]: {raw_bytes.hex()}"
    except Exception as e:
        return f"[Error decodificando Hex]: {str(e)}"


def encode_hex(text: str) -> str:
    """Convierte texto en su representación hexadecimal."""
    return text.encode("utf-8").hex()


def rot_n(text: str, n: int) -> str:
    """Aplica rotación César de N posiciones al texto manteniendo mayúsculas y minúsculas."""
    result = []
    n = n % 26
    for char in text:
        if "a" <= char <= "z":
            result.append(chr((ord(char) - ord("a") + n) % 26 + ord("a")))
        elif "A" <= char <= "Z":
            result.append(chr((ord(char) - ord("A") + n) % 26 + ord("A")))
        else:
            result.append(char)
    return "".join(result)


def rot13(text: str) -> str:
    """Decodifica o codifica ROT13."""
    return rot_n(text, 13)


def caesar_bruteforce(text: str) -> Dict[int, str]:
    """Genera las 25 posibles rotaciones del cifrado César."""
    results = {}
    for shift in range(1, 26):
        results[shift] = rot_n(text, shift)
    return results


def xor_data(data: bytes, key: bytes) -> bytes:
    """Aplica operación XOR entre datos y una clave repetida."""
    if not key:
        return data
    key_len = len(key)
    return bytes(b ^ key[i % key_len] for i, b in enumerate(data))


def xor_decrypt_text(ciphertext_hex: str, key_str: str) -> str:
    """Descifra datos hexadecimales usando una clave en texto vía XOR."""
    try:
        cipher_bytes = bytes.fromhex(re.sub(r"[^0-9a-fA-F]", "", ciphertext_hex))
        key_bytes = key_str.encode("utf-8")
        decrypted = xor_data(cipher_bytes, key_bytes)
        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            return f"[Hex]: {decrypted.hex()}"
    except Exception as e:
        return f"[Error en XOR]: {str(e)}"


def vigenere_cipher(text: str, key: str, decrypt: bool = False) -> str:
    """Aplica cifrado o descifrado Vigenère."""
    if not key:
        return text

    key = key.lower()
    key_indices = [ord(k) - ord("a") for k in key if "a" <= k <= "z"]
    if not key_indices:
        return text

    result = []
    key_idx = 0
    k_len = len(key_indices)

    for char in text:
        shift = key_indices[key_idx % k_len]
        if decrypt:
            shift = -shift

        if "a" <= char <= "z":
            result.append(chr((ord(char) - ord("a") + shift) % 26 + ord("a")))
            key_idx += 1
        elif "A" <= char <= "Z":
            result.append(chr((ord(char) - ord("A") + shift) % 26 + ord("A")))
            key_idx += 1
        else:
            result.append(char)

    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """Descifra texto cifrado con Vigenère usando una clave."""
    return vigenere_cipher(text, key, decrypt=True)


def reverse_string(text: str) -> str:
    """Invierte una cadena de texto."""
    return text[::-1]


def to_binary(text: str) -> str:
    """Convierte texto en una cadena de bits (8 bits por caracter)."""
    return " ".join(f"{ord(c):08b}" for c in text)


def from_binary(binary_str: str) -> str:
    """Convierte una cadena de bits separada por espacios o continua a texto."""
    cleaned = re.sub(r"[^01]", "", binary_str)
    if len(cleaned) % 8 != 0:
        # Intentar con bloques de 7 bits si 8 no encaja
        if len(cleaned) % 7 == 0:
            chars = [chr(int(cleaned[i : i + 7], 2)) for i in range(0, len(cleaned), 7)]
            return "".join(chars)
        return "[Error]: La longitud de bits no es múltiplo de 8 ni de 7."

    chars = [chr(int(cleaned[i : i + 8], 2)) for i in range(0, len(cleaned), 8)]
    return "".join(chars)


# Código Morse
MORSE_MAP = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..", "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.", " ": "/"
}
REVERSE_MORSE = {v: k for k, v in MORSE_MAP.items()}


def to_morse(text: str) -> str:
    """Codifica texto a código Morse."""
    upper = text.upper()
    return " ".join(MORSE_MAP.get(c, "?") for c in upper)


def from_morse(morse_code: str) -> str:
    """Decodifica código Morse a texto legible."""
    tokens = morse_code.strip().split()
    decoded = []
    for token in tokens:
        if token == "/":
            decoded.append(" ")
        else:
            decoded.append(REVERSE_MORSE.get(token, "?"))
    return "".join(decoded)


# ==========================================
# 2. CRIPTOANÁLISIS Y HASHING
# ==========================================

def frequency_analysis(text: str) -> Dict[str, float]:
    """Calcula la frecuencia porcentual de cada letra en el texto."""
    letters = [c.upper() for c in text if c.isalpha()]
    total = len(letters)
    if total == 0:
        return {}

    counts = collections.Counter(letters)
    return {char: round((count / total) * 100, 2) for char, count in counts.most_common()}


def identify_hash(hash_str: str) -> List[str]:
    """Identifica el posible algoritmo de un hash basado en longitud y caracteres."""
    cleaned = hash_str.strip().lower()
    length = len(cleaned)
    is_hex = bool(re.match(r"^[0-9a-f]+$", cleaned))

    possibilities = []

    if is_hex:
        if length == 32:
            possibilities.extend(["MD5", "NTLM", "MD4"])
        elif length == 40:
            possibilities.extend(["SHA-1", "RIPEMD-160"])
        elif length == 56:
            possibilities.append("SHA-224")
        elif length == 64:
            possibilities.extend(["SHA-256", "Keccak-256", "Blake2s"])
        elif length == 96:
            possibilities.append("SHA-384")
        elif length == 128:
            possibilities.extend(["SHA-512", "Whirlpool", "Blake2b"])

    if cleaned.startswith("$2a$") or cleaned.startswith("$2b$") or cleaned.startswith("$2y$"):
        possibilities.append("Bcrypt")
    elif cleaned.startswith("$6$") and len(cleaned) > 80:
        possibilities.append("SHA-512 Crypt (Linux)")
    elif cleaned.startswith("$1$"):
        possibilities.append("MD5 Crypt (Linux)")
    elif cleaned.startswith("$5$"):
        possibilities.append("SHA-256 Crypt (Linux)")

    if not possibilities:
        possibilities.append("Desconocido / Criptograma personalizado")

    return possibilities


# ==========================================
# 3. FORENSE Y ANÁLISIS DE ARCHIVOS
# ==========================================

FILE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "PNG Image",
    b"\xff\xd8\xff": "JPEG Image",
    b"GIF87a": "GIF87a Image",
    b"GIF89a": "GIF89a Image",
    b"PK\x03\x04": "ZIP Archive / DOCX / APK / JAR",
    b"\x1f\x8b\x08": "GZIP Archive",
    b"BZh": "BZIP2 Archive",
    b"7z\xbc\xaf\x27\x1c": "7-Zip Archive",
    b"Rar!\x1a\x07": "RAR Archive",
    b"%PDF": "PDF Document",
    b"\x7fELF": "ELF Executable (Linux)",
    b"MZ": "PE Executable / DLL (Windows DOS MZ)",
    b"\xca\xfe\xba\xbe": "Java Class / Mach-O Fat Binary",
    b"OggS": "OGG Audio/Video Container",
    b"RIFF": "RIFF (WAV / AVI / WEBP)",
    b"SQLite format 3\x00": "SQLite Database",
}


def analyze_file_magic(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Inspecciona los primeros bytes (magic numbers) de un archivo para identificar su tipo real."""
    p = Path(file_path)
    if not p.exists():
        return {"error": f"El archivo {p} no existe."}

    file_size = p.stat().st_size
    try:
        with open(p, "rb") as f:
            header = f.read(32)

        matched_type = "Desconocido / Datos binarios genéricos"
        for sig, desc in FILE_SIGNATURES.items():
            if header.startswith(sig):
                matched_type = desc
                break

        return {
            "file": p.name,
            "size_bytes": file_size,
            "header_hex": header[:16].hex(),
            "detected_type": matched_type,
        }
    except Exception as e:
        return {"error": str(e)}


def extract_strings(file_path: Union[str, Path], min_len: int = 4, max_results: int = 100) -> List[str]:
    """Extrae cadenas ASCII legibles de longitud mínima desde un archivo binario."""
    p = Path(file_path)
    if not p.exists():
        return [f"[Error]: Archivo no encontrado: {p}"]

    try:
        with open(p, "rb") as f:
            data = f.read()

        pattern = re.compile(rb"[\x20-\x7e]{" + str(min_len).encode() + rb",}")
        matches = pattern.findall(data)
        decoded = [m.decode("ascii", errors="ignore") for m in matches[:max_results]]
        return decoded
    except Exception as e:
        return [f"[Error extrayendo cadenas]: {str(e)}"]


def extract_exif_metadata(image_path: Union[str, Path]) -> Dict[str, Any]:
    """Extrae metadatos EXIF de una imagen usando Pillow si está disponible."""
    p = Path(image_path)
    if not p.exists():
        return {"error": f"El archivo {p} no existe."}

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        img = Image.open(p)
        info = img.getexif()
        if not info:
            return {"status": "No se encontraron metadatos EXIF"}

        metadata = {}
        for tag_id, value in info.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            metadata[tag_name] = str(value)
        return metadata
    except ImportError:
        return {"error": "Librería Pillow no instalada."}
    except Exception as e:
        return {"error": f"Error leyendo EXIF: {str(e)}"}


# ==========================================
# 4. RED Y WEB (UTILIDADES DEFENSIVAS)
# ==========================================

def dns_lookup(domain: str) -> Dict[str, Any]:
    """Resuelve registros DNS A básicos de un dominio."""
    domain = domain.strip().replace("http://", "").replace("https://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "ip": ip, "status": "Resuelto con éxito"}
    except Exception as e:
        return {"domain": domain, "error": str(e)}


def analyze_url(url: str) -> Dict[str, Any]:
    """Obtiene los encabezados HTTP, título y comentarios HTML de una URL de reto CTF."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url

    try:
        import requests
        from bs4 import BeautifulSoup

        resp = requests.get(url, timeout=10, headers={"User-Agent": "CTF-AI-Solver/1.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "Sin título"
        # Extraer comentarios HTML que frecuentemente contienen pistas en retos Web
        comments = [c.strip() for c in soup.find_all(string=lambda text: isinstance(text, str) and "<!--" in text)]

        return {
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "title": title,
            "html_comments": comments[:10],
            "body_snippet": resp.text[:500],
        }
    except Exception as e:
        return {"error": f"Error conectando a URL: {str(e)}"}


# ==========================================
# 5. DETECCIÓN DE FLAGS (PATRONES COMUNES)
# ==========================================

FLAG_PATTERNS = [
    re.compile(r"flag\{[^}]+\}", re.IGNORECASE),
    re.compile(r"ctf\{[^}]+\}", re.IGNORECASE),
    re.compile(r"picoctf\{[^}]+\}", re.IGNORECASE),
    re.compile(r"htb\{[^}]+\}", re.IGNORECASE),
    re.compile(r"thm\{[^}]+\}", re.IGNORECASE),
    re.compile(r"dc\{[^}]+\}", re.IGNORECASE),
]


def find_flags(text: str) -> List[str]:
    """Busca banderas (flags) típicas de CTF dentro de cualquier texto o salida."""
    found = []
    for pattern in FLAG_PATTERNS:
        matches = pattern.findall(text)
        for m in matches:
            if m not in found:
                found.append(m)
    return found
