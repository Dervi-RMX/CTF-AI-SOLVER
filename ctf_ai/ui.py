"""
Módulo de Interfaz Gráfica de Terminal (TUI) con Rich
Muestra banners, paneles estilizados, formato markdown y alertas interactivas.
"""

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.prompt import Confirm, Prompt


BANNER = r"""
 [bold cyan]   ____ _____ _____      _    ___   ____        _                [/bold cyan]
 [bold cyan]  / ___|_   _|  ___|    / \  |_ _| / ___|  ___ | |_   _____ _ __  [/bold cyan]
 [bold green] | |     | | | |_ _____/ _ \  | |  \___ \ / _ \| \ \ / / _ \ '__| [/bold green]
 [bold green] | |___  | | |  _|_____/ ___ \ | |   ___) | (_) | |\ V /  __/ |    [/bold green]
 [bold yellow]  \____| |_| |_|     /_/   \_\___| |____/ \___/|_| \_/ \___|_|    [/bold yellow]
 [bold magenta]       [+] Asistente Inteligente de Retos CTF en PowerShell [+]    [/bold magenta]
 [bold red]    [#] [bold white on red] CTF-AI SOLVER PRO [/bold white on red] • [bold yellow]Created & Designed by Demon [Demon Hacker][/bold yellow] [#][/bold red]
"""


class CTFInterface:
    """Controlador de la interfaz de consola con Rich."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def clear_screen(self) -> None:
        """Limpia la terminal de forma multiplataforma y robusta."""
        import os
        os.system("cls" if os.name == "nt" else "clear")
        self.console.clear()

    def display_banner(self) -> None:
        """Muestra el banner de inicio con estilo hacker y créditos de Demon."""
        self.console.print(BANNER)
        credits_panel = Panel(
            "[bold white]CTF-AI Solver Pro[/bold white] [dim]•[/dim] "
            "[bold green]Entorno Inteligente de Retos & Study Mentor[/bold green]\n"
            "[bold yellow]Autor & Creador:[/bold yellow] [bold red]Demon[/bold red] [dim](Demon Hacker)[/dim] "
            "[dim]|[/dim] [bold cyan]PowerShell & Python 3.12[/bold cyan]\n"
            "[italic dim white]Escribe 'help' o presiona '/' para autocompletar comandos interactivos.[/italic dim white]",
            border_style="red",
            title="[bold red]:: SISTEMA & CREDITOS ::[/bold red]",
            subtitle="[bold yellow]Created by Demon[/bold yellow]",
        )
        self.console.print(credits_panel)
        self.console.print()

    def display_providers(self, available: List[str], current: str) -> None:
        """Muestra una barra de estado con los proveedores de IA configurados."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="bold green")

        active_label = f"[bold green]{current.upper()} (Activo)[/bold green]"
        other_label = (
            ", ".join([p.upper() for p in available if p != current])
            if len(available) > 1
            else "[dim]Ninguno adicional[/dim]"
        )

        table.add_row("IA Activa:", active_label)
        table.add_row("Disponibles:", other_label)

        self.console.print(Panel(table, title="[bold blue]Estado de Conexión IA[/bold blue]", border_style="blue"))

    def display_ai_response(self, text: str, title: str = "Respuesta de la IA") -> None:
        """Formatea e imprime una respuesta de IA renderizando Markdown."""
        md = Markdown(text)
        self.console.print(Panel(md, title=f"[bold magenta]{title}[/bold magenta]", border_style="magenta"))

    def display_step(self, step_number: int, action: str, output: str = "") -> None:
        """Muestra un paso de resolución estructurado."""
        content = f"[bold yellow]Acción:[/bold yellow] {action}\n"
        if output:
            snippet = output[:800] + ("\n... [salida truncada]" if len(output) > 800 else "")
            content += f"\n[bold cyan]Salida:[/bold cyan]\n[dim]{snippet}[/dim]"

        self.console.print(
            Panel(
                content,
                title=f"[bold green]Paso {step_number}[/bold green]",
                border_style="green",
            )
        )

    def display_flag(self, flag: str) -> None:
        """Muestra una celebración visual destacada al capturar una bandera."""
        content = (
            f"[bold white on green]  🚩 ¡BANDERA CAPTURADA!  [/bold white on green]\n\n"
            f"[bold yellow]{flag}[/bold yellow]\n\n"
            f"[dim green]¡Felicidades! Se ha detectado la bandera en el reto.[/dim green]"
        )
        self.console.print(Panel(content, title="[bold red]FLAG DETECTADA[/bold red]", border_style="red"))

    def print_info(self, message: str) -> None:
        self.console.print(f"[bold cyan]ℹ [INFO]:[/bold cyan] {message}")

    def print_success(self, message: str) -> None:
        self.console.print(f"[bold green]✔ [OK]:[/bold green] {message}")

    def print_warning(self, message: str) -> None:
        self.console.print(f"[bold yellow]⚠ [AVISO]:[/bold yellow] {message}")

    def print_error(self, message: str) -> None:
        self.console.print(f"[bold red]✖ [ERROR]:[/bold red] {message}")

    def prompt_confirm(self, command: str, is_dangerous: bool = False) -> bool:
        """Solicita confirmación al usuario antes de ejecutar un comando."""
        if is_dangerous:
            self.console.print(
                Panel(
                    f"[bold red]ADVERTENCIA: El comando parece potencialmente destructivo:\n\n[/bold red]"
                    f"[bold yellow]{command}[/bold yellow]",
                    title="[bold red]ALERTA DE SEGURIDAD[/bold red]",
                    border_style="red",
                )
            )
            return Confirm.ask("[bold red]¿Confirmas la ejecución de este comando potencialmente peligroso?[/bold red]", default=False)

        self.console.print(f"\n[bold cyan]Comando sugerido:[/bold cyan] [bold white]{command}[/bold white]")
        return Confirm.ask("¿Deseas ejecutar este comando en tu terminal?", default=True)

    def display_help(self) -> None:
        """Muestra la tabla de comandos interactivos disponibles."""
        table = Table(title="⚡ Comandos Interactivos de CTF-AI Solver Pro ⚡", border_style="cyan")
        table.add_column("Comando", style="bold yellow", no_wrap=True)
        table.add_column("Alias", style="bold magenta")
        table.add_column("Descripción", style="white")

        # Comandos CTF Solver
        table.add_row("challenge <texto>", "c", "Define o inicia un nuevo reto CTF")
        table.add_row("file <ruta>", "f", "Carga la descripción o archivo del reto")
        table.add_row("solve", "s", "Inicia el bucle de resolución paso a paso con la IA")
        table.add_row("step", "st", "Ejecuta un solo paso de razonamiento/acción")
        table.add_row("evidence", "evd", "Muestra el inventario de hipótesis y evidencias del reto")
        table.add_row("plan", "pl", "Muestra el árbol de tareas operacionales y presupuesto")
        table.add_row("report [archivo]", "rep", "Exporta informe técnico del reto a Markdown")
        table.add_row("ask <pregunta>", "a", "Consulta cualquier duda libremente a la IA")
        table.add_row("tool <nombre> [args]", "t", "Ejecuta una herramienta integrada (base64, rot13, etc.)")
        table.add_row("exec <comando>", "!", "Ejecuta un comando en la consola (con confirmación)")
        table.add_row("provider <gemini|openai|claude>", "p", "Cambia el modelo o proveedor de IA activo")
        table.add_row("model [id|nº]", "m", "Lista o cambia el modelo de IA para el proveedor activo")
        table.add_row("context", "ctx", "Muestra el contexto acumulado del reto")
        table.add_row("save <ruta>", "", "Guarda la sesión actual en formato JSON")
        table.add_row("load <ruta>", "", "Carga una sesión guardada previamente")

        # Comandos Cybersecurity Study Mentor
        table.add_row("mentor", "study", "Inicia la entrevista y diagnóstico de estudio")
        table.add_row("cert [id]", "certs", "Preparación guiada de certificaciones y drill final")
        table.add_row("roadmap [track]", "rm", "Genera y muestra ruta de aprendizaje personalizada")
        table.add_row("plan-study <horas>", "", "Recalibra el cronograma semanal (ej. plan-study 3)")
        table.add_row("quiz [tema]", "qz", "Inicia un drill socrático de autoevaluación técnica")

        # Comandos Cisco Packet Tracer Automation (Pro)
        table.add_row("pt c <instrucción>", "", "Automatiza red completa en Packet Tracer desde lenguaje natural")
        table.add_row("pt pdf <ruta.pdf>", "", "Resuelve práctica de laboratorio Cisco desde archivo PDF")
        table.add_row("pt status", "", "Ver estado en vivo, telemetría y conexión con Packet Tracer")
        table.add_row("pt pause / pt resume", "", "Pausa o reanuda la automatización de la topología")
        table.add_row("pt verify", "", "Comprueba conectividad (pings ICMP) en la topología activa")
        table.add_row("pt save <ruta.pkt>", "", "Guarda la topología activa en archivo .pkt")
        table.add_row("pt help", "", "Manual detallado y ejemplos de Cisco Packet Tracer")

        # Comandos de Sistema y Diagnóstico
        table.add_row("open <nº|url>", "o, browse", "Abre un curso o enlace web en tu navegador predeterminado")
        table.add_row("diag", "diagnostics", "Diagnóstico del entorno (APIs, Docker, herramientas)")
        table.add_row("tools", "", "Lista todas las utilidades CTF integradas")
        table.add_row("clear", "cls", "Limpia la pantalla de la terminal")
        table.add_row("help", "h, ?", "Muestra este menú de ayuda")
        table.add_row("exit", "q, quit", "Cierra el asistente")

        self.console.print(table)

    def display_evidence_inventory(self, inventory: Any) -> None:
        """Renderiza una tabla estilizada con el inventario de evidencias e hipótesis."""
        table = Table(title="🔍 Inventario de Evidencias e Hipótesis del Reto", border_style="yellow")
        table.add_column("ID", style="bold cyan", no_wrap=True)
        table.add_column("Tipo", style="bold magenta")
        table.add_column("Fuente", style="dim white")
        table.add_column("Descripción", style="white")
        table.add_column("Certeza", style="bold green", justify="right")

        if not inventory.items:
            self.console.print("[dim]No hay evidencias registradas en este momento.[/dim]")
            return

        for ev in inventory.items:
            conf_str = f"{int(ev.confidence * 100)}%"
            color = "green" if "VALIDADA" in ev.evidence_type.value else ("yellow" if "CANDIDATA" in ev.evidence_type.value else "white")
            table.add_row(ev.id, f"[{color}]{ev.evidence_type.value}[/{color}]", ev.source, ev.description[:70], conf_str)

        self.console.print(table)

    def display_task_tree(self, planner: Any) -> None:
        """Muestra el árbol de tareas operacionales y el estado del presupuesto."""
        self.console.print(Panel(planner.get_progress_summary(), title="[bold blue]Presupuesto Operacional[/bold blue]", border_style="blue"))

        table = Table(title="📋 Árbol de Tareas Operacionales", border_style="cyan")
        table.add_column("ID", style="bold cyan", no_wrap=True)
        table.add_column("Prioridad", justify="center")
        table.add_column("Estado", style="bold")
        table.add_column("Tarea", style="white")
        table.add_column("Herramienta", style="italic yellow")

        if not planner.tasks:
            self.console.print("[dim]No hay tareas planificadas actualmente.[/dim]")
            return

        for t in planner.tasks:
            status_color = "green" if t.status.value == "ÉXITO" else ("red" if t.status.value == "FALLIDA" else "cyan")
            table.add_row(t.id, f"P{t.priority}", f"[{status_color}]{t.status.value}[/{status_color}]", t.title, t.tool_name or "-")

        self.console.print(table)

    def display_diagnostics(self, diag: Dict[str, Any]) -> None:
        """Renderiza un panel completo de diagnóstico de entorno y herramientas."""
        table = Table(title="🩺 Diagnóstico del Sistema y Entorno CTF Pro", border_style="green")
        table.add_column("Componente", style="bold white")
        table.add_column("Estado / Versión", style="bold")
        table.add_column("Observaciones", style="dim white")

        for comp, info in diag.items():
            status_str = "[bold green]OK[/bold green]" if info.get("ok") else "[bold red]NO DISPONIBLE[/bold red]"
            table.add_row(comp, status_str, info.get("detail", ""))

        self.console.print(table)

    def display_tools_menu(self) -> None:
        """Lista las herramientas de decodificación y forense integradas."""
        table = Table(title="Herramientas CTF Integradas", border_style="green")
        table.add_column("Herramienta", style="bold cyan")
        table.add_column("Argumentos", style="italic yellow")
        table.add_column("Descripción", style="white")

        table.add_row("b64d", "<texto>", "Decodificar Base64")
        table.add_row("b64e", "<texto>", "Codificar a Base64")
        table.add_row("hexd", "<hex>", "Decodificar Hexadecimal a texto")
        table.add_row("hexe", "<texto>", "Codificar texto a Hexadecimal")
        table.add_row("rot13", "<texto>", "Cifrado o descifrado ROT13")
        table.add_row("caesar", "<texto>", "Fuerza bruta de las 25 rotaciones César")
        table.add_row("vigenere", "<texto> <clave>", "Descifrar Vigenère con clave")
        table.add_row("binary", "<bits>", "Decodificar cadena de ceros y unos")
        table.add_row("morse", "<code>", "Decodificar código Morse (espacio o / entre letras)")
        table.add_row("hashid", "<hash>", "Identificar posible algoritmo de un hash")
        table.add_row("magic", "<ruta_archivo>", "Inspeccionar magic bytes de un archivo")
        table.add_row("strings", "<ruta_archivo>", "Extraer cadenas legibles ASCII de un binario")
        table.add_row("exif", "<ruta_imagen>", "Extraer metadatos EXIF de una imagen")
        table.add_row("url", "<url>", "Analizar headers, comentarios y título de una página")
        table.add_row("reverse", "<texto>", "Invertir una cadena de texto")

        self.console.print(table)

    def display_file_triage(self, triage: Dict[str, Any]) -> None:
        """Muestra una ficha técnica completa de triaje del archivo local."""
        table = Table(
            title=f"Triaje de Archivo Local: {triage.get('name', 'Archivo')}",
            border_style="cyan",
            show_header=False,
            box=None,
            padding=(0, 2),
        )
        table.add_column("Propiedad", style="bold cyan")
        table.add_column("Valor", style="white")

        table.add_row("Ruta:", f"[dim]{triage.get('path', '')}[/dim]")
        table.add_row("Tamaño:", f"[bold yellow]{triage.get('size_str', '')}[/bold yellow] ({triage.get('size_bytes', 0)} bytes)")

        type_desc = f"[bold green]{triage.get('file_type', 'Desconocido')}[/bold green]"
        if triage.get("is_binary"):
            type_desc += " [dim](Binario)[/dim]"
        else:
            type_desc += " [dim](Texto plano / Código)[/dim]"
        table.add_row("Tipo / Magic:", type_desc)

        table.add_row("SHA-256:", f"[dim]{triage.get('sha256', '')}[/dim]")
        table.add_row("MD5:", f"[dim]{triage.get('md5', '')}[/dim]")

        flags = triage.get("found_flags", [])
        if flags:
            table.add_row("Flags Detectadas:", f"[bold white on green] {', '.join(flags)} [/bold white on green]")

        self.console.print(Panel(table, title="[bold cyan]:: FICHA TECNICA DEL ARCHIVO ::[/bold cyan]", border_style="cyan"))

        # Si hay cadenas o previsualización
        if triage.get("strings_preview"):
            sample = "\n".join([f"  • {s}" for s in triage["strings_preview"][:8]])
            self.console.print(Panel(
                f"[bold yellow]Muestreo de Strings / Cadenas Legibles:[/bold yellow]\n{sample}",
                border_style="yellow",
            ))
        elif triage.get("text_preview") and len(triage.get("text_preview", "")) > 10:
            preview = triage["text_preview"][:500] + ("\n... [resto truncado]" if len(triage["text_preview"]) > 500 else "")
            self.console.print(Panel(
                f"[dim]{preview}[/dim]",
                title="[bold blue]Vista Previa de Contenido[/bold blue]",
                border_style="blue",
            ))

    def display_models_menu(self, provider_name: str, models: List[Dict[str, Any]], active_model: str) -> None:
        """Renderiza una tabla con los modelos de IA disponibles para el proveedor actual."""
        if not models:
            self.console.print(Panel(
                f"[yellow]No hay información de modelos disponible para el proveedor '{provider_name}'.[/yellow]",
                title="[bold yellow]Catálogo de Modelos[/bold yellow]",
                border_style="yellow",
            ))
            return

        table = Table(
            title=f"Modelos de IA Disponibles: {provider_name.upper()}",
            caption=(
                "[bold cyan]Tip de Selección:[/bold cyan] "
                "[white]Escribe [/white][bold yellow]/model <número>[/bold yellow][white] (ej. [/white][bold yellow]/model 1[/bold yellow][white]) "
                "o [/white][bold yellow]/model <nombre>[/bold yellow][white] para activarlo inmediatamente.[/white]"
            ),
            border_style="cyan",
        )
        table.add_column("#", style="bold yellow", justify="center", no_wrap=True)
        table.add_column("Modelo ID", style="bold cyan", no_wrap=True)
        table.add_column("Nombre / Etiqueta", style="white")
        table.add_column("Descripción", style="dim white")
        table.add_column("Estado", justify="center", no_wrap=True)

        for idx, m in enumerate(models, 1):
            m_id = m.get("id", "")
            m_name = m.get("name", m_id)
            desc = m.get("description", "")
            is_active = (m_id == active_model) or (active_model and (active_model.endswith(m_id) or m_id.endswith(active_model)))

            if is_active:
                status = "[bold green][ACTIVO][/bold green]"
            elif m.get("recommended"):
                status = "[bold yellow][Recomendado][/bold yellow]"
            else:
                status = "[dim][Disponible][/dim]"

            table.add_row(f"[{idx}]", m_id, m_name, desc, status)

        self.console.print(table)

    def display_slash_commands_menu(self) -> None:
        """Muestra un panel formateado con todos los Slash Commands disponibles al teclear '/'."""
        table = Table(
            title="⚡ Slash Commands Disponibles (/)",
            caption="[bold cyan]💡 Tip:[/bold cyan] [white]Escribe [/white][bold yellow]/[palabra][/bold yellow][white] y pulsa [/white][bold green][Tab][/bold green][white] o flechas [/white][bold green][↑/↓][/bold green][white] para autocompletar interactivamente.[/white]",
            border_style="cyan"
        )
        table.add_column("Slash Command", style="bold yellow")
        table.add_column("Categoría", style="bold magenta")
        table.add_column("Descripción", style="white")

        from ctf_ai.completer import COMMANDS_REGISTRY
        for name, aliases, desc, cat in COMMANDS_REGISTRY:
            alias_str = f" (o /{'/'.join(aliases)})" if aliases else ""
            table.add_row(f"/{name}{alias_str}", cat, desc)

        self.console.print(table)

    def display_course_catalog(self, courses: List[Any], title: str = "Cursos y Recursos Recomendados") -> None:
        """Renderiza una tabla con cursos y recursos de aprendizaje con enlaces nativos OSC 8 e índice para comando 'open'."""
        if not courses:
            self.console.print(Panel(
                "[dim]No se encontraron cursos específicos para esa búsqueda. Intenta con 'soc', 'principiante', 'redes', 'web', 'linux' o 'reversing'.[/dim]",
                title=f"[bold yellow]{title}[/bold yellow]",
                border_style="yellow"
            ))
            return

        table = Table(
            title=f"🎓 {title}",
            caption=(
                "[bold cyan]💡 Tip de Acceso:[/bold cyan] "
                "[white]Escribe [/white][bold yellow]open 1[/bold yellow][white] (o [/white][bold yellow]open {nº}[/bold yellow][white]) para abrir cualquier recurso de inmediato en tu navegador, "
                "o pulsa [/white][bold green][Ctrl + Clic][/bold green][white] sobre el enlace azul.[/white]"
            ),
            border_style="green"
        )
        table.add_column("#", style="bold yellow", justify="center", no_wrap=True)
        table.add_column("Curso / Plataforma", style="bold cyan", no_wrap=False)
        table.add_column("Proveedor", style="white")
        table.add_column("Nivel", style="bold yellow")
        table.add_column("Acceso", style="bold green")
        table.add_column("Enlace Directo", no_wrap=False)
        table.add_column("Habilidades", style="dim white")

        for idx, c in enumerate(courses, 1):
            if hasattr(c, "to_dict"):
                c_data = c.to_dict()
                name = c_data.get("name", "")
                provider = c_data.get("provider", "")
                level = c_data.get("level", "")
                cost = c_data.get("access_type", "Gratis")
                url = c_data.get("url", "")
                skills_str = ", ".join(c_data.get("skills", []))
            elif isinstance(c, dict):
                name = c.get("name") or c.get("title", "")
                provider = c.get("provider", "")
                level = c.get("level", "")
                cost = c.get("access_type") or c.get("cost", "Gratis")
                url = c.get("url", "")
                skills_str = ", ".join(c.get("skills", []))
            else:
                name = getattr(c, "name", "")
                provider = getattr(c, "provider", "")
                level = getattr(c, "level", "")
                cost = getattr(getattr(c, "access_type", None), "value", "Gratis")
                url = getattr(c, "url", "")
                skills_str = ", ".join(getattr(c, "skills", []))

            # Renderizar hipervínculo OSC 8 nativo de terminal
            link_cell = f"[bold cyan underline link={url}]Abrir [{idx}] ↗[/bold cyan underline link={url}]\n[dim]{url}[/dim]"
            table.add_row(f"[{idx}]", name, provider, level, cost, link_cell, skills_str)

        self.console.print(table)

    def display_certifications_menu(self, certs: List[Any], tracker: Optional[Any] = None) -> None:
        """Muestra el catálogo visual de certificaciones con el progreso local persistido en la máquina del usuario."""
        table = Table(
            title="🎯 Catálogo de Certificaciones de Ciberseguridad & Rutas de Preparación Progresiva",
            caption="[bold cyan]💡 Uso:[/bold cyan] Escribe [bold yellow]/cert {nº o nombre}[/bold yellow] (ej. [bold yellow]/cert 1[/bold yellow] o [bold yellow]/cert sec+[/bold yellow]) para continuar o iniciar tu preparación.",
            border_style="magenta",
        )
        table.add_column("#", style="bold yellow", justify="center", no_wrap=True)
        table.add_column("Certificación", style="bold cyan", no_wrap=False)
        table.add_column("Entidad", style="white")
        table.add_column("Nivel", style="bold green")
        table.add_column("Passing Score", style="bold yellow")
        table.add_column("Progreso en tu PC", style="bold yellow", justify="center")

        for idx, cert in enumerate(certs, 1):
            c_data = cert.to_dict() if hasattr(cert, "to_dict") else cert
            cert_id = c_data.get("cert_id", "")
            name = c_data.get("name", "")
            vendor = c_data.get("vendor", "")
            level = c_data.get("level", "")
            passing = c_data.get("passing_score", "")
            total_mods = len(c_data.get("study_topics", []))

            progress_str = "[dim]Sin iniciar[/dim]"
            if tracker:
                p = tracker.get_cert_progress(cert_id, total_modules=total_mods)
                done = len(p.get("completed_modules", []))
                pct = p.get("completion_percentage", 0.0)
                if p.get("all_modules_completed"):
                    progress_str = "[bold white on green] ✔ 100% (Listo p/ Examen) [/bold white on green]"
                elif done > 0:
                    progress_str = f"[bold green]{done}/{total_mods} mods ({pct}%)[/bold green]"
                else:
                    progress_str = f"[dim cyan]0/{total_mods} (Nuevo)[/dim cyan]"

            table.add_row(f"[{idx}]", name, vendor, level, passing, progress_str)

        self.console.print(table)

    def display_cert_study_topics(self, cert: Any) -> None:
        """Despliega la ficha curricular exhaustiva y temas de estudio clave para la certificación seleccionada."""
        c = cert.to_dict() if hasattr(cert, "to_dict") else cert
        name = c.get("name", "Certificación")
        vendor = c.get("vendor", "")
        level = c.get("level", "")
        passing = c.get("passing_score", "")
        exam_fmt = c.get("exam_format", "")
        url = c.get("official_url", "")
        desc = c.get("description", "")
        domains = c.get("domains", [])
        study_topics = c.get("study_topics", [])

        # 1. Panel de Encabezado y Metadatos
        header_text = (
            f"[bold white]{name}[/bold white] [dim]•[/dim] [bold cyan]{vendor}[/bold cyan] [dim]({level})[/dim]\n"
            f"[italic]{desc}[/italic]\n\n"
            f"[bold yellow]Formato Oficial:[/bold yellow] {exam_fmt}\n"
            f"[bold green]Criterio de Aprobación:[/bold green] {passing}\n"
            f"[bold cyan]Enlace Oficial:[/bold cyan] [underline link={url}]{url}[/underline link]"
        )
        self.console.print(Panel(header_text, title=f"[bold green]:: PLAN DE PREPARACIÓN OFICIAL ::[/bold green]", border_style="green"))

        # 2. Tabla de Blueprint Ponderado
        if domains:
            domain_table = Table(title="📐 Blueprint Oficial de Dominios (Ponderación de Examen)", border_style="cyan")
            domain_table.add_column("Dominio Oficial", style="bold cyan")
            domain_table.add_column("Peso en el Examen", style="bold yellow", justify="center")
            for d in domains:
                domain_table.add_row(d.get("name", ""), d.get("weight", "N/A"))
            self.console.print(domain_table)

        # 3. Temas de Estudio Estructurados
        if study_topics:
            self.console.print("\n[bold yellow]📚 Temas de Estudio Clave a Dominar:[/bold yellow]")
            for idx, t in enumerate(study_topics, 1):
                dom_title = t.get("domain", "")
                t_title = t.get("title", "")
                concepts = t.get("concepts", [])
                exam_tips = t.get("exam_tips", [])
                labs = t.get("recommended_labs", [])
                resources = t.get("free_resources", [])

                content_parts = [
                    f"[bold cyan]{dom_title}[/bold cyan] [dim]—[/dim] [bold white]{t_title}[/bold white]\n",
                    "[bold yellow]📌 Conceptos Críticos a Memorizar:[/bold yellow]",
                    *[f"  • {c}" for c in concepts],
                ]

                if exam_tips:
                    content_parts.append("\n[bold red]⚡ Exam Tips & Trampas Clásicas:[/bold red]")
                    for tip in exam_tips:
                        content_parts.append(f"  💡 [italic]{tip}[/italic]")

                if labs:
                    content_parts.append("\n[bold green]🧪 Laboratorios Prácticos Recomendados:[/bold green]")
                    for lab in labs:
                        content_parts.append(f"  • {lab}")

                if resources:
                    content_parts.append("\n[bold blue]🔗 Recursos Gratuitos Directos:[/bold blue]")
                    for r in resources:
                        r_name = r.get("name", "Recurso")
                        r_url = r.get("url", "")
                        content_parts.append(f"  • [underline link={r_url}]{r_name}[/underline link] [dim]({r_url})[/dim]")

                self.console.print(Panel(
                    "\n".join(content_parts),
                    title=f"[bold magenta]Módulo {idx}: {t_title}[/bold magenta]",
                    border_style="magenta",
                ))

    def display_cert_quiz_question(self, q_data: Dict[str, Any]) -> None:
        """Renderiza una pregunta tipo examen con opciones A, B, C, D."""
        curr = q_data.get("index", 1)
        total = q_data.get("total", 1)
        cert_name = q_data.get("cert_name", "Certificación")
        domain = q_data.get("domain", "General")
        scenario = q_data.get("scenario", "")
        question = q_data.get("question", "")
        options = q_data.get("options", [])

        lines = [
            f"[bold cyan]Dominio:[/bold cyan] [bold yellow]{domain}[/bold yellow]\n",
        ]

        if scenario:
            lines.append(f"[italic dim white]Escenario de Examen:[/italic dim white]\n[white]{scenario}[/white]\n")

        lines.append(f"[bold white]{question}[/bold white]\n")
        lines.append("[bold cyan]Opciones Disponibles:[/bold cyan]")
        for opt in options:
            lines.append(f"  [bold yellow]{opt[:2]}[/bold yellow] {opt[2:].strip()}")

        self.console.print(Panel(
            "\n".join(lines),
            title=f"[bold green]Simulacro de Examen {cert_name}[/bold green] [bold yellow]• Pregunta {curr} de {total}[/bold yellow]",
            border_style="green",
        ))

    def display_quiz_feedback(self, record: Dict[str, Any]) -> None:
        """Muestra retroalimentación visual e inmediata para la respuesta del usuario."""
        is_correct = record.get("is_correct", False)
        user_choice = record.get("user_choice", "")
        correct_ans = record.get("correct_answer", "")
        explanation = record.get("explanation", "")

        if is_correct:
            content = (
                f"[bold green]✔ ¡RESPUESTA CORRECTA! ({user_choice})[/bold green]\n\n"
                f"[white]{explanation}[/white]"
            )
            border = "green"
            title = "[bold green]:: EVALUACIÓN ::[/bold green]"
        else:
            content = (
                f"[bold red]✘ RESPUESTA INCORRECTA[/bold red]\n"
                f"[yellow]Tu selección:[/yellow] {user_choice} [dim]|[/dim] "
                f"[bold green]Opción Correcta:[/bold green] [bold yellow]{correct_ans}[/bold yellow]\n\n"
                f"[bold white]Explicación Didáctica:[/bold white]\n{explanation}"
            )
            border = "red"
            title = "[bold red]:: EVALUACIÓN ::[/bold red]"

        self.console.print(Panel(content, title=title, border_style=border))

    def display_cert_scorecard(self, scorecard: Dict[str, Any]) -> None:
        """Renderiza el diagnóstico final del simulacro con análisis por dominio y recomendaciones."""
        cert_name = scorecard.get("cert_name", "Certificación")
        vendor = scorecard.get("vendor", "")
        total = scorecard.get("total", 0)
        correct = scorecard.get("correct", 0)
        pct = scorecard.get("percentage", 0.0)
        passing_pct = scorecard.get("passing_percentage", 70.0)
        passing_str = scorecard.get("passing_score", "70%")
        passed = scorecard.get("passed", False)
        domain_breakdown = scorecard.get("domain_breakdown", {})
        recommendations = scorecard.get("recommendations", [])

        if passed:
            verdict_badge = "[bold white on green] 🏆 ¡FELICIDADES! HAS SUPERADO EL SIMULACRO OFICIAL [/bold white on green]"
            verdict_style = "green"
        else:
            verdict_badge = "[bold white on red] ⚠️ REQUIERE REFORZAR CONCEPTOS ANTES DEL EXAMEN [/bold white on red]"
            verdict_style = "red"

        score_text = (
            f"{verdict_badge}\n\n"
            f"[bold white]Certificación Objetivo:[/bold white] [bold cyan]{cert_name}[/bold cyan] ({vendor})\n"
            f"[bold white]Puntuación Obtenida:[/bold white] [bold yellow]{correct} / {total}[/bold yellow] ([bold {'green' if passed else 'red'}]{pct}%[/bold {'green' if passed else 'red'}])\n"
            f"[bold white]Umbral Mínimo Requerido:[/bold white] [bold white]{passing_str}[/bold white] [dim](aprox. {passing_pct}%)[/dim]"
        )
        self.console.print(Panel(score_text, title="[bold yellow]:: RESULTADO DEL SIMULACRO ::[/bold yellow]", border_style=verdict_style))

        # Tabla de Dominios
        if domain_breakdown:
            table = Table(title="📊 Rendimiento por Dominio Oficial del Examen", border_style="cyan")
            table.add_column("Dominio", style="bold cyan")
            table.add_column("Preguntas", justify="center")
            table.add_column("Aciertos", justify="center")
            table.add_column("% Obtenido", justify="center")
            table.add_column("Diagnóstico", justify="center")

            for dom, stats in domain_breakdown.items():
                d_pct = stats.get("percentage", 0.0)
                d_status = stats.get("status", "Reforzar")
                status_formatted = f"[bold green]✔ {d_status}[/bold green]" if d_status == "Dominado" else f"[bold red]⚡ {d_status}[/bold red]"
                table.add_row(
                    dom,
                    str(stats.get("total", 0)),
                    str(stats.get("correct", 0)),
                    f"{d_pct}%",
                    status_formatted,
                )
            self.console.print(table)

        # Recomendaciones de Estudio
        if recommendations:
            rec_lines = [
                "[bold yellow]🎯 Plan de Acción y Próximos Pasos Recomendados:[/bold yellow]",
                *[f"  • {r}" for r in recommendations],
                "",
                "[dim white]💡 Tip: Puedes volver a revisar los temas de estudio con [/dim white][bold cyan]/cert[/bold cyan][dim white] o repetir el simulacro con [/dim white][bold cyan]/quiz[/bold cyan][dim white].[/dim white]",
            ]
            self.console.print(Panel("\n".join(rec_lines), title="[bold blue]Recomendaciones Pedagógicas[/bold blue]", border_style="blue"))

    def display_module_lesson(
        self,
        cert: Any,
        module_index: int,
        total_modules: int,
        topic: Any,
        is_completed: bool = False,
    ) -> None:
        """Despliega la lección temática guiada para el módulo en curso."""
        c = cert.to_dict() if hasattr(cert, "to_dict") else cert
        cert_name = c.get("name", "Certificación")
        t = topic.to_dict() if hasattr(topic, "to_dict") else topic

        dom_title = t.get("domain", "")
        t_title = t.get("title", "")
        concepts = t.get("concepts", [])
        exam_tips = t.get("exam_tips", [])
        labs = t.get("recommended_labs", [])
        resources = t.get("free_resources", [])

        status_tag = "[bold green]✔ MÓDULO SUPERADO PREVIAMENTE[/bold green]" if is_completed else "[bold yellow]⚡ MÓDULO ACTIVO EN PREPARACIÓN[/bold yellow]"

        content_parts = [
            f"[bold white]Certificación:[/bold white] [bold cyan]{cert_name}[/bold cyan] [dim]|[/dim] {status_tag}\n",
            f"[bold cyan]Dominio Oficial:[/bold cyan] [bold white]{dom_title}[/bold white]\n",
            "[bold yellow]📌 Conceptos Críticos que debes dominar:[/bold yellow]",
            *[f"  • {concept}" for concept in concepts],
        ]

        if exam_tips:
            content_parts.append("\n[bold red]⚡ Trampas Clásicas & Exam Tips de la Certificación:[/bold red]")
            for tip in exam_tips:
                content_parts.append(f"  💡 [italic]{tip}[/italic]")

        if labs:
            content_parts.append("\n[bold green]🧪 Laboratorios Prácticos Recomendados:[/bold green]")
            for lab in labs:
                content_parts.append(f"  • {lab}")

        if resources:
            content_parts.append("\n[bold blue]🔗 Recursos y Lecturas Oficiales Gratuitas:[/bold blue]")
            for r in resources:
                content_parts.append(f"  • [underline link={r.get('url', '')}]{r.get('name', '')}[/underline link]")

        panel = Panel(
            "\n".join(content_parts),
            title=f"[bold green]:: MÓDULO {module_index + 1} de {total_modules}: {t_title} ::[/bold green]",
            border_style="green" if is_completed else "yellow",
        )
        self.console.print(panel)

    def display_concept_step_header(
        self,
        cert_name: str,
        module_title: str,
        step_idx: int,
        total_steps: int,
        concept_title: str,
    ) -> None:
        """Despliega un encabezado visual para el concepto individual en curso dentro del módulo."""
        pct = round(((step_idx + 1) / max(1, total_steps)) * 100)
        header_text = (
            f"[bold cyan]Certificación:[/bold cyan] [bold white]{cert_name}[/bold white] [dim]|[/dim] "
            f"[bold yellow]Módulo:[/bold yellow] [white]{module_title}[/white]\n"
            f"[bold green]Progreso en el Módulo:[/bold green] Paso {step_idx + 1} de {total_steps} [dim]({pct}% completado)[/dim]"
        )
        self.console.print(Panel(
            header_text,
            title=f"[bold magenta]:: CONCEPTO {step_idx + 1}/{total_steps}: {concept_title} ::[/bold magenta]",
            border_style="magenta",
        ))

    def display_concept_explanation(self, concept_title: str, explanation_text: str) -> None:
        """Despliega la explicación didáctica paso a paso impartida por el mentor de IA."""
        self.console.print(Panel(
            explanation_text,
            title=f"[bold cyan]📖 Mentoría Paso a Paso: {concept_title}[/bold cyan]",
            border_style="cyan",
        ))

    def display_concept_check(self, q_data: Dict[str, Any]) -> None:
        """Despliega la pregunta interactiva de comprobación inmediata del concepto recién explicado."""
        curr = q_data.get("index", 1)
        total = q_data.get("total", 1)
        concept_title = q_data.get("concept_title", "Concepto")
        scenario = q_data.get("scenario", "")
        question = q_data.get("question", "")
        options = q_data.get("options", [])

        lines = []
        if scenario:
            lines.append(f"[italic dim white]Escenario Práctico:[/italic dim white]\n[white]{scenario}[/white]\n")
        lines.append(f"[bold white]{question}[/bold white]\n")
        lines.append("[bold cyan]Opciones Disponibles:[/bold cyan]")
        for opt in options:
            lines.append(f"  [bold yellow]{opt[:2]}[/bold yellow] {opt[2:].strip()}")

        self.console.print(Panel(
            "\n".join(lines),
            title=f"[bold yellow]❓ Comprobación Inmediata de Comprensión ({curr}/{total}): {concept_title}[/bold yellow]",
            border_style="yellow",
        ))

    def display_difficult_module_exam_banner(
        self,
        cert_name: str,
        module_title: str,
        num_questions: int = 5,
        passing_pct: float = 70.0,
    ) -> None:
        """Muestra el banner de activación del Examen Difícil del Módulo."""
        text = (
            f"[bold white on red]  🔥 EXAMEN DIFÍCIL DEL MÓDULO (EVALUACIÓN DE DOMINIO) 🔥  [/bold white on red]\n\n"
            f"[bold white]Certificación:[/bold white] [bold cyan]{cert_name}[/bold cyan]\n"
            f"[bold white]Módulo:[/bold white] [bold yellow]{module_title}[/bold yellow]\n\n"
            f"Has completado la explicación paso a paso de todos los conceptos del temario.\n"
            f"[bold green]✔ La IA ha verificado tu comprensión y determina que ESTÁS PREPARADO.[/bold green]\n\n"
            f"Ahora pondremos a prueba tu destreza con [bold yellow]{num_questions} preguntas de escenario complejo[/bold yellow].\n"
            f"[bold white]Criterio para Aprobar y Desbloquear el Siguiente Módulo:[/bold white] [bold green]≥ {passing_pct}%[/bold green]\n"
            f"[dim white]Instrucciones: Responde cada pregunta (A, B, C o D). Si necesitas pausar, escribe 'stop'.[/dim white]"
        )
        self.console.print(Panel(text, title="[bold red]:: CONTROL DE CALIDAD Y EXAMEN ::[/bold red]", border_style="red"))

    def display_grand_final_exam_banner(self, cert: Any) -> None:
        """Muestra una celebración visual al desbloquear el Gran Examen Final de 100 preguntas."""
        c = cert.to_dict() if hasattr(cert, "to_dict") else cert
        name = c.get("name", "Certificación")
        passing = c.get("passing_score", "70%")

        text = (
            f"[bold white on green]  🎓 ¡FASE DE APRENDIZAJE COMPLETADA CON ÉXITO!  [/bold white on green]\n\n"
            f"Has superado con éxito todos los módulos temáticos para [bold cyan]{name}[/bold cyan].\n\n"
            f"[bold yellow]⚡ Has desbloqueado el Gran Examen Final de Simulación (100 Preguntas) ⚡[/bold yellow]\n"
            f"Este examen integra preguntas de todos los dominios oficiales de la certificación.\n"
            f"[white]Criterio de Aprobación Oficial:[/white] [bold green]{passing}[/bold green]\n"
            f"[dim white]Tus resultados se guardarán de forma permanente en tu máquina.[/dim white]"
        )
        self.console.print(Panel(text, title="[bold yellow]:: GRAN EXAMEN FINAL DESBLOQUEADO ::[/bold yellow]", border_style="green"))

    def display_grand_diploma(self, scorecard: Dict[str, Any]) -> None:
        """Renderiza un diploma en consola cuando el alumno aprueba el Gran Examen Final."""
        cert_name = scorecard.get("cert_name", "Certificación")
        vendor = scorecard.get("vendor", "")
        pct = scorecard.get("percentage", 0.0)
        score = scorecard.get("correct", 0)
        total = scorecard.get("total", 0)

        diploma_art = (
            f"\n[bold yellow]╔══════════════════════════════════════════════════════════════════════════════╗[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]          [bold white on red]  🏆 CERTIFICADO DE PREPARACIÓN DE ÉLITE EN CIBERSEGURIDAD  [/bold white on red]          [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]╠══════════════════════════════════════════════════════════════════════════════╣[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]                                                                              [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   Se certifica que el estudiante ha completado con excelencia el programa     [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   integral de preparación oficial para la acreditación profesional:           [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]                                                                              [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   [bold cyan]{cert_name.center(72)}[/bold cyan]   [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   [dim white]{('Entidad Emisora: ' + vendor).center(72)}[/dim white]   [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]                                                                              [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   Puntuación Final: [bold green]{score} de {total} respuestas correctas ({pct}%)[/bold green]                       [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   Veredicto Oficial: [bold white on green] APTO Y COMPLETAMENTE PREPARADO PARA EL EXAMEN REAL [/bold white on green]   [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]                                                                              [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]║[/bold yellow]   [dim]Emitido localmente por CTF-AI Solver Pro • Diseñado por Demon Hacker[/dim]       [bold yellow]║[/bold yellow]\n"
            f"[bold yellow]╚══════════════════════════════════════════════════════════════════════════════╝[/bold yellow]\n"
        )
        self.console.print(diploma_art)



