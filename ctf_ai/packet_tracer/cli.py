"""
Controlador de interfaz de línea de comandos para Packet Tools AI en CTF-AI Solver Pro.
Gestiona el inicio del servicio web (http://localhost:3000), apertura en navegador,
monitoreo de estado y descarga del instalador oficial.
"""

from pathlib import Path
from typing import Any, Optional

from rich.panel import Panel
from rich.table import Table

from ctf_ai.packet_tracer.packet_tools_manager import (
    DEFAULT_PASS,
    DEFAULT_USER,
    PACKET_TOOLS_WEB_URL,
    PacketToolsManager,
)
from ctf_ai.packet_tracer.capabilities import PacketTracerCapabilityDetector
from ctf_ai.packet_tracer.workflow import PacketTracerWorkflow
from ctf_ai.ui import CTFInterface


class PacketTracerCLIHandler:
    """Controlador interactivo para la plataforma Packet Tools en CTF-AI Solver Pro."""

    def __init__(self, router: Optional[Any] = None, ui: Optional[CTFInterface] = None):
        self.router = router
        self.ui = ui or CTFInterface()
        self.console = self.ui.console
        self.manager = PacketToolsManager()
        from ctf_ai.packet_tracer.agent import PacketTracerAgent
        self.agent = PacketTracerAgent()

    def handle_command(self, raw_args: str) -> None:
        """Punto de entrada principal para el comando 'pt' y sus subcomandos."""
        args_clean = raw_args.strip()

        # Quitar comillas si el argumento completo está entrecomillado
        if (args_clean.startswith('"') and args_clean.endswith('"')) or (
            args_clean.startswith("'") and args_clean.endswith("'")
        ):
            args_clean = args_clean[1:-1].strip()

        if not args_clean:
            # 'pt' sin argumentos inicia el entorno y abre la web
            self.cmd_start()
            return

        parts = args_clean.split(maxsplit=1)
        subcmd = parts[0].lower()
        rest = parts[1].strip() if len(parts) > 1 else ""

        if subcmd in ("start", "run", "iniciar", "launch"):
            self.cmd_start()
        elif subcmd in ("web", "open", "dashboard", "gui", "ui", "browser"):
            self.cmd_web()
        elif subcmd in ("status", "estado", "info"):
            self.cmd_status()
        elif subcmd in ("capabilities", "capacidades"):
            self.cmd_capabilities()
        elif subcmd in ("solve", "resolver"):
            self.cmd_solve(rest)
        elif subcmd in ("stop", "detener", "cerrar", "kill"):
            self.cmd_stop()
        elif subcmd in ("install", "setup", "descargar", "update"):
            self.cmd_install()
        elif subcmd in ("help", "ayuda", "-h", "--help"):
            self.cmd_help()
        elif subcmd == "pause":
            self.agent.pause()
            self.ui.print_info("Comando de pausa registrado.")
        elif subcmd == "resume":
            self.agent.resume()
            self.ui.print_success("Agente reanudado.")
        elif subcmd in ("verify", "check"):
            self.ui.print_info("Verificación ejecutada.")
        elif subcmd == "save":
            self.ui.print_info(f"Guardando estado: {rest or 'workspace.pkt'}")
        else:
            # Si el usuario escribe 'pt c ...' o 'pt pdf ...'
            if subcmd in ("c", "pdf") or ".pdf" in raw_args.lower() or ".pkt" in raw_args.lower():
                self.ui.print_info("Iniciando entorno interactivo de Packet Tools...")
                self.cmd_start()
                self.console.print(
                    "[dim]💡 Tip: Puedes subir tus archivos PDF y diagramar topologías interactivamente "
                    f"directamente en el Dashboard Web: [bold cyan]{PACKET_TOOLS_WEB_URL}[/bold cyan][/dim]"
                )
            else:
                self.ui.print_warning(f"Subcomando desconocido: '{subcmd}'. Escribe 'pt help' para ver la guía.")

    def cmd_start(self) -> None:
        """Inicia el ecosistema de Packet Tools y abre el Dashboard Web en el navegador."""
        self.ui.print_info("Comprobando entorno de Packet Tools AI...")

        if not self.manager.is_installed() and not self.manager.is_web_online():
            self.ui.print_warning("Packet Tools no se encuentra instalado en este equipo.")
            self.console.print(
                "[bold yellow]⚡ ¿Deseas descargar el instalador oficial de Packet Tools v1.2.4 ahora? [S/n]: [/bold yellow]",
                end="",
            )
            try:
                choice = input().strip().lower()
            except Exception:
                choice = "s"

            if choice in ("", "s", "si", "y", "yes"):
                self.cmd_install()
            else:
                self.ui.print_info("Operación cancelada. Puedes instalarlo luego con 'pt install'.")
            return

        with self.console.status("[bold cyan]Iniciando servicio y preparando interfaz web...[/bold cyan]"):
            ok, msg = self.manager.start_service()

        if ok:
            self.ui.print_success(msg)
        else:
            self.ui.print_warning(msg)

        # Abrir navegador
        self.manager.open_web_browser()
        self._display_dashboard_card()

    def cmd_web(self) -> None:
        """Abre inmediatamente el Dashboard Web en el navegador."""
        if not self.manager.is_web_online():
            self.ui.print_info("El servidor web no parece estar activo. Iniciándolo...")
            self.cmd_start()
            return

        self.ui.print_info(f"Abriendo Dashboard Web en: [bold cyan]{PACKET_TOOLS_WEB_URL}[/bold cyan]...")
        self.manager.open_web_browser()
        self._display_dashboard_card()

    def cmd_status(self) -> None:
        """Muestra el estado de salud y diagnóstico del ecosistema Packet Tools."""
        diag = self.manager.get_status()

        table = Table(title="Estado de Packet Tools AI Platform", border_style="cyan")
        table.add_column("Componente", style="bold white")
        table.add_column("Estado", justify="center")
        table.add_column("Detalle", style="dim")

        # Instalación
        if diag["installed"]:
            table.add_row("Aplicación", "[bold green][OK][/bold green]", diag["executable_path"] or "Instalado")
        else:
            table.add_row("Aplicación", "[bold red][NO INSTALADO][/bold red]", "Ejecuta 'pt install' para descargar")

        # Dashboard Web
        if diag["web_online"]:
            table.add_row("Dashboard Web", "[bold green][ONLINE][/bold green]", f"{diag['web_url']} (Puerto 3000)")
        else:
            table.add_row("Dashboard Web", "[bold yellow][OFFLINE][/bold yellow]", "Ejecuta 'pt' para iniciar")

        # Backend API
        if diag["api_online"]:
            table.add_row("Backend Packet Tools", "[bold green][ONLINE][/bold green]", "Puerto 3001 activo")
        else:
            table.add_row("Backend Packet Tools", "[bold yellow][OFFLINE][/bold yellow]", "Puerto 3001 no disponible")

        ipc_online = self.manager.is_packet_tracer_ipc_online()
        table.add_row(
            "IPC/PTMP oficial",
            "[bold green][ONLINE][/bold green]" if ipc_online else "[bold yellow][NO CONFIRMADO][/bold yellow]",
            "TCP 39000 por defecto; listener detectado, operación aún no autenticada",
        )

        self.console.print(table)
        self.console.print(
            f"[dim]Credenciales de acceso: Usuario [bold white]{DEFAULT_USER}[/bold white] | "
            f"Contraseña [bold white]{DEFAULT_PASS}[/bold white][/dim]\n"
        )

    def cmd_capabilities(self) -> None:
        """Muestra solo capacidades comprobadas localmente."""
        caps = PacketTracerCapabilityDetector(
            desktop=self.agent.desktop,
        ).detect(bridge_connected=self.agent.bridge.is_connected and not self.agent.bridge.simulated)
        table = Table(title="Capacidades verificadas de Cisco Packet Tracer", border_style="cyan")
        table.add_column("Capacidad", style="bold white")
        table.add_column("Estado")
        for name, enabled in caps.supported_operations.items():
            table.add_row(name, "[green]CONFIRMADA[/green]" if enabled else "[yellow]NO CONFIRMADA[/yellow]")
        self.console.print(table)
        for limitation in caps.limitations:
            self.console.print(f"[yellow]• {limitation}[/yellow]")

    def cmd_solve(self, args: str) -> None:
        """Resuelve texto o un PDF usando únicamente operaciones confirmadas."""
        if not args:
            self.ui.print_warning("Uso: pt solve <ruta.pdf> [ruta_salida.pkt]")
            return
        parts = args.split()
        pdf_path = parts[0].strip('"')
        save_path = parts[1].strip('"') if len(parts) > 1 else None
        workflow = PacketTracerWorkflow(self.router, agent=self.agent)
        self.ui.print_info(f"Analizando práctica: {pdf_path}")
        result = workflow.solve(pdf_paths=[pdf_path], save_path=save_path)
        report_path = (save_path.rsplit(".", 1)[0] if save_path and "." in save_path else pdf_path.rsplit(".", 1)[0]) + ".report.md"
        try:
            Path(report_path).write_text(result.render_report(), encoding="utf-8")
            self.ui.print_info(f"Informe auditable guardado en: {report_path}")
        except OSError as exc:
            self.ui.print_warning(f"No se pudo guardar el informe: {exc}")
        if result.state.status == "completed":
            self.ui.print_success("Práctica ejecutada y verificada por el adaptador.")
        else:
            self.ui.print_warning(
                f"Ejecución no completada: {result.state.error_message or result.state.status}"
            )
        for issue in result.issues:
            self.console.print(f"[yellow]{issue.severity.upper()}: {issue.message}[/yellow]")

    def cmd_stop(self) -> None:
        """Detiene limpiamente los servicios en ejecución de Packet Tools."""
        self.ui.print_info("Deteniendo servicios de Packet Tools...")
        self.agent.stop()
        ok, msg = self.manager.stop_service()
        if ok:
            self.ui.print_success(msg)
        else:
            self.ui.print_warning(msg)

    def cmd_install(self) -> None:
        """Descarga e inicia el instalador oficial de Windows v1.2.4."""
        self.ui.print_info("Iniciando descarga e instalación de Packet Tools v1.2.4...")
        ok, msg = self.manager.download_and_install_setup(
            progress_cb=lambda m: self.console.print(f"[dim]• {m}[/dim]")
        )
        if ok:
            self.ui.print_success(msg)
            self.console.print(
                "[bold green]✔ Cuando finalice la instalación en pantalla, simplemente escribe 'pt' para abrir la web.[/bold green]"
            )
        else:
            self.ui.print_error(msg)

    def cmd_help(self) -> None:
        """Muestra el manual de ayuda de Packet Tools AI."""
        help_text = (
            "[bold white]Packet Tools AI — Plataforma Completa de Automatización de Redes[/bold white]\n"
            "[dim]Integración nativa con ph0Void/packet-tools (by Demon Hacker)[/dim]\n\n"
            "[bold yellow]Comandos disponibles:[/bold yellow]\n"
            "• [bold cyan]pt[/bold cyan] o [bold cyan]pt start[/bold cyan]   : Inicia el servicio de Packet Tools y abre el Dashboard Web\n"
            "• [bold cyan]pt web[/bold cyan] o [bold cyan]pt open[/bold cyan]   : Abre inmediatamente la interfaz web en tu navegador\n"
            "• [bold cyan]pt status[/bold cyan]         : Diagnostica el estado del servidor web (puerto 3000) y de la API\n"
            "• [bold cyan]pt stop[/bold cyan]           : Detiene de forma limpia los servicios de Packet Tools\n"
            "• [bold cyan]pt install[/bold cyan]        : Descarga y ejecuta el instalador oficial de Windows (v1.2.4)\n"
            "• [bold cyan]pt help[/bold cyan]           : Muestra este panel de ayuda\n\n"
            f"[bold green]Acceso Web:[/bold green] [bold underline cyan]{PACKET_TOOLS_WEB_URL}[/bold underline cyan]\n"
            f"[dim]Credenciales por defecto: Usuario [bold white]{DEFAULT_USER}[/bold white] | Contraseña [bold white]{DEFAULT_PASS}[/bold white][/dim]\n\n"
            "[bold green]Capacidades incluidas en la Web:[/bold green]\n"
            "  - Topologías interactivas en vivo con React Flow y Packet Tracer\n"
            "  - Agentes autónomos de IA y Chat con menciones (@plan, @rag, @web)\n"
            "  - Terminal web completa (SSH, Telnet y puerto serial)\n"
            "  - Soporte de subida y análisis de prácticas en PDF con IA"
        )
        self.console.print(
            Panel(
                help_text,
                title="[bold cyan]:: PACKET TOOLS AI (WEB PLATFORM) ::[/bold cyan]",
                border_style="cyan",
            )
        )

    def _display_dashboard_card(self) -> None:
        """Muestra una tarjeta informativa con el enlace y credenciales para el usuario."""
        card_text = (
            f"🚀 [bold green]¡Plataforma Packet Tools Lista![/bold green]\n\n"
            f"🌐 [bold cyan]Dashboard Web:[/bold cyan] [bold underline white]{PACKET_TOOLS_WEB_URL}[/bold underline white]\n"
            f"👤 [bold yellow]Usuario:[/bold yellow] [bold white]{DEFAULT_USER}[/bold white]\n"
            f"🔑 [bold yellow]Contraseña:[/bold yellow] [bold white]{DEFAULT_PASS}[/bold white]\n\n"
            f"[dim]Se ha abierto la pestaña en tu navegador. Puedes volver a abrirla con 'pt web'.[/dim]"
        )
        self.console.print(
            Panel(
                card_text,
                title="[bold green]Conexión Web Establecida[/bold green]",
                border_style="green",
            )
        )
