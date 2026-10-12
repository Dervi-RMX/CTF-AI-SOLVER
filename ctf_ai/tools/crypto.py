"""
Herramientas Criptográficas y de Decodificación Estructuradas para CTF-AI Solver Pro
Incluye multi-decodificador recursivo, análisis estadístico (IoC, Entropía),
cifrados clásicos, identificación de hashes y ataques matemáticos para RSA.
"""

import base64
import collections
import math
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from ctf_ai.tools.base import BaseTool, ToolResult, registry


import codecs

class MultiDecoderTool(BaseTool):
    """Herramienta heurística que desanida capas sucesivas de codificaciones comunes."""

    name = "multi_decoder"
    description = "Intenta decodificar heurísticamente texto con capas múltiples (Base64, Hex, URL, ROT13)"
    category = "crypto"
    arguments_schema = {
        "text": {"type": "str", "required": False, "default": "", "help": "Texto cifrado o codificado"},
        "data": {"type": "str", "required": False, "default": "", "help": "Alias para text"},
        "max_layers": {"type": "int", "required": False, "default": 5, "help": "Límite de capas"},
    }

    def execute(self, text: str = "", data: str = "", max_layers: int = 5) -> ToolResult:
        input_str = text or data
        if not input_str:
            return ToolResult(success=False, error="Falta argumento requerido: 'text' o 'data'")

        current = input_str.strip()
        chain = []
        visited = set([current])
        codecs_found = {}

        for layer in range(max_layers):
            decoded = None
            method_used = None

            # 1. Probar URL decode si contiene %
            if "%" in current:
                cand = urllib.parse.unquote(current)
                if cand != current:
                    decoded = cand
                    method_used = "URL-Decode"
                    codecs_found["url"] = cand

            # 2. Probar Base64 si parece b64
            if not decoded:
                cleaned_b64 = re.sub(r"\s+", "", current)
                if re.match(r"^[A-Za-z0-9+/=]+$", cleaned_b64) and len(cleaned_b64) % 4 == 0 and len(cleaned_b64) > 4:
                    try:
                        raw = base64.b64decode(cleaned_b64)
                        cand = raw.decode("utf-8")
                        if cand.isprintable() and len(cand) > 0 and cand != current:
                            decoded = cand
                            method_used = "Base64"
                            codecs_found["base64"] = cand
                    except Exception:
                        pass

            # 3. Probar Hexadecimal si es puramente hex
            if not decoded:
                cleaned_hex = re.sub(r"[^0-9a-fA-F]", "", current)
                if len(cleaned_hex) >= 4 and len(cleaned_hex) % 2 == 0 and re.match(r"^[0-9a-fA-F]+$", cleaned_hex):
                    try:
                        raw = bytes.fromhex(cleaned_hex)
                        cand = raw.decode("utf-8")
                        if cand.isprintable() and len(cand) > 0 and cand != current:
                            decoded = cand
                            method_used = "Hex"
                            codecs_found["hex"] = cand
                    except Exception:
                        pass

            # 4. Probar ROT13 si genera una bandera reconocida
            if not decoded:
                try:
                    cand = codecs.decode(current, "rot_13")
                    if re.search(r"(?:flag|ctf|picoctf)\{", cand, re.IGNORECASE):
                        decoded = cand
                        method_used = "ROT13"
                        codecs_found["rot13"] = cand
                except Exception:
                    pass

            if decoded and decoded not in visited:
                chain.append(f"Capa {layer+1} ({method_used}): {decoded[:100]}")
                visited.add(decoded)
                current = decoded
                # Si encontramos un flag conocido, detener la cadena
                if re.search(r"flag\{|ctf\{", current, re.IGNORECASE):
                    break
            else:
                break

        res_dict = {
            "layers": chain,
            "final_text": current,
            **codecs_found,
        }

        if not chain:
            return ToolResult(
                success=True,
                output={**res_dict, "status": "Sin cambios detectables"},
                raw_text=f"No se pudieron desanidar capas automáticas: {current}",
            )

        return ToolResult(
            success=True,
            output=res_dict,
            raw_text="\n".join(chain) + f"\nResultado final: {current}",
        )


class StatisticalAnalysisTool(BaseTool):
    """Calcula entropía de Shannon e Índice de Coincidencia (IoC) para identificar tipo de cifrado."""

    name = "crypto_stats"
    description = "Calcula entropía de Shannon e Índice de Coincidencia (IoC) para identificar mono/polialfabéticos"
    category = "crypto"
    arguments_schema = {
        "text": {"type": "str", "required": True, "help": "Texto a evaluar"},
    }

    def execute(self, text: str) -> ToolResult:
        if not text:
            return ToolResult(success=False, error="Texto vacío")

        # 1. Entropía de Shannon
        entropy = 0.0
        length = len(text)
        counts = collections.Counter(text)
        for count in counts.values():
            p_x = count / length
            entropy += -p_x * math.log2(p_x)

        # 2. Índice de Coincidencia (IoC) solo sobre letras
        letters = [c.upper() for c in text if c.isalpha()]
        n = len(letters)
        ioc = 0.0
        if n > 1:
            letter_counts = collections.Counter(letters)
            numerator = sum(count * (count - 1) for count in letter_counts.values())
            ioc = numerator / (n * (n - 1))

        # Diagnóstico aproximado
        diag = "Indeterminado"
        if ioc >= 0.060:
            diag = "Probable texto plano o cifrado monoalfabético (César, Sustitución simple)"
        elif 0.040 <= ioc < 0.060:
            diag = "Probable cifrado polialfabético (Vigenère) o texto con alta aleatoriedad"
        elif ioc < 0.040:
            diag = "Probable texto comprimido, hashes o datos de alta entropía (XOR/AES)"

        res = {
            "entropy": round(entropy, 3),
            "shannon_entropy": round(entropy, 3),
            "ioc": round(ioc, 4),
            "index_of_coincidence": round(ioc, 4),
            "total_chars": length,
            "letters_count": n,
            "diagnosis": diag,
        }
        return ToolResult(
            success=True,
            output=res,
            raw_text=f"Entropía: {res['entropy']} bits/char | IoC: {res['ioc']} | Diagnóstico: {diag}",
        )


class RsaMathTool(BaseTool):
    """Ataques matemáticos clásicos para retos CTF de RSA."""

    name = "rsa_math"
    description = "Ataques de resolución RSA (small e = 3 con raíz cúbica exacta, factorización de Fermat)"
    category = "crypto"
    arguments_schema = {
        "n": {"type": "int", "required": True, "help": "Módulo N"},
        "e": {"type": "int", "required": False, "default": 65537, "help": "Exponente público e"},
        "c": {"type": "int", "required": False, "default": 0, "help": "Texto cifrado c (opcional si sólo se desea factorizar)"},
        "action": {"type": "str", "required": False, "default": "", "help": "Acción específica (opcional)"},
    }

    def execute(self, n: int, c: int = 0, e: int = 65537, action: str = "") -> ToolResult:
        n = int(n)
        c = int(c) if c else 0
        e = int(e)

        # 1. Ataque small e: si e == 3 (o c != 0 y m^3 < n), m = int(c^(1/3))
        if e == 3 or action == "small_e_cube_root":
            if c > 0:
                low = 0
                high = c
                root = None
                while low <= high:
                    mid = (low + high) // 2
                    cubed = mid ** 3
                    if cubed == c:
                        root = mid
                        break
                    elif cubed < c:
                        low = mid + 1
                    else:
                        high = mid - 1

                if root:
                    # Convertir a texto si es posible
                    m_str = ""
                    try:
                        num_bytes = (root.bit_length() + 7) // 8
                        m_bytes = root.to_bytes(num_bytes, "big")
                        m_str = m_bytes.decode("utf-8", errors="replace")
                    except Exception:
                        pass

                    return ToolResult(
                        success=True,
                        output={
                            "method": "Small e = 3 raíz cúbica exacta",
                            "m_int": root,
                            "recovered_m": root,
                            "plaintext": m_str,
                        },
                        raw_text=f"RSA Descifrado (Small e): {m_str or root}",
                    )

        # 2. Ataque de Fermat (para primos p y q muy cercanos)
        # n = a^2 - b^2 => a = ceil(sqrt(n))
        a = math.isqrt(n)
        if a * a < n:
            a += 1

        for _ in range(100000):  # Probar hasta 100k pasos
            b2 = a * a - n
            if b2 >= 0:
                b = math.isqrt(b2)
                if b * b == b2:
                    p = a - b
                    q = a + b
                    if p > 1 and q > 1 and p * q == n:
                        m_str = ""
                        if c > 0:
                            phi = (p - 1) * (q - 1)
                            try:
                                d = pow(e, -1, phi)
                                m = pow(c, d, n)
                                num_bytes = (m.bit_length() + 7) // 8
                                m_bytes = m.to_bytes(num_bytes, "big")
                                m_str = m_bytes.decode("utf-8", errors="replace")
                            except Exception:
                                pass

                        return ToolResult(
                            success=True,
                            output={"method": "Factorización de Fermat", "p": p, "q": q, "plaintext": m_str},
                            raw_text=f"RSA Descifrado (Fermat): p={p}, q={q} {m_str}",
                        )
            a += 1

        return ToolResult(
            success=False,
            error="No se pudo resolver RSA con métodos automáticos rápidos (Small e / Fermat).",
        )


# Registrar herramientas en el registry global
registry.register(MultiDecoderTool)
registry.register(StatisticalAnalysisTool)
registry.register(RsaMathTool)
