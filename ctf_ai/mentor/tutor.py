"""
Tutor Socrático Pedagógico para Cybersecurity Study Mentor
Proporciona explicaciones didácticas, pistas progresivas graduadas sin desvelar la solución de inmediato,
diagnóstico de errores y preguntas de práctica (drills) para afianzar competencias reales.
"""

from typing import Any, Dict, List, Optional
from ctf_ai.ai_providers import AIRouter


SOCRATIC_PROMPT = """Eres el Tutor Socrático de CTF-AI Solver Pro, un mentor pedagógico especializado en ciberseguridad.
Tus principios educativos son:
1. NUNCA reveles la respuesta o bandera directamente si el alumno está resolviendo un reto; dale PISTAS PROGRESIVAS graduadas (Nivel 1: pista sutil/conceptual, Nivel 2: herramienta o vector a mirar, Nivel 3: metodología exacta).
2. Explica los ERRORES conceptuales con paciencia y conecta la teoría con escenarios del mundo real.
3. Propón preguntas de autoevaluación (drills) desafiantes pero alcanzables.
4. Fomenta el razonamiento analítico y el aprendizaje basado en evidencias.
"""


import random

OFFLINE_DRILLS = [
    {
        "category": "redes",
        "question": "¿Cuál es la función principal del protocolo ARP (Address Resolution Protocol) en una red local?",
        "options": [
            "A) Traducir nombres de dominio legibles (FQDN) a direcciones IP públicas.",
            "B) Mapear una dirección de capa de red (IPv4) a una dirección física de enlace (MAC).",
            "C) Asignar dinámicamente configuraciones de red mediante concesiones temporales.",
            "D) Encriptar el tráfico transmitido entre conmutadores (switches) de capa 2.",
        ],
        "answer": "B",
        "explanation": "ARP resuelve direcciones lógicas IP (Capa 3) a direcciones físicas MAC (Capa 2) para permitir la entrega de tramas Ethernet en el mismo segmento local.",
    },
    {
        "category": "web",
        "question": "En una vulnerabilidad SQL Injection (SQLi), ¿qué técnica permite extraer información cuando la aplicación no devuelve datos en la respuesta HTTP ni mensajes de error?",
        "options": [
            "A) Inyección basada en Uniones (UNION-based SQLi).",
            "B) Inyección fuera de banda o ciega basada en tiempo (Time-based Blind SQLi).",
            "C) Inyección reflejada de cabeceras Host.",
            "D) Desbordamiento de búfer en el motor de base de datos.",
        ],
        "answer": "B",
        "explanation": "Cuando no hay salida visual ni errores, se utilizan pausas condicionales (como SLEEP() o pg_sleep()) para inferir datos carácter a carácter mediante el tiempo de respuesta del servidor.",
    },
    {
        "category": "linux",
        "question": "¿Qué permiso especial en Linux permite que un archivo ejecutable se ejecute con los privilegios del propietario del archivo en lugar de los del usuario actual?",
        "options": [
            "A) Sticky Bit (t)",
            "B) SGID (Set Group ID)",
            "C) SUID (Set User ID)",
            "D) Permiso Inmutable (chattr +i)",
        ],
        "answer": "C",
        "explanation": "El bit SUID (valor octal 4000) hace que el binario se ejecute con los permisos de su propietario (frecuentemente root), siendo un vector clásico de escalada de privilegios si está mal configurado.",
    },
    {
        "category": "criptografía",
        "question": "¿Cuál es la principal debilidad del modo de operación ECB (Electronic Codebook) en el cifrado por bloques como AES?",
        "options": [
            "A) Requiere claves asimétricas de longitud superior a 4096 bits.",
            "B) Bloques idénticos de texto plano producen bloques idénticos de texto cifrado, preservando patrones visuales.",
            "C) No permite descifrado paralelo en procesadores modernos.",
            "D) Requiere un vector de inicialización (IV) de tamaño variable.",
        ],
        "answer": "B",
        "explanation": "En ECB no hay difusión entre bloques: si dos bloques de entrada son iguales, sus bloques cifrados también lo son, revelando la estructura de los datos (el famoso 'pingüino de Tux').",
    },
    {
        "category": "forense",
        "question": "¿Cuáles son los primeros 8 bytes mágicos (Magic Bytes) característicos de un archivo de imagen en formato PNG?",
        "options": [
            "A) 50 4B 03 04 14 00 00 00 (PK..)",
            "B) FF D8 FF E0 00 10 4A 46",
            "C) 89 50 4E 47 0D 0A 1A 0A (.PNG....)",
            "D) 7F 45 4C 46 02 01 01 00 (.ELF....)",
        ],
        "answer": "C",
        "explanation": "Los archivos PNG siempre comienzan con la firma hexadecimal 89 50 4E 47 0D 0A 1A 0A para verificar integridad y prevenir corrupción de caracteres de salto de línea.",
    },
]


class SocraticTutor:
    """Tutor interactivo para aprendizaje guiado y resolución socrática de dudas."""

    def __init__(self, ai_router: AIRouter):
        self.router = ai_router

    def give_hint(self, challenge_context: str, hint_level: int = 1) -> str:
        """
        Genera una pista progresiva:
        Nivel 1: Concepto y dirección general.
        Nivel 2: Vector de ataque o formato a inspeccionar.
        Nivel 3: Herramienta o técnica concreta recomendada.
        """
        hint_level = max(1, min(3, int(hint_level)))
        prompt = f"""El estudiante está trabajando en el siguiente reto y solicita una pista de nivel {hint_level}/3.

CONTEXTO DEL RETO:
{challenge_context}

INSTRUCCIONES PARA LA PISTA (Nivel {hint_level}):
- Nivel 1: No menciones herramientas específicas; orienta la atención hacia la naturaleza de la información.
- Nivel 2: Sugiere el vector o familia de herramientas adecuada sin dar la solución.
- Nivel 3: Sugiere la herramienta o paso técnico exacto, pero NUNCA des la flag o contraseña final.
"""
        try:
            return self.router.ask(prompt=prompt, system_prompt=SOCRATIC_PROMPT)
        except Exception as e:
            return f"💡 Pista pedagógica (Modo Local): Revisa con detenimiento las firmas de datos o cadenas legibles del artefacto. ({str(e)})"

    def explain_concept(self, topic: str) -> str:
        """Explica un concepto de ciberseguridad con analogía, teoría y ejemplo práctico."""
        prompt = f"""Explica didácticamente el concepto '{topic}' en español:
1. ¿Qué es y qué problema resuelve o qué riesgo representa?
2. Ejemplo práctico o comando representativo.
3. ¿Cómo suele aparecer en competiciones CTF o auditorías de seguridad?
"""
        return self.router.ask(prompt=prompt, system_prompt=SOCRATIC_PROMPT)

    def get_offline_quiz_question(self, topic: str = "general") -> str:
        """Obtiene una pregunta curada del banco local cuando no hay cuota de API disponible."""
        topic_lower = topic.lower()
        candidates = [d for d in OFFLINE_DRILLS if d["category"] in topic_lower or topic_lower in d["category"]]
        drill = random.choice(candidates) if candidates else random.choice(OFFLINE_DRILLS)

        lines = [
            f"🧠 **Drill Técnico (Banco Offline):** {drill['question']}",
            "",
            *[f"  {opt}" for opt in drill["options"]],
            "",
            "*(Para verificar tu respuesta, piensa en la opción y escribe tu análisis o consúltala con el tutor)*",
            "",
            f"<!-- Respuesta correcta: {drill['answer']} | Explicación: {drill['explanation']} -->",
        ]
        return "\n".join(lines)

    def generate_quiz_question(self, topic: str = "general") -> str:
        """Genera una pregunta de práctica tipo certificación o entrevista técnica."""
        prompt = f"""Genera una pregunta técnica de práctica sobre '{topic}' con 4 opciones (A, B, C, D) y no reveles la respuesta correcta hasta que el alumno responda (o colócala oculta al final)."""
        try:
            return self.router.ask(prompt=prompt, system_prompt=SOCRATIC_PROMPT)
        except Exception:
            # Fallback transparente ante cuota agotada (429) o error de conexión
            return self.get_offline_quiz_question(topic)

    def evaluate_answer(self, question: str, user_answer: str) -> str:
        """Evalúa la respuesta del estudiante explicando aciertos o áreas de mejora."""
        prompt = f"""Pregunta formulada:
{question}

Respuesta del estudiante:
{user_answer}

Evalúa si la respuesta es correcta, explica detalladamente el por qué y añade un consejo de refuerzo."""
        return self.router.ask(prompt=prompt, system_prompt=SOCRATIC_PROMPT)
