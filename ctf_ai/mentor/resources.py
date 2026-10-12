"""
Catálogo de Recursos de Aprendizaje Verificados para Cybersecurity Study Mentor
Registra plataformas legítimas, URLs reales, modalidades de acceso estrictamente clasificadas
(gratuito permanente vs prueba vs certificado de pago) y habilidades asociadas.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Optional


class AccessType(str, Enum):
    PERMANENTLY_FREE = "100% Gratuito Permanente"
    FREE_TIER_LIMITED = "Capa Gratuita con Módulos Libres"
    FREE_CONTENT_PAID_CERT = "Contenido Gratuito / Certificado de Pago"
    FREE_TRIAL = "Prueba Gratuita Temporal"
    PAID = "De Pago"
    PENDING_VERIFICATION = "Pendiente de Verificación"


class LearningResource:
    """Representa un curso, laboratorio o plataforma educativa verificado."""

    def __init__(
        self,
        name: str,
        provider: str,
        url: str,
        access_type: AccessType,
        language: str = "Inglés / Español",
        level: str = "Principiante",
        skills: Optional[List[str]] = None,
        estimated_hours: int = 10,
        prerequisites: str = "Ninguno",
        verified_date: str = "2026-04",
    ):
        self.name = name
        self.provider = provider
        self.url = url
        self.access_type = access_type
        self.language = language
        self.level = level
        self.skills = skills or []
        self.estimated_hours = estimated_hours
        self.prerequisites = prerequisites
        self.verified_date = verified_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "url": self.url,
            "access_type": self.access_type.value,
            "language": self.language,
            "level": self.level,
            "skills": self.skills,
            "estimated_hours": self.estimated_hours,
            "prerequisites": self.prerequisites,
            "verified_date": self.verified_date,
        }


# Catálogo curado de plataformas 100% legítimas y comprobadas
VERIFIED_RESOURCES: List[LearningResource] = [
    LearningResource(
        name="PortSwigger Web Security Academy",
        provider="PortSwigger",
        url="https://portswigger.net/web-security",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés",
        level="Principiante a Avanzado",
        skills=["SQL Injection", "XSS", "CSRF", "SSRF", "Autenticación Web", "Burp Suite"],
        estimated_hours=60,
        prerequisites="Conceptos básicos de HTTP y navegadores",
    ),
    LearningResource(
        name="Cisco Skills for All: Introduction to Cybersecurity",
        provider="Cisco Networking Academy",
        url="https://skillsforall.com/course/introduction-to-cybersecurity",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Español / Inglés",
        level="Principiante",
        skills=["Fundamentos de Ciberseguridad", "Amenazas comunes", "Privacidad", "Defensa"],
        estimated_hours=15,
        prerequisites="Ninguno",
    ),
    LearningResource(
        name="Cisco Skills for All: Networking Basics",
        provider="Cisco Networking Academy",
        url="https://skillsforall.com/course/networking-basics",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Español / Inglés",
        level="Principiante",
        skills=["TCP/IP", "Direccionamiento IPv4/IPv6", "Subredes", "Routers y Switches"],
        estimated_hours=25,
        prerequisites="Ninguno",
    ),
    LearningResource(
        name="OverTheWire: Bandit Wargame",
        provider="OverTheWire",
        url="https://overthewire.org/wargames/bandit/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés",
        level="Principiante",
        skills=["Terminal Linux", "Comandos Bash", "Permisos", "SSH", "Redirecciones"],
        estimated_hours=15,
        prerequisites="Terminal básica",
    ),
    LearningResource(
        name="TryHackMe: Pre-Security & Free Practice Rooms",
        provider="TryHackMe",
        url="https://tryhackme.com/",
        access_type=AccessType.FREE_TIER_LIMITED,
        language="Inglés",
        level="Principiante",
        skills=["Linux Fundamentals", "Windows Basics", "Networking", "Web Basics"],
        estimated_hours=30,
        prerequisites="Ninguno",
    ),
    LearningResource(
        name="Hack The Box Academy: Tier 0 Modules",
        provider="Hack The Box",
        url="https://academy.hackthebox.com/",
        access_type=AccessType.FREE_TIER_LIMITED,
        language="Inglés",
        level="Principiante a Intermedio",
        skills=["Linux Fundamentals", "Setting Up Your Workspace", "Web Requests"],
        estimated_hours=20,
        prerequisites="Bases de computación",
    ),
    LearningResource(
        name="Linux Journey",
        provider="Linux Journey Community",
        url="https://linuxjourney.com/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Español / Inglés",
        level="Principiante",
        skills=["Administración Linux", "Línea de comandos", "Procesos", "Sistemas de Archivos"],
        estimated_hours=15,
        prerequisites="Ninguno",
    ),
    LearningResource(
        name="Microsoft Learn: SC-900 Security Fundamentals",
        provider="Microsoft",
        url="https://learn.microsoft.com/certifications/exams/sc-900/",
        access_type=AccessType.FREE_CONTENT_PAID_CERT,
        language="Español / Inglés",
        level="Principiante",
        skills=["Identidad y Acceso", "Seguridad Cloud", "Cumplimiento", "Conceptos Zero Trust"],
        estimated_hours=20,
        prerequisites="Bases generales de informática",
    ),
    LearningResource(
        name="OWASP Juice Shop & Top 10 Guides",
        provider="OWASP Foundation",
        url="https://owasp.org/www-project-juice-shop/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés / Español",
        level="Intermedio",
        skills=["OWASP Top 10", "Vulnerabilidades Web prácticas", "Explotación ética"],
        estimated_hours=25,
        prerequisites="Bases de desarrollo web",
    ),
    LearningResource(
        name="OpenSecurityTraining2: Introductory Intel x86",
        provider="OpenSecurityTraining2",
        url="https://ost2.fyi/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés",
        level="Intermedio",
        skills=["Arquitectura x86", "Ensamblador", "Registros", "Pila (Stack)", "Reversing"],
        estimated_hours=30,
        prerequisites="Conceptos de programación en C",
    ),
    LearningResource(
        name="Discudemy: Cupones 100% Descuento Udemy",
        provider="Discudemy",
        url="https://www.discudemy.com/language/spanish",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Español / Inglés",
        level="Todos los niveles",
        skills=["Cupones Udemy", "Cursos Gratis", "Hacking Ético", "Redes", "Ciberseguridad", "Udemy"],
        estimated_hours=5,
        prerequisites="Cuenta gratuita en Udemy",
    ),
    LearningResource(
        name="Real.Discount: Buscador de Cupones Gratis Udemy",
        provider="Real.Discount",
        url="https://www.real.discount/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés / Español",
        level="Todos los niveles",
        skills=["Cupones Udemy 100% OFF", "Seguridad Informática", "Certificaciones", "Udemy"],
        estimated_hours=5,
        prerequisites="Cuenta gratuita en Udemy",
    ),
    LearningResource(
        name="Tutorialbar: Ofertas y Cupones Gratuitos de Tecnología",
        provider="Tutorialbar",
        url="https://www.tutorialbar.com/all-courses/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés",
        level="Todos los niveles",
        skills=["Cupones Udemy", "Hacking Ético", "Python", "Cloud Security", "Udemy"],
        estimated_hours=5,
        prerequisites="Cuenta gratuita en Udemy",
    ),
    LearningResource(
        name="FreeCodeCamp: Information Security & Python Certification",
        provider="freeCodeCamp",
        url="https://www.freecodecamp.org/learn/information-security/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Español / Inglés",
        level="Principiante a Intermedio",
        skills=["Seguridad de la Información", "Python", "TCP/IP", "Penetration Testing", "Certificado Gratuito"],
        estimated_hours=300,
        prerequisites="Bases de programación",
    ),
    LearningResource(
        name="LetsDefend: Blue Team Training & Simulador de SOC L1",
        provider="LetsDefend",
        url="https://letsdefend.io/",
        access_type=AccessType.FREE_TIER_LIMITED,
        language="Inglés",
        level="Principiante a Intermedio",
        skills=["SOC", "Blue Team", "Triaje de Alertas", "Análisis de Malware", "EDR", "SIEM", "Incident Response"],
        estimated_hours=40,
        prerequisites="Conceptos básicos de redes y sistemas",
    ),
    LearningResource(
        name="Security Blue Team: Introduction to Cyber Defense",
        provider="Security Blue Team (SBT)",
        url="https://securityblue.team/courses/introduction-to-cyber-defense/",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés",
        level="Principiante",
        skills=["Blue Team", "SOC", "Defensa de Redes", "Threat Intelligence", "Gestión de Incidentes"],
        estimated_hours=15,
        prerequisites="Ninguno",
    ),
    LearningResource(
        name="CyberDefenders: Blue Team CTF & Digital Forensics",
        provider="CyberDefenders",
        url="https://cyberdefenders.org/",
        access_type=AccessType.FREE_TIER_LIMITED,
        language="Inglés",
        level="Principiante a Avanzado",
        skills=["SOC", "DFIR", "Análisis Forense", "Wireshark", "Splunk", "Detección de Amenazas"],
        estimated_hours=50,
        prerequisites="Conocimientos de análisis de tráfico",
    ),
    LearningResource(
        name="Splunk Free Training: Fundamentos de SIEM y Análisis de Datos",
        provider="Splunk",
        url="https://www.splunk.com/en_us/training/free-courses/overview.html",
        access_type=AccessType.PERMANENTLY_FREE,
        language="Inglés / Español",
        level="Principiante",
        skills=["SIEM", "Splunk", "Análisis de Logs", "SOC", "Monitoreo de Seguridad"],
        estimated_hours=20,
        prerequisites="Ninguno",
    ),
]


class ResourceCatalog:
    """Gestor del catálogo de recursos para el Study Mentor."""

    def __init__(self):
        self.resources: List[LearningResource] = list(VERIFIED_RESOURCES)

    def search_by_skill(self, skill: str) -> List[LearningResource]:
        s_lower = skill.lower()
        return [r for r in self.resources if any(s_lower in sk.lower() for sk in r.skills)]

    def filter_by_level(self, level: str) -> List[LearningResource]:
        l_lower = level.lower()
        return [r for r in self.resources if l_lower in r.level.lower()]

    def filter_permanently_free(self) -> List[LearningResource]:
        return [r for r in self.resources if r.access_type == AccessType.PERMANENTLY_FREE]

    def search_courses(self, query: str) -> List[LearningResource]:
        """Busca cursos y recursos relevantes para cualquier consulta en lenguaje natural."""
        q = query.lower().strip()
        if not q:
            return self.resources

        matched = []
        is_beginner_intent = any(term in q for term in ["empezar", "inicio", "principiante", "cero", "basico", "básico", "primeros pasos"])

        stop_words = {"los", "las", "para", "por", "que", "con", "una", "uno", "del", "busca", "buscar", "quiero", "dame", "cursos", "curso", "como"}
        words = [w for w in re.findall(r"\w+", q) if len(w) > 2 and w not in stop_words]

        for r in self.resources:
            score = 0
            # Coincidencia directa completa en nombre o proveedor
            if q in r.name.lower() or q in r.provider.lower():
                score += 8

            # Coincidencias de palabras clave individuales (ej: soc, siem, web, reversing)
            for w in words:
                if w in r.name.lower() or w in r.provider.lower():
                    score += 5
                if any(w == skill.lower() or w in skill.lower() for skill in r.skills):
                    score += 4

            # Coincidencia exacta de habilidades
            if any(skill.lower() in q or q in skill.lower() for skill in r.skills):
                score += 3

            # Intención de principiante si coincide con recursos introductorios
            if is_beginner_intent and "principiante" in r.level.lower():
                score += 1

            if score > 0:
                matched.append((score, r))

        if matched:
            matched.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in matched]

        return []

    def get_all(self) -> List[LearningResource]:
        return self.resources
