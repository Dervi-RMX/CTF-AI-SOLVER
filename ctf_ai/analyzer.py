"""
Módulo de Análisis Inteligente de Retos CTF
Utiliza modelos de lenguaje para clasificar retos, diseñar estrategias y razonar paso a paso.
"""

import json
import re
from typing import Any, Dict, List, Optional
from ctf_ai.ai_providers import AIRouter
from ctf_ai.tools import find_flags


CTF_SYSTEM_PROMPT = """Eres CTF-AI Solver, un asistente experto y mentor en competiciones CTF (Capture The Flag) y ciberseguridad defensiva/analítica.
Tu objetivo es ayudar al usuario a razonar, analizar y resolver retos de diferentes categorías:
1. Criptografía (Crypto): Cifrados clásicos (César, Vigenère, ROT), modernos (RSA, AES, ECC), análisis de frecuencia, XOR, Diffie-Hellman.
2. Esteganografía (Stego): Metadatos EXIF, canales LSB en imágenes, strings ocultos, magic bytes corruptos.
3. Forense (Forensics): Análisis de capturas PCAP, dumps de memoria, sistemas de archivos, extracción de artefactos.
4. Web: Inspección de código fuente HTML/JS, cookies, cabeceras HTTP, lógica de APIs.
5. Ingeniería Inversa (Reversing): Desensamblado conceptual, cadenas de texto, descompilación en pseudocódigo.
6. Pwn / Binary: Análisis de protecciones de ejecutables (NX, ASLR, Canary, PIE), lógica de buffers.
7. Misc / OSINT: Codificaciones exóticas (Brainfuck, Morse, Base64/32/85/58), fuentes públicas de información.

DIRECTRICES:
- Explica de forma concisa tu razonamiento lógico y metodológico paso a paso.
- Cuando propongas un comando para la consola (PowerShell o bash), colócalo claramente en un bloque de código.
- Si detectas una flag (bandera) en formato flag{...}, ctf{...}, etc., resáltala inmediatamente.
- Prioriza soluciones elegantes y educativas.
"""


class CTFAnalyzer:
    """Motor analítico que interactúa con la IA para resolver retos."""

    def __init__(self, ai_router: AIRouter):
        self.router = ai_router

    def analyze_challenge(self, description: str, file_details: Optional[str] = None) -> Dict[str, Any]:
        """Realiza el análisis inicial del reto y propone una estrategia."""
        prompt = f"""Analiza el siguiente reto CTF y responde estructuradamente en español:

DESCRIPCIÓN DEL RETO:
{description}
"""
        if file_details:
            prompt += f"\nDETALLES DE ARCHIVOS ADJUNTOS:\n{file_details}\n"

        prompt += """
Por favor proporciona:
1. Categoría principal (Crypto / Web / Forensics / Stego / Reversing / Pwn / Misc / OSINT)
2. Nivel de dificultad estimado (Fácil / Medio / Difícil)
3. Observaciones y pistas clave detectadas
4. Plan de ataque recomendado (Paso a paso)
5. Primer paso concreto a ejecutar (comando o herramienta recomendada)
"""

        try:
            response = self.router.ask(
                prompt=prompt,
                system_prompt=CTF_SYSTEM_PROMPT,
            )

            # Detectar banderas iniciales si están en la descripción
            flags = find_flags(description)

            return {
                "raw_response": response,
                "found_flags": flags,
            }
        except Exception as e:
            return {
                "raw_response": f"Error al analizar el reto: {str(e)}",
                "found_flags": [],
            }

    def solve_step(
        self,
        context_summary: str,
        step_number: int,
        last_output: Optional[str] = None,
    ) -> str:
        """Determina la siguiente acción o deducción basándose en los resultados anteriores."""
        prompt = f"""Estamos resolviendo el reto (Paso {step_number}).

HISTORIAL Y CONTEXTO ACUMULADO:
{context_summary}
"""
        if last_output:
            prompt += f"\nÚLTIMO RESULTADO OBTENIDO:\n{last_output}\n"

        prompt += """
Evalúa el resultado anterior y determina:
1. ¿Qué información nueva o pista obtuvimos?
2. ¿Se descubrió la flag? Si es así, indícala claramente.
3. ¿Cuál es el siguiente paso exacto? Si se requiere ejecutar un comando en la terminal, inclúyelo en un bloque de código.
"""

        try:
            return self.router.ask(
                prompt=prompt,
                system_prompt=CTF_SYSTEM_PROMPT,
            )
        except Exception as e:
            return f"Error en la inferencia del paso {step_number}: {str(e)}"

    def consult(self, question: str, context: Optional[str] = None) -> str:
        """Permite hacer una pregunta libre sobre el reto actual."""
        try:
            return self.router.ask(
                prompt=question,
                system_prompt=CTF_SYSTEM_PROMPT,
                context=context,
            )
        except Exception as e:
            return f"Error al consultar al asistente: {str(e)}"
