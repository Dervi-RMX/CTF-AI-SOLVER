"""
Generador de Rutas de Estudio (Roadmaps) para Cybersecurity Study Mentor
Construye itinerarios formativos progresivos por semanas y módulos adaptados a las horas y presupuesto del usuario.
"""

from typing import Any, Dict, List, Optional
import json
from pathlib import Path

from ctf_ai.mentor.interview import StudentProfile
from ctf_ai.mentor.resources import ResourceCatalog, LearningResource, VERIFIED_RESOURCES


class StudyModule:
    """Representa una semana o etapa de aprendizaje dentro de la ruta."""

    def __init__(
        self,
        stage_number: int,
        title: str,
        estimated_hours: int,
        concepts: List[str],
        labs: List[str],
        resources: Optional[List[Dict[str, str]]] = None,
        evaluation: str = "Prueba práctica y resumen de conceptos",
        completed: bool = False,
    ):
        self.stage_number = stage_number
        self.title = title
        self.estimated_hours = estimated_hours
        self.concepts = concepts
        self.labs = labs
        self.resources = resources or []
        self.evaluation = evaluation
        self.completed = completed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage_number,
            "title": self.title,
            "estimated_hours": self.estimated_hours,
            "concepts": self.concepts,
            "labs": self.labs,
            "resources": self.resources,
            "evaluation": self.evaluation,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudyModule":
        return cls(
            stage_number=data.get("stage", 1),
            title=data.get("title", ""),
            estimated_hours=data.get("estimated_hours", 5),
            concepts=data.get("concepts", []),
            labs=data.get("labs", []),
            resources=data.get("resources", []),
            evaluation=data.get("evaluation", ""),
            completed=data.get("completed", False),
        )


class LearningPath:
    """Ruta formativa completa con módulos secuenciales y proyecto final."""

    def __init__(
        self,
        role: str,
        level: str,
        weekly_hours: int,
        modules: List[StudyModule],
        capstone_project: str,
    ):
        self.role = role
        self.level = level
        self.weekly_hours = weekly_hours
        self.modules = modules
        self.capstone_project = capstone_project

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "level": self.level,
            "weekly_hours": self.weekly_hours,
            "modules": [m.to_dict() for m in self.modules],
            "capstone_project": self.capstone_project,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LearningPath":
        return cls(
            role=data.get("role", "General"),
            level=data.get("level", "Principiante"),
            weekly_hours=data.get("weekly_hours", 5),
            modules=[StudyModule.from_dict(m) for m in data.get("modules", [])],
            capstone_project=data.get("capstone_project", "Proyecto práctico final"),
        )

    def to_markdown(self) -> str:
        lines = [
            f"# 🎯 Ruta de Estudio Personalizada: {self.role}",
            f"**Nivel de inicio:** {self.level} | **Dedicación semanal:** {self.weekly_hours} horas",
            f"**Duración total estimada:** {len(self.modules)} semanas",
            "",
            "---",
            "",
        ]

        for m in self.modules:
            status_mark = "✔ [COMPLETADO]" if m.completed else "⏳ [PENDIENTE]"
            lines.append(f"## Semana {m.stage_number}: {m.title} ({status_mark})")
            lines.append(f"**Dedicación:** ~{m.estimated_hours} horas")
            lines.append("\n**Conceptos a dominar:**")
            for c in m.concepts:
                lines.append(f"- {c}")

            lines.append("\n**Laboratorios y Práctica:**")
            for lab in m.labs:
                lines.append(f"- 🧪 {lab}")

            if m.resources:
                lines.append("\n**Recursos recomendados (100% legítimos):**")
                for r in m.resources:
                    lines.append(f"- 🔗 [{r.get('name')}]({r.get('url')}) - *{r.get('access')}*")

            lines.append(f"\n**Criterio de Evaluación:** {m.evaluation}\n")
            lines.append("---\n")

        lines.append("## 🏆 Proyecto Final (Capstone)")
        lines.append(self.capstone_project)
        return "\n".join(lines)


class RoadmapGenerator:
    """Generador especializado de rutas de aprendizaje estructuradas."""

    @classmethod
    def generate_for_profile(cls, profile: StudentProfile) -> LearningPath:
        role_lower = profile.target_role.lower()

        if "pentest" in role_lower or "ofensiva" in role_lower:
            return cls._generate_pentest_path(profile)
        elif "blue" in role_lower or "soc" in role_lower:
            return cls._generate_blue_team_path(profile)
        elif "forense" in role_lower or "dfir" in role_lower:
            return cls._generate_forensics_path(profile)
        elif "reversing" in role_lower or "malware" in role_lower:
            return cls._generate_reversing_path(profile)
        else:
            return cls._generate_fundamentals_path(profile)

    @classmethod
    def _generate_pentest_path(cls, p: StudentProfile) -> LearningPath:
        m1 = StudyModule(
            stage_number=1,
            title="Fundamentos de Redes, TCP/IP y Terminal Linux",
            estimated_hours=p.weekly_hours,
            concepts=["Modelo TCP/IP y OSI", "Puertos, protocolos (HTTP, SSH, DNS)", "Comandos esenciales de Bash"],
            labs=["Completar OverTheWire Bandit niveles 1 al 10", "Capturar y filtrar paquetes con Wireshark"],
            resources=[
                {"name": "OverTheWire: Bandit", "url": "https://overthewire.org/wargames/bandit/", "access": "100% Gratuito"},
                {"name": "Linux Journey", "url": "https://linuxjourney.com/", "access": "100% Gratuito"},
            ],
            evaluation="Ser capaz de navegar por el sistema de archivos de Linux y resolver Bandit nivel 10.",
        )
        m2 = StudyModule(
            stage_number=2,
            title="Reconocimiento, Escaneo y Enumeración de Servicios",
            estimated_hours=p.weekly_hours,
            concepts=["Escaneo de puertos con Nmap", "Banners y versiones", "Enumeración de directorios web (Gobuster/ffuf)"],
            labs=["Escanear máquina de laboratorio local con Nmap", "Enumerar subdominios y rutas en entorno de prueba"],
            resources=[
                {"name": "TryHackMe: Nmap Room (Free)", "url": "https://tryhackme.com/", "access": "Capa Gratuita"},
            ],
            evaluation="Redactar un informe de reconocimiento con servicios, versiones y posibles vectores.",
        )
        m3 = StudyModule(
            stage_number=3,
            title="Vulnerabilidades Web Fundamentales (OWASP Top 10)",
            estimated_hours=p.weekly_hours,
            concepts=["Inyección SQL (SQLi)", "Cross-Site Scripting (XSS)", "Fallo de control de acceso"],
            labs=["PortSwigger Web Academy: Laboratorios Apprentice de SQLi y XSS"],
            resources=[
                {"name": "PortSwigger Web Security Academy", "url": "https://portswigger.net/web-security", "access": "100% Gratuito Permanente"},
            ],
            evaluation="Explotar y mitigar vulnerabilidad SQLi en laboratorio sin herramientas automatizadas.",
        )
        m4 = StudyModule(
            stage_number=4,
            title="Explotación Básica y Escalada de Privilegios",
            estimated_hours=p.weekly_hours,
            concepts=["Permisos SUID/SGID en Linux", "Tareas Cron mal configuradas", "Reverse shells seguras"],
            labs=["Resolver 1 máquina vulnerable de nivel 'Easy' en TryHackMe o VulnHub"],
            resources=[
                {"name": "Hack The Box Academy: Linux Fundamentals", "url": "https://academy.hackthebox.com/", "access": "Módulo Gratuito Tier 0"},
            ],
            evaluation="Obtener acceso inicial y elevar privilegios a root en entorno de prueba.",
        )

        capstone = "Resolver de forma autónoma una máquina 'Easy' de TryHackMe o HTB y redactar un informe profesional de pentesting con hallazgos, pruebas de concepto y remediaciones."
        return LearningPath(role=p.target_role, level=p.level, weekly_hours=p.weekly_hours, modules=[m1, m2, m3, m4], capstone_project=capstone)

    @classmethod
    def _generate_blue_team_path(cls, p: StudentProfile) -> LearningPath:
        m1 = StudyModule(
            stage_number=1,
            title="Arquitectura de Red y Análisis de Tráfico con Wireshark",
            estimated_hours=p.weekly_hours,
            concepts=["Handshake TCP de 3 vías", "Análisis de consultas DNS anómalas", "Tráfico HTTP no cifrado"],
            labs=["Inspeccionar archivos PCAP con capturas de ataques reales", "Identificar IPs atacantes y user-agents"],
            resources=[
                {"name": "Cisco Skills for All: Networking Basics", "url": "https://skillsforall.com/course/networking-basics", "access": "100% Gratuito"},
            ],
            evaluation="Reconstruir una sesión HTTP y extraer el archivo descargado a partir de un PCAP.",
        )
        m2 = StudyModule(
            stage_number=2,
            title="Análisis de Logs de Windows (Event Viewer & Sysmon)",
            estimated_hours=p.weekly_hours,
            concepts=["Event IDs críticos (4624 login, 4625 fallo, 4688 creación de proceso)", "Sysmon Event ID 1 (ejecución de comandos)"],
            labs=["Analizar volcado de eventos de seguridad ante intento de fuerza bruta RDP"],
            resources=[
                {"name": "Microsoft Learn: Security Fundamentals", "url": "https://learn.microsoft.com/certifications/exams/sc-900/", "access": "Gratuito / Cert opcional"},
            ],
            evaluation="Identificar la IP de origen y usuario vulnerado a partir de un archivo .evtx.",
        )
        m3 = StudyModule(
            stage_number=3,
            title="Fundamentos de SIEM y Detección de Amenazas",
            estimated_hours=p.weekly_hours,
            concepts=["Arquitectura de SIEM (Splunk/Elastic)", "Creación de reglas de correlación", "Detección de malware básico"],
            labs=["Instalar Elastic Stack o Splunk Free localmente y cargar logs de prueba"],
            resources=[
                {"name": "TryHackMe: Blue Team Free Rooms", "url": "https://tryhackme.com/", "access": "Capa Gratuita"},
            ],
            evaluation="Crear una regla de alerta para detectar inyecciones de comandos en servidor web.",
        )

        capstone = "Análisis completo de un incidente de compromiso de red ficticio: identificar vector de entrada, persistencia, movimiento lateral e informe de contención."
        return LearningPath(role=p.target_role, level=p.level, weekly_hours=p.weekly_hours, modules=[m1, m2, m3], capstone_project=capstone)

    @classmethod
    def _generate_forensics_path(cls, p: StudentProfile) -> LearningPath:
        m1 = StudyModule(
            stage_number=1,
            title="Estructuras de Archivos, Metadatos y Magic Bytes",
            estimated_hours=p.weekly_hours,
            concepts=["Firmas binarias (Magic Bytes)", "Análisis hexadecimal", "Metadatos EXIF e integridad con hashes"],
            labs=["Reparar cabecera de archivo corrupto en editor hex", "Extraer artefactos con strings y binwalk"],
            resources=[
                {"name": "Linux Journey", "url": "https://linuxjourney.com/", "access": "100% Gratuito"},
            ],
            evaluation="Identificar el tipo real de 5 archivos con extensión falsa y recuperar una imagen alterada.",
        )
        m2 = StudyModule(
            stage_number=2,
            title="Forense de Memoria RAM (Volatility)",
            estimated_hours=p.weekly_hours,
            concepts=["Estructura de procesos en memoria", "Detección de DLLs inyectadas", "Extracción de contraseñas de memoria"],
            labs=["Analizar volcado de memoria (.raw/.vmem) con Volatility 3"],
            resources=[
                {"name": "TryHackMe: Memory Forensics (Free Tier)", "url": "https://tryhackme.com/", "access": "Capa Gratuita"},
            ],
            evaluation="Localizar el PID del proceso malicioso y la dirección IP con la que mantenía conexión activa.",
        )

        capstone = "Resolución de un caso forense completo de CTF (imagen de disco + volcado de RAM) con informe de cadena de custodia y evidencias comprobadas."
        return LearningPath(role=p.target_role, level=p.level, weekly_hours=p.weekly_hours, modules=[m1, m2], capstone_project=capstone)

    @classmethod
    def _generate_reversing_path(cls, p: StudentProfile) -> LearningPath:
        m1 = StudyModule(
            stage_number=1,
            title="Arquitectura de Computadores y Ensamblador x86/x64",
            estimated_hours=p.weekly_hours,
            concepts=["Registros (RAX, RBX, RSP, RBP, RIP)", "La Pila (Stack) y convención de llamadas", "Instrucciones MOV, PUSH, POP, JMP, CALL"],
            labs=["Desensamblar programas simples en C compilados con GCC/MSVC"],
            resources=[
                {"name": "OpenSecurityTraining2: Intro to x86", "url": "https://ost2.fyi/", "access": "100% Gratuito Permanente"},
            ],
            evaluation="Leer un fragmento de ensamblador y predecir el valor de retorno de una función.",
        )
        m2 = StudyModule(
            stage_number=2,
            title="Análisis Estático con Ghidra y Detección de Packers",
            estimated_hours=p.weekly_hours,
            concepts=["Uso de Ghidra para descompilación", "Estructura de cabeceras PE y ELF", "Entropía y desempaquetado de UPX"],
            labs=["Resolver un reto CrackMe básico de reversing en crackmes.one"],
            resources=[
                {"name": "OpenSecurityTraining2: Life of Binaries", "url": "https://ost2.fyi/", "access": "100% Gratuito"},
            ],
            evaluation="Revertir el algoritmo de validación de clave de un binario CrackMe nivel 1.",
        )

        capstone = "Análisis completo de un binario ofuscado con extracción de la contraseña oculta e informe técnico en pseudocódigo C."
        return LearningPath(role=p.target_role, level=p.level, weekly_hours=p.weekly_hours, modules=[m1, m2], capstone_project=capstone)

    @classmethod
    def _generate_fundamentals_path(cls, p: StudentProfile) -> LearningPath:
        m1 = StudyModule(
            stage_number=1,
            title="Bases de Computación, Terminal y Linux",
            estimated_hours=p.weekly_hours,
            concepts=["Sistemas operativos", "Línea de comandos Bash", "Permisos y ficheros"],
            labs=["Completar Bandit niveles 1 al 10 en OverTheWire"],
            resources=[
                {"name": "OverTheWire: Bandit", "url": "https://overthewire.org/wargames/bandit/", "access": "100% Gratuito"},
                {"name": "Linux Journey", "url": "https://linuxjourney.com/", "access": "100% Gratuito"},
            ],
            evaluation="Moverse por la terminal sin entorno gráfico.",
        )
        m2 = StudyModule(
            stage_number=2,
            title="Fundamentos de Redes e Internet",
            estimated_hours=p.weekly_hours,
            concepts=["Direcciones IP, DNS, DHCP", "Puertos y protocolos", "Seguridad básica en redes"],
            labs=["Curso interactivo de Cisco Skills for All"],
            resources=[
                {"name": "Cisco Skills for All: Networking Basics", "url": "https://skillsforall.com/course/networking-basics", "access": "100% Gratuito"},
            ],
            evaluation="Comprender qué ocurre exactamente al escribir una URL en el navegador.",
        )
        capstone = "Participar en un CTF introductorio tipo PicoCTF resolviendo retos iniciales de General Skills y Web."
        return LearningPath(role=p.target_role, level=p.level, weekly_hours=p.weekly_hours, modules=[m1, m2], capstone_project=capstone)
