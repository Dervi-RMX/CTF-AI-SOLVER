"""
Módulo de Autocompletado de Comandos (/ Slash Commands) para CTF-AI Solver Pro.
Proporciona sugerencias en tiempo real, metadatos descriptivos en español y sub-argumentos contextuales.
"""

from typing import Iterable, List, Tuple
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style


# Catálogo maestro de comandos: (nombre_sin_slash, alias_list, descripción_corta, categoría)
COMMANDS_REGISTRY: List[Tuple[str, List[str], str, str]] = [
    # Categoría 1: Retos y Motor Autónomo de Evidencias
    ("challenge", ["c"], "Define el enunciado del reto y formula la primera hipótesis", "Retos"),
    ("solve", ["s"], "Inicia el bucle de razonamiento autónomo basado en evidencias", "Retos"),
    ("step", ["st"], "Ejecuta un único paso táctico del plan", "Retos"),
    ("evidence", ["evd"], "Muestra el inventario de hipótesis, hechos y banderas", "Retos"),
    ("plan", ["pl"], "Muestra el árbol de tareas operacionales y presupuesto", "Retos"),
    ("report", ["rep"], "Exporta un informe técnico completo del reto a Markdown", "Retos"),
    ("file", ["f"], "Carga y analiza un archivo local del reto (strings, magic)", "Retos"),
    ("context", ["ctx"], "Muestra el historial y pistas acumuladas del reto actual", "Retos"),

    # Categoría 2: Asistencia de IA y Ejecución
    ("ask", ["a"], "Consulta libremente cualquier duda técnica a la IA", "IA & Terminal"),
    ("provider", ["p"], "Alterna el modelo de IA activo (gemini, openai, claude)", "IA & Terminal"),
    ("model", ["m"], "Lista o cambia el modelo de IA para el proveedor activo", "IA & Terminal"),
    ("tool", ["t"], "Ejecuta una herramienta integrada (base64, hex, rot13, etc.)", "IA & Terminal"),
    ("tools", [], "Lista todas las herramientas y utilidades CTF disponibles", "IA & Terminal"),
    ("exec", ["!"], "Ejecuta un comando en la consola del sistema con confirmación", "IA & Terminal"),
    ("mode", [], "Cambia el modo activo de trabajo (ctf, mentor, diag)", "IA & Terminal"),

    # Categoría 3: Certificaciones & Cybersecurity Study Mentor
    ("cert", ["certs", "certificacion"], "Preparación de certificaciones (ISC2, Sec+, eJPT, CJCA) con temas y quiz", "Certificaciones"),
    ("quiz", ["qz", "drill", "exam"], "Inicia un simulacro interactivo para la certificación elegida", "Certificaciones"),
    ("mentor", ["study"], "Conversa con el mentor IA: cursos, cupones gratis y asesoría", "Study Mentor"),
    ("roadmap", ["rm"], "Genera o visualiza tu ruta de aprendizaje personalizada", "Study Mentor"),
    ("plan-study", ["schedule"], "Recalibra el cronograma semanal ante cambios de tiempo", "Study Mentor"),

    # Categoría 4: Sesión y Sistema
    ("open", ["o", "browse"], "Abre un curso o enlace web en tu navegador predeterminado", "Navegación"),
    ("diag", ["diagnostics"], "Comprueba estado de conexión a APIs, Docker y PATH", "Sistema"),
    ("save", [], "Guarda la sesión actual del reto en formato JSON", "Sistema"),
    ("load", [], "Restaura una sesión guardada previamente", "Sistema"),
    ("clear", ["cls"], "Limpia la pantalla de la terminal", "Sistema"),
    ("help", ["h", "?"], "Muestra la guía completa de comandos interactivos", "Sistema"),
    ("exit", ["q", "quit"], "Cierra el asistente de forma segura", "Sistema"),

    # Categoría 5: Cisco Packet Tracer Automation
    ("pt", ["packet-tools", "packettools", "packet-tracer"], "Plataforma Web Packet Tools AI (ph0Void/packet-tools)", "Redes & IA"),
]


# Sub-argumentos sugeridos según el comando activo
SUB_ARGUMENTS = {
    "cert": [
        ("isc2", "ISC2 Certified in Cybersecurity (CC) - Principios, Redes, Operaciones"),
        ("sec+", "CompTIA Security+ (SY0-701) - Zero Trust, Amenazas, Arquitectura"),
        ("net+", "CompTIA Network+ (N10-008) - Fundamentos TCP/IP y Subnetting"),
        ("ejpt", "eLearnSecurity Junior Penetration Tester v2 (INE) - Pentest Práctico"),
        ("cjca", "Certified Junior Cybersecurity Analyst (TCM) - SOC, SIEM y PCAP"),
        ("pjpt", "Practical Junior Penetration Tester (TCM) - Active Directory"),
        ("btl1", "Blue Team Level 1 (SBT) - Phishing, Splunk, Forense"),
        ("ceh", "Certified Ethical Hacker (EC-Council) - Escaneo y Metodología"),
    ],
    "certs": [
        ("isc2", "ISC2 CC"),
        ("sec+", "CompTIA Security+"),
        ("ejpt", "eLearnSecurity eJPT"),
        ("cjca", "TCM Security CJCA"),
    ],
    "quiz": [
        ("isc2", "Simulacro ISC2 Certified in Cybersecurity (CC)"),
        ("sec+", "Simulacro CompTIA Security+ (SY0-701)"),
        ("net+", "Simulacro CompTIA Network+ (N10-008)"),
        ("ejpt", "Simulacro eLearnSecurity Junior Pentester (eJPT)"),
        ("cjca", "Simulacro Certified Junior Cyber Analyst (CJCA)"),
        ("pjpt", "Simulacro Practical Junior Pentester (PJPT)"),
        ("btl1", "Simulacro Blue Team Level 1 (BTL1)"),
        ("ceh", "Simulacro Certified Ethical Hacker (CEH)"),
    ],
    "qz": [
        ("isc2", "Simulacro ISC2 CC"),
        ("sec+", "Simulacro CompTIA Sec+"),
        ("ejpt", "Simulacro eJPT"),
        ("cjca", "Simulacro CJCA"),
    ],
    "open": [
        ("1", "Abrir el recurso [1] en el navegador"),
        ("2", "Abrir el recurso [2] en el navegador"),
        ("3", "Abrir el recurso [3] en el navegador"),
        ("4", "Abrir el recurso [4] en el navegador"),
    ],
    "o": [
        ("1", "Abrir el recurso [1] en el navegador"),
        ("2", "Abrir el recurso [2] en el navegador"),
        ("3", "Abrir el recurso [3] en el navegador"),
    ],
    "mentor": [
        ("como empezar en soc", "Ruta y laboratorios de Analista SOC y Blue Team"),
        ("busca cursos udemy", "Buscar cupones 100% libres y filtros de Udemy"),
        ("iniciarme en hacking etico", "Ruta formativa recomendada desde cero"),
        ("seguridad web y owasp", "Laboratorios y cursos prácticos de aplicaciones web"),
        ("ingenieria inversa", "Recursos y binarios de práctica de reversing"),
    ],
    "study": [
        ("como empezar en soc", "Ruta y laboratorios de Analista SOC y Blue Team"),
        ("busca cursos udemy", "Buscar cupones 100% libres y filtros de Udemy"),
        ("iniciarme en hacking etico", "Ruta formativa recomendada desde cero"),
        ("seguridad web y owasp", "Laboratorios y cursos prácticos de aplicaciones web"),
    ],
    "provider": [
        ("gemini", "Google Gemini 3.8 Flash (Activo y rápido)"),
        ("openai", "OpenAI GPT-4o / GPT-4o-mini"),
        ("claude", "Anthropic Claude 3.5 Sonnet / Haiku"),
    ],
    "model": [
        ("1", "Seleccionar modelo #1"),
        ("2", "Seleccionar modelo #2"),
        ("3", "Seleccionar modelo #3"),
        ("gemini-3.8-flash", "Gemini 3.8 Flash (Recomendado)"),
        ("gemini-3.7-flash", "Gemini 3.7 Flash (Razonamiento)"),
        ("claude-3-5-sonnet-latest", "Claude 3.5 Sonnet (Reversing)"),
        ("gpt-4o", "OpenAI GPT-4o (Multimodal)"),
        ("gpt-4o-mini", "OpenAI GPT-4o Mini (Rápido)"),
    ],
    "m": [
        ("1", "Seleccionar modelo #1"),
        ("2", "Seleccionar modelo #2"),
        ("3", "Seleccionar modelo #3"),
    ],
    "mode": [
        ("ctf", "Modo resolución de retos técnicos"),
        ("mentor", "Modo formación y mentoría de estudio"),
        ("diag", "Modo diagnóstico de herramientas"),
    ],
    "roadmap": [
        ("pentesting", "Ruta de Pentesting y Seguridad Ofensiva"),
        ("blue_team", "Ruta de SOC y Defensa (Blue Team)"),
        ("forensics", "Ruta de Análisis Forense Digital"),
        ("reversing", "Ruta de Reversing e Ingeniería Inversa"),
        ("fundamentals", "Ruta de Fundamentos de Ciberseguridad"),
    ],
    "tool": [
        ("b64d", "Decodifica Base64 a texto"),
        ("b64e", "Codifica texto a Base64"),
        ("hexd", "Decodifica cadena Hexadecimal a texto"),
        ("hexe", "Codifica texto a Hexadecimal"),
        ("rot13", "Aplica rotación ROT13"),
        ("caesar", "Fuerza bruta de 25 rotaciones César"),
        ("vigenere", "Descifra Vigenère con clave"),
        ("binary", "Convierte ceros y unos binarios a texto"),
        ("morse", "Decodifica código Morse"),
        ("hashid", "Identifica algoritmo de hash (MD5, SHA1, etc.)"),
        ("magic", "Inspecciona magic bytes de archivo"),
        ("strings", "Extrae cadenas ASCII y UTF-16"),
        ("exif", "Extrae metadatos de imágenes"),
        ("url", "Inspecciona cabeceras HTTP de una URL"),
        ("reverse", "Invierte el orden de los caracteres"),
    ],
    "pt": [
        ("start", "Iniciar servicio Packet Tools y abrir Dashboard Web (http://localhost:3000)"),
        ("web", "Abrir Dashboard Web de Packet Tools en el navegador"),
        ("open", "Abrir Dashboard Web en el navegador"),
        ("status", "Ver estado del servidor web (Next.js) y backend API"),
        ("stop", "Detener los servicios en ejecución de Packet Tools"),
        ("install", "Descargar y ejecutar instalador oficial de Windows (v1.2.4)"),
        ("help", "Mostrar guía y opciones de Packet Tools Web Platform"),
    ],
}


# Estilo visual moderno para el menú emergente de autocompletado en terminal
COMPLETION_STYLE = Style.from_dict({
    "completion-menu.completion": "bg:#1e1e1e #00d7d7",
    "completion-menu.completion.current": "bg:#005f87 #ffffff bold",
    "completion-menu.meta.completion": "bg:#1e1e1e #aaaaaa",
    "completion-menu.meta.completion.current": "bg:#005f87 #ffff5f bold",
    "scrollbar.background": "bg:#121212",
    "scrollbar.button": "bg:#444444",
})


class CTFCommandCompleter(Completer):
    """
    Autocompletador para la terminal interactiva de CTF-AI Solver Pro.
    Sugiere comandos al escribir '/' o el nombre del comando, y sub-argumentos contextuales.
    """

    def __init__(self, router=None):
        self.router = router
        self.path_completer = PathCompleter(expanduser=True)

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        text_before_cursor = document.text_before_cursor.lstrip()

        # Caso 1: Sugerencia de comando principal (primer token)
        if " " not in text_before_cursor:
            typed = text_before_cursor
            has_slash = typed.startswith("/")
            query = typed.lstrip("/").lower()

            for name, aliases, desc, cat in COMMANDS_REGISTRY:
                all_names = [name] + aliases
                # Coincidencia si el comando o sus alias empiezan por lo que el usuario escribió
                matches = any(n.startswith(query) for n in all_names) or (query in name)

                if matches:
                    completion_text = f"/{name}" if has_slash else name
                    display_text = f"/{name}" if has_slash else name
                    meta_text = f"[{cat}] {desc}"

                    # Si el usuario ya escribió '/', reemplazamos desde el inicio del token
                    yield Completion(
                        text=completion_text,
                        start_position=-len(typed),
                        display=display_text,
                        display_meta=meta_text,
                    )

        # Caso 2: Sugerencia de sub-argumentos para comandos específicos
        else:
            parts = text_before_cursor.split()
            cmd_token = parts[0].lstrip("/").lower()

            # Autocompletado de rutas del sistema de archivos de la PC para /file o /f
            if cmd_token in ("file", "f"):
                cmd_prefix_len = len(parts[0])
                sub_text = text_before_cursor[cmd_prefix_len:].lstrip()
                sub_doc = Document(sub_text, cursor_position=len(sub_text))
                for comp in self.path_completer.get_completions(sub_doc, complete_event):
                    yield comp
                return

            # Autocompletado dinámico para /model o /m basado en el router activo
            if cmd_token in ("model", "m") and self.router is not None and len(parts) <= 2:
                arg_query = parts[1].lower() if len(parts) == 2 and not text_before_cursor.endswith(" ") else ""
                replace_len = len(parts[1]) if len(parts) == 2 and not text_before_cursor.endswith(" ") else 0

                try:
                    models = self.router.get_available_models()
                except Exception:
                    models = []

                if models:
                    for idx, m in enumerate(models, 1):
                        idx_str = str(idx)
                        m_id = m.get("id", "")
                        desc = m.get("description", "")

                        # Sugerencia por número
                        if not arg_query or idx_str.startswith(arg_query):
                            yield Completion(
                                text=idx_str,
                                start_position=-replace_len,
                                display=f"#{idx_str} ({m_id})",
                                display_meta=desc[:45],
                            )

                        # Sugerencia por ID de modelo
                        if not arg_query or m_id.lower().startswith(arg_query) or arg_query in m_id.lower():
                            yield Completion(
                                text=m_id,
                                start_position=-replace_len,
                                display=m_id,
                                display_meta=desc[:45],
                            )

                    # Sugerencia de proveedores alternativos
                    for p_name, p_desc in [
                        ("claude", "Ver catálogo de Anthropic Claude"),
                        ("openai", "Ver catálogo de OpenAI"),
                        ("gemini", "Ver catálogo de Google Gemini"),
                    ]:
                        if not arg_query or p_name.startswith(arg_query) or arg_query in p_name:
                            yield Completion(
                                text=p_name,
                                start_position=-replace_len,
                                display=p_name,
                                display_meta=p_desc,
                            )
                    return

            # Solo autocompletar el segundo argumento si estamos sobre él
            if cmd_token in SUB_ARGUMENTS and len(parts) <= 2:
                arg_query = parts[1].lower() if len(parts) == 2 and not text_before_cursor.endswith(" ") else ""
                replace_len = len(parts[1]) if len(parts) == 2 and not text_before_cursor.endswith(" ") else 0

                for opt, opt_desc in SUB_ARGUMENTS[cmd_token]:
                    if not arg_query or opt.startswith(arg_query) or arg_query in opt:
                        yield Completion(
                            text=opt,
                            start_position=-replace_len,
                            display=opt,
                            display_meta=opt_desc,
                        )
