"""
Asesor y Consultor Educativo Inteligente para Cybersecurity Study Mentor
Permite conversar de forma dinámica con la IA sobre metas formativas, plataformas de cupones
100% gratuitos de Udemy, rutas de aprendizaje, cursos abiertos y certificaciones.
"""

from typing import Any, Dict, List, Optional
from ctf_ai.ai_providers import AIRouter
from ctf_ai.mentor.interview import StudentProfile


MENTOR_ADVISOR_SYSTEM_PROMPT = """Eres el Mentor Senior de Formación en Ciberseguridad de CTF-AI Solver Pro.
Tu misión es guiar de forma cercana, realista, estructurada y técnica a personas que quieren formarse en ciberseguridad, hacking ético, pentesting, análisis forense, seguridad web, reversing o administración de sistemas seguros.

PRINCIPIOS CLAVE:
1. Responde siempre en español, con un tono motivador, profesional y estructurado en Markdown legible.
2. Si el usuario pregunta por UDEMY, CUPONES 100% GRATIS O DESCUENTOS:
   - Explica las plataformas y agregadores legítimos que publican cupones de 100% de descuento diariamente:
     • **Discudemy** (https://www.discudemy.com/ o https://www.discudemy.com/language/spanish): Agregador destacado con filtros en español e inglés.
     • **Real.Discount** (https://www.real.discount/): Buscador global de cupones 100% OFF con filtros por categoría ("Cybersecurity", "IT & Software").
     • **Tutorialbar** (https://www.tutorialbar.com/all-courses/): Portal de cupones verificados con sección específica de tecnología y ciberseguridad.
     • **Coursevania** (https://coursevania.com/): Cupones 100% gratuitos actualizados por fecha.
   - Explica la técnica de búsqueda directa gratuita en Udemy:
     • Enlace directo a cursos de precio $0: https://www.udemy.com/courses/search/?q=ciberseguridad&price=price-free
     • Indicar que al buscar cualquier tecnología, en el filtro lateral izquierdo seleccionen "Precio -> Gratis".
   - Explica las reglas de los cupones de Udemy: Los cupones 100% OFF tienen un cupo limitado (hasta 1.000 inscripciones según la política de Udemy) o 3-5 días de vigencia. Por tanto, deben reclamarse rápido. Una vez inscritos, quedan guardados en la biblioteca para siempre sin coste ni tarjeta.
   - Recomienda temáticas e instructores de referencia según el área que le interese.
3. Si el usuario pregunta por otras áreas o plataformas gratuitas:
   - Menciona opciones de auditoría gratuita ("Audit Mode" en Coursera y edX, permitiendo ver todos los vídeos y lecturas sin pagar certificado).
   - Recomienda laboratorios prácticos y wargames (TryHackMe salas libres, PortSwigger Web Security Academy, OverTheWire Bandit, PicoCTF).
   - Recomienda canales de YouTube con cursos completos (S4vitar, El Pingüino de Mario, NetworkChuck, John Hammond, David Bombal, The Cyber Mentor).
4. Adapta las recomendaciones al perfil del estudiante si está disponible (nivel, horas semanales, objetivo profesional).
5. NUNCA respondas con una tabla genérica repetitiva; personaliza la respuesta exactamente a lo que el estudiante acaba de pedir.
"""


OFFLINE_COUPON_GUIDE = """### 🎓 Guía Especializada: Cursos de Udemy y Cupones 100% Gratuitos

Para conseguir cursos de ciberseguridad y hacking ético en Udemy **completamente gratis y de forma 100% legal**, tienes dos métodos directos:

---

#### 1. Plataformas y Agregadores de Cupones 100% OFF (Actualizados a diario)
Los propios instructores de Udemy crean promociones con cupones al 100% para conseguir estudiantes y reseñas. Estas webs recopilan esos cupones directos:

1. **Discudemy** 🔗 [discudemy.com/language/spanish](https://www.discudemy.com/language/spanish)
   - Es el portal más utilizado para cupones en habla hispana e internacional.
   - Cuenta con categorías directas para *Security*, *Networking* y *Operating Systems*.
2. **Real.Discount** 🔗 [real.discount](https://www.real.discount/)
   - Potente buscador con filtros por categoría ("IT & Software / Security") y valoración.
   - Te lleva directamente al enlace de Udemy con el cupón aplicado (`?couponCode=...`).
3. **Tutorialbar** 🔗 [tutorialbar.com/all-courses](https://www.tutorialbar.com/all-courses/)
   - Publica diariamente decenas de cupones 100% gratis con sección dedicada a hacking ético y redes.
4. **Coursevania** 🔗 [coursevania.com](https://coursevania.com/)
   - Agregador de cupones verificados organizados por fecha y categoría técnica.

> [!TIP]
> **Consejo Clave sobre Cupones de Udemy:** La política de Udemy limita los cupones gratuitos a **1.000 inscripciones** o 3-5 días. Cuando veas un curso que te interese, pulsa **"Inscribirse ahora"** de inmediato para que quede vinculado a tu biblioteca para siempre. **No requiere introducir tarjeta bancaria** si el total marca $0.00.

---

#### 2. Cursos 100% Gratuitos Permanentes dentro de Udemy
Udemy dispone de cientos de cursos nativos gratuitos sin necesidad de cupones:
- **Búsqueda filtrada directa:** [Cursos gratuitos de Ciberseguridad en Udemy](https://www.udemy.com/courses/search/?q=ciberseguridad&price=price-free)
- **Cómo aplicarlo:** Escribe cualquier tecnología (ej: *Python*, *Linux*, *Nmap*, *Wireshark*) en la barra de búsqueda de Udemy, ve al menú lateral izquierdo y marca la casilla **Precio ➔ Gratis**.

---

#### 3. Alternativas Gratuitas de Máxima Calidad
Si buscas complementar o mientras encuentras cupones activos:
- **PortSwigger Web Security Academy:** [portswigger.net/web-security](https://portswigger.net/web-security) (Laboratorios 100% gratuitos de seguridad web).
- **OverTheWire Bandit:** [overthewire.org](https://overthewire.org/) (Aprende Linux y terminal desde cero jugando).
- **TryHackMe:** [tryhackme.com](https://tryhackme.com/) (Módulos gratuitos en el path Pre-Security).
- **Canales de YouTube recomendados:** *S4vitar* (Hacking ético y resolución de máquinas), *El Pingüino de Mario* (Linux y redes), *NetworkChuck* (Fundamentos prácticos).
"""


class MentorAdvisor:
    """Consultor pedagógico conversacional de ciberseguridad."""

    def __init__(self, ai_router: AIRouter):
        self.router = ai_router

    def consult(
        self,
        query: str,
        student_profile: Optional[StudentProfile] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Consulta al mentor de IA teniendo en cuenta el historial y el perfil del alumno.
        Si la API de IA no está disponible o sufre agotamiento de cuota, recurre al asesor offline.
        """
        profile_ctx = ""
        if student_profile:
            profile_ctx = (
                f"\nDATOS DEL ESTUDIANTE:\n"
                f"- Rol Objetivo: {student_profile.target_role}\n"
                f"- Nivel Actual: {student_profile.level}\n"
                f"- Disponibilidad: {student_profile.weekly_hours} horas semanales\n"
                f"- Preferencia de Coste: {student_profile.budget_mode}\n"
            )

        conversation_history_text = ""
        if history:
            conversation_history_text = "\nHISTORIAL PREVIO DE LA CONVERSACIÓN:\n"
            for turn in history[-4:]:  # Últimos 4 turnos
                role = "Estudiante" if turn.get("role") == "user" else "Mentor"
                conversation_history_text += f"{role}: {turn.get('content', '')}\n"

        prompt = f"""{profile_ctx}{conversation_history_text}
CONSULTA ACTUAL DEL ESTUDIANTE:
{query}

Por favor, asesora al estudiante respondiendo directamente a su consulta actual con información detallada, plataformas legítimas, pasos accionables y enlaces recomendados."""

        try:
            response = self.router.ask(
                prompt=prompt,
                system_prompt=MENTOR_ADVISOR_SYSTEM_PROMPT,
            )
            # Guardar en historial si fue exitoso
            if history is not None:
                history.append({"role": "user", "content": query})
                history.append({"role": "assistant", "content": response})
            return response
        except Exception:
            # Fallback resiliente offline
            offline_resp = self.get_offline_advice(query, student_profile)
            if history is not None:
                history.append({"role": "user", "content": query})
                history.append({"role": "assistant", "content": offline_resp})
            return offline_resp

    def get_offline_advice(self, query: str, student_profile: Optional[StudentProfile] = None) -> str:
        """Genera recomendaciones estructuradas offline cuando la API externa no está accesible."""
        q_lower = query.lower()

        # Detección de interés en cupones o Udemy
        if any(term in q_lower for term in ["udemy", "cupon", "cupón", "cupones", "descuento", "gratis", "free"]):
            return OFFLINE_COUPON_GUIDE

        # Detección de interés en seguridad web
        if any(term in q_lower for term in ["web", "owasp", "sql", "xss", "burp"]):
            return (
                "### 🌐 Guía de Formación en Seguridad Web (Modo Local)\n\n"
                "Para especializarte en seguridad y auditoría de aplicaciones web sin coste:\n\n"
                "1. **PortSwigger Web Security Academy:** [portswigger.net/web-security](https://portswigger.net/web-security)\n"
                "   - Es el estándar de oro de la industria, 100% gratuito y con laboratorios reales en la nube de Burp Suite.\n"
                "2. **OWASP Juice Shop:** [owasp.org/www-project-juice-shop](https://owasp.org/www-project-juice-shop/)\n"
                "   - Aplicación vulnerable deliberada para practicar las 10 vulnerabilidades críticas de OWASP.\n"
                "3. **Práctica en CTFs:** Retos de la categoría Web en [PicoCTF](https://play.picoctf.org/) y [Root-Me](https://www.root-me.org/)."
            )

        # Detección de interés en reversing / bajo nivel
        if any(term in q_lower for term in ["revers", "ensamblador", "asm", "x86", "binari", "malware", "pwn"]):
            return (
                "### 🧩 Guía de Ingeniería Inversa y Reversing (Modo Local)\n\n"
                "Para iniciarte en reversing y análisis de binarios:\n\n"
                "1. **OpenSecurityTraining2 (OST2):** [ost2.fyi](https://ost2.fyi/)\n"
                "   - Cursos de clase mundial de x86/x64 Architecture y Reversing completamente gratuitos.\n"
                "2. **Ghidra Software Reverse Engineering:** [ghidra-sre.org](https://ghidra-sre.org/)\n"
                "   - Suite gratuita y de código abierto de la NSA para desensamblado y descompilación.\n"
                "3. **Crackmes.one:** [crackmes.one](https://crackmes.one/)\n"
                "   - Retos binarios creados por la comunidad ordenados por nivel de dificultad."
            )

        # Detección de interés en SOC / Blue Team / Defensor
        if any(term in q_lower for term in ["soc", "blue team", "siem", "analista", "defens", "deteccion", "detección", "incident"]):
            return (
                "### 🛡️ Guía para Iniciarse como Analista SOC / Blue Team (Modo Local)\n\n"
                "El rol de **Analista SOC (Security Operations Center)** es puramente **defensivo**: su misión es monitorizar eventos, detectar anomalías, clasificar alertas y responder a incidentes en tiempo real.\n\n"
                "#### 1. Plataformas y Laboratorios Defensivos 100% Gratuitos:\n"
                "1. **LetsDefend:** [https://letsdefend.io/](https://letsdefend.io/)\n"
                "   - Simulador interactivo que replica una consola real de SOC: alertas de phishing, malware en endpoints (EDR) y análisis de logs.\n"
                "2. **Security Blue Team (SBT):** [https://securityblue.team/courses/introduction-to-cyber-defense/](https://securityblue.team/courses/introduction-to-cyber-defense/)\n"
                "   - Curso introductorio gratuito oficial a la ciberdefensa y operaciones de seguridad.\n"
                "3. **CyberDefenders:** [https://cyberdefenders.org/](https://cyberdefenders.org/)\n"
                "   - Retos prácticos tipo Blue Team CTF con análisis de capturas de red (PCAP) y memoria RAM.\n"
                "4. **Splunk Free Training:** [https://www.splunk.com/en_us/training/free-courses/overview.html](https://www.splunk.com/en_us/training/free-courses/overview.html)\n"
                "   - Formación gratuita en el SIEM estándar de la industria para búsqueda e indexación de eventos.\n\n"
                "#### 2. Tecnologías y Habilidades Imprescindibles para SOC:\n"
                "• **SIEM:** Splunk, Wazuh, Elastic Security.\n"
                "• **Análisis de Red:** Wireshark, inspección de cabeceras TCP/IP, DNS y HTTP.\n"
                "• **Logs del Sistema:** Windows Event Logs (Sysmon), logs de autenticación en Linux (`/var/log/auth.log`).\n"
                "• **Marco Táctico:** MITRE ATT&CK Framework.\n\n"
                "> [!TIP]\n"
                "> Escribe `open 1` para abrir la primera plataforma (LetsDefend) en tu navegador."
            )

        # Detección de inicio general en ciberseguridad
        if any(term in q_lower for term in ["ciberseguridad", "empezar", "inicio", "principiante", "aprender"]):
            return (
                "### 🌐 Guía de Inicio en Ciberseguridad: Fundamentos y Rutas\n\n"
                "Para ingresar en el mundo de la ciberseguridad sin perderte, el primer paso es construir una base sólida antes de elegir tu especialización:\n\n"
                "#### 1. Los Tres Pilares Fundamentales (100% Gratuitos):\n"
                "1. **Sistemas Operativos (Linux):**\n"
                "   • **Linux Journey:** [https://linuxjourney.com/](https://linuxjourney.com/) (Comandos bash, procesos y permisos).\n"
                "   • **OverTheWire Bandit:** [https://overthewire.org/](https://overthewire.org/) (Aprende la terminal jugando niveles progresivos).\n"
                "2. **Redes y Comunicaciones:**\n"
                "   • **Cisco Skills for All - Networking Basics:** [https://skillsforall.com/](https://skillsforall.com/) (Modelo OSI, TCP/IP, direccionamiento).\n"
                "3. **Conceptos de Seguridad:**\n"
                "   • **Cisco Skills for All - Introduction to Cybersecurity:** [https://skillsforall.com/](https://skillsforall.com/).\n\n"
                "#### 2. Principales Ramas para Especializarte:\n"
                "• **Defensiva (Blue Team / SOC):** Si te gusta monitorizar, analizar tráfico, cazar amenazas y responder a incidentes.\n"
                "• **Ofensiva (Pentesting / Red Team):** Si te gusta encontrar vulnerabilidades y realizar auditorías de intrusión autorizadas.\n"
                "• **Seguridad Web:** Auditoría de APIs, OWASP Top 10 y aplicaciones web en PortSwigger Academy.\n\n"
                "*(Dime qué rama te llama más la atención y te guiaré con recursos específicos y cupones de Udemy)*"
            )

        # Guía de rol guardado
        role = student_profile.target_role if student_profile else "Ciberseguridad General"
        return (
            f"### 🛡️ Recomendación de Mentoría: {role}\n\n"
            "Para avanzar sólidamente en tu formación técnica sin inversión inicial:\n\n"
            "1. **Bases de Sistemas y Redes:**\n"
            "   - **Linux Journey:** [https://linuxjourney.com/](https://linuxjourney.com/)\n"
            "   - **Cisco Skills for All:** [https://skillsforall.com/](https://skillsforall.com/)\n"
            "2. **Laboratorios Prácticos Diarios:**\n"
            "   - **OverTheWire (Bandit):** [https://overthewire.org/](https://overthewire.org/)\n"
            "   - **TryHackMe:** [https://tryhackme.com/](https://tryhackme.com/)\n"
            "3. **Cupones de Cursos:** Usa webs como [https://www.discudemy.com/](https://www.discudemy.com/) o [https://www.real.discount/](https://www.real.discount/) para obtener cursos de Udemy 100% gratuitos cuando se publiquen."
        )
