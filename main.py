#!/usr/bin/env python3
"""
CTF-AI Solver - Punto de Entrada Principal
Asistente interactivo con Inteligencia Artificial para la resolución de retos CTF.
"""

import argparse
import os
import re
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configurar salida UTF-8 en consola de Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ctf_ai.config import get_config
from ctf_ai.ai_providers import AIRouter
from ctf_ai.analyzer import CTFAnalyzer
from ctf_ai.executor import CommandExecutor
from ctf_ai.session import CTFSession
from ctf_ai.ui import CTFInterface
import ctf_ai.tools as ctf_tools
from ctf_ai.core.engine import AutonomousCTFEngine
from ctf_ai.core.evidence import EvidenceType
from ctf_ai.core.file_triage import triage_local_file
from ctf_ai.tools.base import registry as tool_registry
from ctf_ai.mentor.interview import StudentProfile, StudyInterviewer
from ctf_ai.mentor.roadmap import RoadmapGenerator, LearningPath
from ctf_ai.mentor.planner import StudyPlanner
from ctf_ai.mentor.tutor import SocraticTutor
from ctf_ai.mentor.resources import ResourceCatalog
from ctf_ai.mentor.advisor import MentorAdvisor
from ctf_ai.reports import ReportGenerator
from ctf_ai.certifications import (
    CERTIFICATION_CATALOG,
    CertificationQuizEngine,
    CertificationProgressTracker,
    get_cert_by_name_or_alias,
    list_all_certifications,
)
from ctf_ai.completer import CTFCommandCompleter, COMPLETION_STYLE
from ctf_ai.packet_tracer import PacketTracerCLIHandler
from rich.panel import Panel
from rich.table import Table
import shutil


# Intentar importar prompt_toolkit para auto-completado e historial en terminal
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import HTML
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False


def extract_commands_from_markdown(text: str) -> list[str]:
    """Extrae comandos sugeridos dentro de bloques de código markdown."""
    pattern = r"```(?:bash|powershell|cmd|sh|shell)?\r?\n(.*?)\r?\n```"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    commands = []
    for m in matches:
        lines = [line.strip() for line in m.strip().splitlines() if line.strip() and not line.strip().startswith("#")]
        if lines:
            commands.extend(lines)
    return commands


class CTFApp:
    """Aplicación principal y bucle interactivo de CTF-AI Solver Pro."""

    def __init__(self, initial_provider: Optional[str] = None, initial_model: Optional[str] = None):
        self.config = get_config()
        self.router = AIRouter(self.config)
        if initial_provider:
            self.router.set_provider(initial_provider)
        if initial_model:
            self.router.set_model(initial_model)

        self.analyzer = CTFAnalyzer(self.router)
        self.executor = CommandExecutor()
        self.session = CTFSession()
        self.ui = CTFInterface()

        # Componentes Pro
        self.engine = AutonomousCTFEngine(self.router, tool_registry=tool_registry)
        self.student_profile = StudentProfile.load_from_file() or StudentProfile()
        self.learning_path = RoadmapGenerator.generate_for_profile(self.student_profile)
        self.study_planner = StudyPlanner(self.learning_path)
        self.study_planner.load()
        self.tutor = SocraticTutor(self.router)
        self.mentor_advisor = MentorAdvisor(self.router)
        self.mentor_history: list[dict[str, str]] = []
        self.resource_catalog = ResourceCatalog()
        self.cert_engine = CertificationQuizEngine(self.router)
        self.cert_tracker = CertificationProgressTracker()
        self.pt_handler = PacketTracerCLIHandler(self.router, self.ui)
        self.last_links: list[str] = []
        self.active_mode = "ctf"  # ctf, mentor, diag

        self.prompt_session = None
        self.completer = None
        if HAS_PROMPT_TOOLKIT:
            try:
                self.completer = CTFCommandCompleter(router=self.router)
                self.prompt_session = PromptSession(
                    history=InMemoryHistory(),
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self.completer,
                    complete_while_typing=True,
                    style=COMPLETION_STYLE,
                )
            except Exception:
                self.prompt_session = None

    def prompt_user(self, text: Optional[str] = None) -> str:
        """Captura la entrada del usuario con colores reales en el prompt."""
        if self.prompt_session and HAS_PROMPT_TOOLKIT:
            try:
                if text is None or "ctf-ai" in str(text):
                    prompt_val = HTML("<ansicyan><b>ctf-ai</b></ansicyan><ansigreen><b>&gt;</b></ansigreen> ")
                else:
                    prompt_val = text

                raw = self.prompt_session.prompt(prompt_val)
                return raw.strip().lstrip("\ufeff").lstrip("ï»¿")
            except (KeyboardInterrupt, EOFError):
                return "exit"
            except Exception:
                self.prompt_session = None

        fallback_text = "\033[1;36mctf-ai\033[0m\033[1;32m>\033[0m " if (text is None or "ctf-ai" in str(text)) else str(text)
        try:
            raw = input(fallback_text)
            return raw.strip().lstrip("\ufeff").lstrip("ï»¿")
        except (KeyboardInterrupt, EOFError):
            return "exit"

    def handle_open_command(self, target: str) -> None:
        """Abre un recurso numerado o URL directamente en el navegador web del sistema."""
        target = target.strip()
        if not target:
            if self.last_links:
                self.ui.print_info("Enlaces activos en el historial reciente:")
                for i, url in enumerate(self.last_links, 1):
                    self.ui.console.print(f"  [bold yellow][{i}][/bold yellow] [bold cyan]{url}[/bold cyan]")
                self.ui.print_info("Escribe 'open <nº>' (ej. 'open 1') para abrir el curso en tu navegador.")
            else:
                self.ui.print_warning("No hay enlaces activos en el historial. Consulta con '/mentor <tema>' o usa 'open <url>'.")
            return

        if target.isdigit():
            idx = int(target)
            if 1 <= idx <= len(self.last_links):
                url = self.last_links[idx - 1]
                try:
                    webbrowser.open(url)
                    self.ui.print_success(f"Abriendo en tu navegador predeterminado: {url}")
                except Exception as e:
                    self.ui.print_error(f"Error al abrir el navegador: {e}")
            else:
                self.ui.print_warning(f"Índice fuera de rango. Selecciona un número entre 1 y {len(self.last_links)}.")
            return

        if target.startswith("http://") or target.startswith("https://"):
            try:
                webbrowser.open(target)
                self.ui.print_success(f"Abriendo en tu navegador predeterminado: {target}")
            except Exception as e:
                self.ui.print_error(f"Error al abrir el navegador: {e}")
        elif "." in target and not target.endswith(".py") and not target.endswith(".json"):
            url = f"https://{target}"
            try:
                webbrowser.open(url)
                self.ui.print_success(f"Abriendo en tu navegador predeterminado: {url}")
            except Exception as e:
                self.ui.print_error(f"Error al abrir el navegador: {e}")
        else:
            self.ui.print_warning("Uso: open <número_del_curso | url> (ej. 'open 1' o 'open https://letsdefend.io')")

    def handle_model_command(self, args: str) -> None:
        """Lista o selecciona el modelo de IA para el proveedor activo."""
        args = args.strip()
        current_provider = self.router.get_current_provider_name()
        active_model = self.router.get_active_model_name()
        models = self.router.get_available_models()

        if not args:
            self.ui.display_models_menu(current_provider, models, active_model)
            return

        # Si el usuario consulta los modelos de un proveedor específico (/model claude, /model openai, /model gemini)
        if args.lower() in ("claude", "openai", "gemini", "anthropic", "chatgpt", "gpt"):
            prov_target = args.lower()
            if prov_target in ("anthropic",):
                prov_target = "claude"
            elif prov_target in ("chatgpt", "gpt"):
                prov_target = "openai"
            prov_models = self.router.get_available_models(prov_target)
            self.ui.display_models_menu(prov_target, prov_models, self.router.get_active_model_name())
            return

        # Selección por número (1..N)
        if args.isdigit():
            idx = int(args)
            new_model = self.router.set_model_by_index(idx)
            if new_model:
                self.ui.print_success(
                    f"Modelo actualizado a: [bold yellow]{new_model}[/bold yellow] (Proveedor: [bold cyan]{current_provider.upper()}[/bold cyan])"
                )
            else:
                self.ui.print_error(
                    f"Número de modelo inválido ({idx}). Debe estar entre 1 y {len(models)}. Escribe '/model' para ver la lista."
                )
            return

        # Selección por nombre o identificador
        model_name = args.lower()
        matching = next((m["id"] for m in models if m["id"].lower() == model_name), None)
        target = matching or args
        self.router.set_model(target)
        self.ui.print_success(
            f"Modelo actualizado a: [bold yellow]{target}[/bold yellow] (Proveedor: [bold cyan]{current_provider.upper()}[/bold cyan])"
        )

    def handle_file_command(self, args_str: str) -> None:
        """Carga, analiza y opcionalmente resuelve de forma autónoma un archivo de la PC."""
        target_path_str = args_str.strip().strip("\"'")
        if not target_path_str:
            self.ui.print_warning("Uso: file <ruta_del_archivo> (ej. 'file C:\\Users\\...\\reto.bin')")
            return

        file_path = Path(target_path_str)
        if not file_path.exists():
            self.ui.print_error(f"El archivo no existe o la ruta es inválida: {file_path}")
            return

        # 1. Triaje inteligente de archivo (texto o binario)
        with self.ui.console.status("[bold cyan]Realizando triaje e inspección estructural del archivo...[/bold cyan]"):
            try:
                triage = triage_local_file(file_path)
            except Exception as e:
                self.ui.print_error(f"Error al analizar el archivo: {e}")
                return

        # 2. Desplegar ficha técnica
        self.ui.display_file_triage(triage)

        # 3. Detectar si hay flags en el triaje inicial
        found_flags = triage.get("found_flags", [])
        if found_flags:
            for f in found_flags:
                if f not in self.session.found_flags:
                    self.session.found_flags.append(f)
                    self.ui.display_flag(f)
            self.ui.print_success(f"¡Flag(s) descubierta(s) directamente en el archivo!: {', '.join(found_flags)}")

        # 4. Inicializar sesión y motor de evidencias
        challenge_desc = f"Reto basado en archivo local '{file_path.name}'. Tipo: {triage.get('file_type', 'Desconocido')}."
        if triage.get("text_preview"):
            challenge_desc += f"\nContenido textual:\n{triage['text_preview']}"
        elif triage.get("strings_preview"):
            challenge_desc += f"\nCadenas legibles:\n" + "\n".join(triage["strings_preview"][:20])

        self.session = CTFSession(challenge_desc)
        if found_flags:
            self.session.found_flags.extend(found_flags)

        with self.ui.console.status("[bold cyan]Analizando el reto con la IA...[/bold cyan]"):
            self.engine.initialize_challenge(challenge_desc, files=[str(file_path)])
            analysis = self.analyzer.analyze_challenge(challenge_desc)

        self.ui.display_ai_response(analysis["raw_response"], title=f"Estrategia IA para '{file_path.name}'")

        # 5. Ofrecer 'hacer todo' (Auto-Solve autónomo)
        if not self.session.found_flags:
            self.ui.console.print("\n[bold yellow]⚡ ¿Deseas que la IA inicie la resolución automática de este archivo ahora mismo? [S/n]: [/bold yellow]", end="")
            choice = self.prompt_user("").lower()
            if choice in ("", "s", "si", "y", "yes"):
                self.run_solve_loop()
            else:
                self.ui.print_info("Puedes avanzar paso a paso con 'step' o iniciar la resolución cuando gustes con 'solve'.")

    def handle_tool_command(self, args_str: str) -> None:
        """Ejecuta una herramienta integrada de CTF."""
        parts = args_str.strip().split(maxsplit=1)
        if not parts:
            self.ui.display_tools_menu()
            return

        tool_name = parts[0].lower()
        param = parts[1] if len(parts) > 1 else ""

        if tool_name in ("b64d", "base64d", "base64"):
            res = ctf_tools.decode_base64(param)
            self.ui.print_success(f"Base64 Decodificado: {res}")
        elif tool_name in ("b64e", "base64e"):
            res = ctf_tools.encode_base64(param)
            self.ui.print_success(f"Base64 Codificado: {res}")
        elif tool_name in ("hexd", "fromhex"):
            res = ctf_tools.decode_hex(param)
            self.ui.print_success(f"Hex Decodificado: {res}")
        elif tool_name in ("hexe", "tohex"):
            res = ctf_tools.encode_hex(param)
            self.ui.print_success(f"Hex Codificado: {res}")
        elif tool_name == "rot13":
            res = ctf_tools.rot13(param)
            self.ui.print_success(f"ROT13: {res}")
        elif tool_name == "caesar":
            results = ctf_tools.caesar_bruteforce(param)
            self.ui.print_info("Resultados de las 25 rotaciones César:")
            for shift, text in results.items():
                self.ui.console.print(f"  [cyan]+{shift:02d}:[/cyan] {text}")
        elif tool_name == "vigenere":
            v_parts = param.split(maxsplit=1)
            if len(v_parts) < 2:
                self.ui.print_error("Uso: tool vigenere <texto_cifrado> <clave>")
                return
            res = ctf_tools.vigenere_decrypt(v_parts[0], v_parts[1])
            self.ui.print_success(f"Vigenère Descifrado: {res}")
        elif tool_name == "binary":
            res = ctf_tools.from_binary(param)
            self.ui.print_success(f"Binario a Texto: {res}")
        elif tool_name == "morse":
            res = ctf_tools.from_morse(param)
            self.ui.print_success(f"Morse Decodificado: {res}")
        elif tool_name == "hashid":
            algos = ctf_tools.identify_hash(param)
            self.ui.print_info(f"Posibles algoritmos para '{param}': {', '.join(algos)}")
        elif tool_name == "magic":
            res = ctf_tools.analyze_file_magic(param)
            self.ui.print_info(f"Análisis Magic Bytes: {res}")
        elif tool_name == "strings":
            res = ctf_tools.extract_strings(param, min_len=4, max_results=30)
            self.ui.print_info(f"Cadenas encontradas ({len(res)}):")
            for s in res:
                self.ui.console.print(f"  [dim]{s}[/dim]")
        elif tool_name == "exif":
            res = ctf_tools.extract_exif_metadata(param)
            self.ui.print_info(f"Metadatos EXIF: {res}")
        elif tool_name == "url":
            res = ctf_tools.analyze_url(param)
            self.ui.print_info(f"Análisis Web: {res}")
        elif tool_name == "reverse":
            res = ctf_tools.reverse_string(param)
            self.ui.print_success(f"Invertido: {res}")
        elif tool_registry.get(tool_name):
            t = tool_registry.get(tool_name)
            arg_name = list(t.arguments_schema.keys())[0] if t.arguments_schema else "text"
            res = t.run(**{arg_name: param} if param else {})
            if res.success:
                self.ui.print_success(f"[{t.name}]: {res.raw_text}")
            else:
                self.ui.print_error(f"[{t.name}]: {res.error}")
        else:
            self.ui.print_error(f"Herramienta desconocida: '{tool_name}'. Escribe 'tools' para ver la lista.")

    def handle_cert_command(self, args_str: str) -> None:
        """Gestiona la preparación de certificaciones: catálogo, módulos progresivos, persistencia local y examen final."""
        args_clean = args_str.strip()
        all_certs = list_all_certifications()

        # Si no se pasó argumento, mostrar catálogo con el progreso guardado en la máquina
        if not args_clean:
            self.ui.display_certifications_menu(all_certs, tracker=self.cert_tracker)
            self.ui.console.print("\n[bold yellow]👉 Selecciona el número o nombre de la certificación a preparar (ej. 1, isc2, sec+) o ENTER para salir: [/bold yellow]", end="")
            choice = self.prompt_user("").strip()
            if not choice:
                return
            args_clean = choice

        cert = get_cert_by_name_or_alias(args_clean)
        if not cert:
            self.ui.print_error(f"Certificación '{args_clean}' no encontrada. Escribe '/cert' para ver la lista disponible.")
            return

        self.cert_tracker.set_active_cert(cert.cert_id)
        prog = self.cert_tracker.get_cert_progress(cert.cert_id, total_modules=len(cert.study_topics))
        total_mods = len(cert.study_topics)
        completed_mods = prog.get("completed_modules", [])
        curr_idx = prog.get("current_module_index", 0)

        # Caso 1: El usuario ya completó todos los módulos de aprendizaje
        if prog.get("all_modules_completed"):
            self.ui.display_grand_final_exam_banner(cert)
            self.ui.console.print("\n[bold green]🏆 ¡Has completado con éxito todos los módulos de aprendizaje de esta certificación![/bold green]")
            self.ui.console.print(f"[bold yellow]⚡ ¿Deseas iniciar ahora el Gran Examen Final de 100 preguntas de todos los temas? [S/n]: [/bold yellow]", end="")
            exam_choice = self.prompt_user("").strip().lower()
            if exam_choice in ("", "s", "si", "y", "yes"):
                self.run_final_exam_loop(cert.cert_id, num_questions=100)
            else:
                self.ui.console.print("\n[dim]Opciones disponibles: Puedes repetir el examen cuando gustes con 'quiz {cert.cert_id} 100' o repasar los temas con 'roadmap'.[/dim]")
            return

        # Caso 2: El usuario tiene módulos pendientes por completar
        if curr_idx >= total_mods:
            curr_idx = total_mods - 1
        active_topic = cert.study_topics[curr_idx]

        status_text = (
            f"[bold cyan]Preparación Progresiva:[/bold cyan] [bold white]{cert.name}[/bold white] [dim]({cert.vendor})[/dim]\n\n"
            f"• [bold green]Progreso guardado en tu PC:[/bold green] {len(completed_mods)} de {total_mods} módulos completados ({prog.get('completion_percentage', 0.0)}%)\n"
            f"• [bold yellow]Módulo activo en curso:[/bold yellow] Módulo {curr_idx + 1} de {total_mods} — [bold white]{active_topic.title}[/bold white]\n"
            f"• [dim white]El Gran Examen Final de 100 preguntas se desbloqueará automáticamente al terminar todos los módulos.[/dim white]"
        )
        self.ui.console.print(Panel(status_text, title="[bold cyan]:: ESTADO DE TU PREPARACIÓN (LOCAL) ::[/bold cyan]", border_style="cyan"))

        self.ui.console.print(f"\n[bold yellow]⚡ ¿Deseas que la IA inicie tu preparación para el Módulo {curr_idx + 1}: '{active_topic.title}'? [S/n]: [/bold yellow]", end="")
        start_choice = self.prompt_user("").strip().lower()
        if start_choice in ("", "s", "si", "y", "yes"):
            self.run_module_prep_flow(cert, start_idx=curr_idx)
        else:
            self.ui.print_info(f"Tu progreso permanece guardado en tu máquina. Puedes retomar exactamente donde lo dejaste ejecutando '/cert {cert.cert_id}'.")

    def run_module_prep_flow(self, cert: Any, start_idx: int) -> None:
        """Bucle guiado de preparación módulo a módulo con explicaciones paso a paso, comprobación inmediata y examen difícil."""
        curr_idx = start_idx
        total_mods = len(cert.study_topics)

        while curr_idx < total_mods:
            topic = cert.study_topics[curr_idx]
            concept_steps = topic.get_concept_steps()
            total_steps = len(concept_steps)
            step_prog = self.cert_tracker.get_step_progress(cert.cert_id, curr_idx)
            current_s_idx = step_prog.get("current_step_index", 0)

            # Si ya había completado todos los pasos pero no el examen difícil del módulo
            if current_s_idx >= total_steps:
                self.ui.print_info(f"Ya has completado la explicación de los {total_steps} conceptos del Módulo {curr_idx + 1}.")
            else:
                self.ui.print_info(f"Iniciando tutoría interactiva paso a paso para el Módulo {curr_idx + 1}: '{topic.title}'.")
                self.ui.console.print("[dim white]La IA te explicará cada concepto uno por uno con ejemplos reales y te hará una pregunta de verificación en cada paso.[/dim white]\n")

                # FASE 1: Tutoría paso a paso por concepto ("Poco a Poco")
                s_idx = current_s_idx
                while s_idx < total_steps:
                    step = concept_steps[s_idx]
                    self.ui.display_concept_step_header(
                        cert_name=cert.name,
                        module_title=topic.title,
                        step_idx=s_idx,
                        total_steps=total_steps,
                        concept_title=step.concept_title,
                    )

                    # Generar o desplegar la explicación del mentor
                    with self.ui.console.status("[bold cyan]El Mentor de IA está preparando la lección de este concepto...[/bold cyan]"):
                        explanation = self.cert_engine.explain_concept_step(cert, topic, step)

                    self.ui.display_concept_explanation(step.concept_title, explanation)

                    # Pregunta de comprobación inmediata
                    q_data = self.cert_engine.get_concept_check(cert, topic, step, s_idx, total_steps)
                    self.ui.display_concept_check(q_data)

                    step_solved = False
                    while not step_solved:
                        ans = self.prompt_user(f"[{s_idx + 1}/{total_steps}] Tu respuesta al concepto (A/B/C/D) > ").strip().upper()
                        if ans in ("STOP", "EXIT", "Q", "SALIR"):
                            self.ui.print_warning(f"Sesión pausada en el concepto {s_idx + 1} del Módulo {curr_idx + 1}. Tu avance está guardado en tu PC.")
                            return
                        if not re.match(r"^[A-D]", ans):
                            self.ui.print_warning("Por favor ingresa una opción válida: A, B, C o D (o escribe 'stop' para pausar).")
                            continue

                        correct_ans = step.check_question.get("answer", "A").upper()
                        if ans == correct_ans:
                            self.ui.print_success(f"✔ ¡CORRECTO! ({ans})")
                            self.ui.console.print(f"[white]{step.check_question.get('explanation', '')}[/white]\n")
                            self.cert_tracker.mark_step_completed(cert.cert_id, curr_idx, s_idx, total_steps)
                            step_solved = True
                        else:
                            self.ui.print_warning(f"✘ Opción incorrecta ({ans}). La opción esperada es {correct_ans}.")
                            self.ui.console.print(f"[dim white]Explicación Didáctica:[/dim white] {step.check_question.get('explanation', '')}\n")
                            self.ui.console.print("[bold yellow]¿Deseas reintentar la comprobación de este concepto antes de continuar? [S/n]: [/bold yellow]", end="")
                            retry = self.prompt_user("").strip().lower()
                            if retry in ("", "s", "si", "y", "yes"):
                                continue
                            else:
                                self.cert_tracker.mark_step_completed(cert.cert_id, curr_idx, s_idx, total_steps)
                                step_solved = True

                    s_idx += 1
                    if s_idx < total_steps:
                        self.ui.console.print("[bold green]👉 Presiona Enter para pasar al siguiente concepto (o escribe 'stop' para pausar)... [/bold green]", end="")
                        cont = self.prompt_user("").strip().lower()
                        if cont in ("stop", "exit", "q", "salir"):
                            self.ui.print_warning(f"Sesión pausada. Continuarás en el Concepto {s_idx + 1} en tu próxima sesión.")
                            return

            # FASE 2: Examen Difícil del Módulo
            self.ui.display_difficult_module_exam_banner(
                cert_name=cert.name,
                module_title=topic.title,
                num_questions=5,
                passing_pct=70.0,
            )
            self.ui.console.print(f"\n[bold yellow]🔥 ¿Deseas iniciar ahora el Examen Difícil de 5 preguntas del Módulo {curr_idx + 1}? [S/n]: [/bold yellow]", end="")
            exam_confirm = self.prompt_user("").strip().lower()
            if exam_confirm not in ("", "s", "si", "y", "yes"):
                self.ui.print_info(f"Examen de módulo postergado. Tu progreso en todos los conceptos del Módulo {curr_idx + 1} está guardado en tu PC.")
                break

            with self.ui.console.status(f"[bold cyan]Cargando Examen Difícil para Módulo {curr_idx + 1}...[/bold cyan]"):
                self.cert_engine.start_difficult_module_exam(cert.cert_id, module_index=curr_idx, num_questions=5)

            while self.cert_engine.has_next_question():
                q_data = self.cert_engine.get_current_question()
                if not q_data:
                    break
                self.ui.display_cert_quiz_question(q_data)

                while True:
                    user_input = self.prompt_user(f"[{q_data['index']}/{q_data['total']}] Respuesta al Examen > ").strip().upper()
                    if user_input in ("STOP", "EXIT", "Q", "SALIR"):
                        self.ui.print_warning("Examen del módulo pausado. Progreso conservado.")
                        return
                    if re.match(r"^[A-D]", user_input):
                        break
                    self.ui.print_warning("Por favor ingresa una opción válida: A, B, C o D (o 'stop' para pausar).")

                feedback = self.cert_engine.submit_answer(user_input)
                self.ui.display_quiz_feedback(feedback)
                self.ui.console.print()

            scorecard = self.cert_engine.get_scorecard()
            self.ui.display_cert_scorecard(scorecard)

            # Criterio de aprobación del examen difícil (al menos 70%)
            if scorecard.get("percentage", 0.0) >= 70.0:
                updated_prog = self.cert_tracker.mark_module_completed(
                    cert_id=cert.cert_id,
                    module_index=curr_idx,
                    score=scorecard.get("correct", 0),
                    total=scorecard.get("total", 5),
                    total_modules=total_mods,
                )
                self.ui.print_success(f"✔ [OK] ¡MÓDULO {curr_idx + 1} SUPERADO CON ÉXITO! Tu avance oficial ha sido guardado de forma permanente en tu máquina.")

                if updated_prog.get("all_modules_completed"):
                    self.ui.display_grand_final_exam_banner(cert)
                    self.ui.console.print(f"\n[bold yellow]⚡ ¿Deseas iniciar ahora el Gran Examen Final de 100 preguntas de todos los temas (estilo examen real)? [S/n]: [/bold yellow]", end="")
                    final_choice = self.prompt_user("").strip().lower()
                    if final_choice in ("", "s", "si", "y", "yes"):
                        self.run_final_exam_loop(cert.cert_id, num_questions=100)
                    else:
                        self.ui.print_info(f"Has desbloqueado el examen final. Puedes iniciarlo cuando gustes escribiendo '/quiz {cert.cert_id} 100'.")
                    break

                next_topic = cert.study_topics[curr_idx + 1]
                self.ui.console.print(f"\n[bold green]👉 ¿Deseas avanzar de inmediato al siguiente módulo ({curr_idx + 2} de {total_mods}: '{next_topic.title}')? [S/n]: [/bold green]", end="")
                next_choice = self.prompt_user("").strip().lower()
                if next_choice in ("", "s", "si", "y", "yes"):
                    curr_idx += 1
                else:
                    self.ui.print_info(f"Excelente sesión. Tu progreso quedó registrado. Para continuar en tu próxima sesión escribe '/cert {cert.cert_id}'.")
                    break
            else:
                self.ui.print_warning(
                    f"Has obtenido un {scorecard.get('percentage', 0.0)}% en el Examen Difícil (se requiere al menos 70% para convalidarlo). "
                    "Repasa los conceptos clave y vuelve a intentar el examen del módulo cuando estés listo."
                )
                break

    def run_final_exam_loop(self, cert_id: str, num_questions: int = 100) -> None:
        """Ejecuta el Gran Examen Final de 100 preguntas que abarca todos los temas de la certificación con pausa/reanudación."""
        paused = self.cert_tracker.get_paused_exam(cert_id)
        if paused and paused.get("questions"):
            p_curr = paused.get("current_index", 0) + 1
            p_total = paused.get("total_questions", num_questions)
            self.ui.console.print(f"\n[bold yellow]⚡ Se encontró un examen final previo pausado en la pregunta {p_curr} de {p_total}.[/bold yellow]")
            self.ui.console.print("[bold green]¿Deseas reanudar desde donde lo dejaste? [S/n]: [/bold green]", end="")
            resume_choice = self.prompt_user("").strip().lower()
            if resume_choice in ("", "s", "si", "y", "yes"):
                with self.ui.console.status("[bold cyan]Reanudando examen final guardado en tu PC...[/bold cyan]"):
                    cert = self.cert_engine.start_final_exam(cert_id, num_questions=num_questions, resume_from=paused)
            else:
                self.cert_tracker.clear_paused_exam(cert_id)
                with self.ui.console.status("[bold cyan]Cargando nuevo banco integral de 100 preguntas...[/bold cyan]"):
                    cert = self.cert_engine.start_final_exam(cert_id, num_questions=num_questions)
        else:
            with self.ui.console.status(f"[bold cyan]Cargando banco integral de {num_questions} preguntas tipo examen real...[/bold cyan]"):
                cert = self.cert_engine.start_final_exam(cert_id, num_questions=num_questions)

        self.ui.print_success(f"Iniciando el GRAN EXAMEN FINAL de {num_questions} preguntas para: [bold yellow]{cert.name}[/bold yellow]")
        self.ui.console.print("[dim white]Instrucciones: Responde cada pregunta (A, B, C o D). Si necesitas pausar, escribe 'stop' para salir de forma segura.[/dim white]\n")

        while self.cert_engine.has_next_question():
            q_data = self.cert_engine.get_current_question()
            if not q_data:
                break

            self.ui.display_cert_quiz_question(q_data)

            while True:
                user_input = self.prompt_user(f"[{q_data['index']}/{q_data['total']}] Respuesta > ").strip().upper()
                if user_input in ("STOP", "EXIT", "Q", "SALIR"):
                    self.cert_tracker.save_paused_exam(cert_id, self.cert_engine.get_exam_state())
                    self.ui.print_warning(f"Examen final pausado en la pregunta {q_data['index']}. Tu progreso ha quedado guardado en tu PC.")
                    return
                if re.match(r"^[A-D]", user_input):
                    break
                self.ui.print_warning("Por favor ingresa una opción válida: A, B, C o D (o 'stop' para pausar).")

            feedback = self.cert_engine.submit_answer(user_input)
            self.ui.display_quiz_feedback(feedback)
            self.ui.console.print()

        scorecard = self.cert_engine.get_scorecard()
        self.cert_tracker.record_final_exam(
            cert_id=cert.cert_id,
            score=scorecard.get("correct", 0),
            total=scorecard.get("total", num_questions),
            percentage=scorecard.get("percentage", 0.0),
            passed=scorecard.get("passed", False),
        )

        self.ui.display_cert_scorecard(scorecard)

        if scorecard.get("passed", False):
            self.ui.display_grand_diploma(scorecard)

    def handle_quiz_command(self, args_str: str) -> None:
        """Lanza directamente un simulacro de examen por certificación o drill socrático."""
        parts = args_str.strip().split()
        if not parts:
            all_certs = list_all_certifications()
            self.ui.display_certifications_menu(all_certs, tracker=self.cert_tracker)
            self.ui.console.print("\n[bold yellow]👉 ¿De qué certificación deseas realizar el quiz? (ej. 1, isc2, sec+, ejpt): [/bold yellow]", end="")
            choice = self.prompt_user("").strip()
            if not choice:
                return
            target = choice
            count = 5
        else:
            target = parts[0]
            count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5

        cert = get_cert_by_name_or_alias(target)
        if cert:
            if count >= 50:
                self.run_final_exam_loop(cert.cert_id, num_questions=count)
            else:
                self.run_cert_quiz_loop(cert.cert_id, count=count)
        else:
            topic = target
            with self.ui.console.status(f"[bold cyan]Generando pregunta pedagógica sobre '{topic}'...[/bold cyan]"):
                question = self.tutor.generate_quiz_question(topic)
            self.ui.display_ai_response(question, title=f"Drill Técnico: {topic}")

    def run_cert_quiz_loop(self, cert_id: str, count: int = 5) -> None:
        """Ejecuta el simulacro de examen interactivo con retroalimentación inmediata y scorecard final."""
        with self.ui.console.status("[bold cyan]Cargando preguntas oficiales de práctica...[/bold cyan]"):
            cert = self.cert_engine.start_quiz(cert_id, num_questions=count)

        self.ui.print_success(f"Iniciando simulacro de {count} preguntas para: [bold yellow]{cert.name}[/bold yellow]")
        self.ui.console.print("[dim white]Instrucciones: Escribe la letra de tu respuesta (A, B, C o D) y presiona Enter. Escribe 'stop' para salir.[/dim white]\n")

        while self.cert_engine.has_next_question():
            q_data = self.cert_engine.get_current_question()
            if not q_data:
                break

            self.ui.display_cert_quiz_question(q_data)

            while True:
                user_input = self.prompt_user("Tu respuesta (A/B/C/D) > ").strip().upper()
                if user_input in ("STOP", "EXIT", "Q", "SALIR"):
                    self.ui.print_warning("Simulacro pausado por el usuario.")
                    return
                if re.match(r"^[A-D]", user_input):
                    break
                self.ui.print_warning("Por favor ingresa una opción válida: A, B, C o D (o 'stop' para pausar).")

            # Evaluar y mostrar retroalimentación pedagógica
            feedback = self.cert_engine.submit_answer(user_input)
            self.ui.display_quiz_feedback(feedback)
            self.ui.console.print()

        # Scorecard final con diagnóstico por dominios
        scorecard = self.cert_engine.get_scorecard()
        self.ui.display_cert_scorecard(scorecard)

    def run_solve_loop(self) -> None:
        """Bucle asistido de resolución interactiva del reto."""
        if not self.session.description:
            self.ui.print_warning("No hay ningún reto definido. Usa 'challenge <descripción>' primero.")
            return

        self.ui.print_info("Iniciando análisis y resolución asistida con IA...")

        # 1. Análisis inicial si no hay pasos previos
        if not self.session.steps:
            with self.ui.console.status("[bold cyan]Analizando el reto con la IA...[/bold cyan]"):
                analysis = self.analyzer.analyze_challenge(self.session.description)

            self.ui.display_ai_response(analysis["raw_response"], title="Estrategia Inicial del Reto")
            if analysis["found_flags"]:
                for f in analysis["found_flags"]:
                    self.ui.display_flag(f)
                    self.session.found_flags.append(f)

        # 2. Bucle de pasos
        while True:
            step_num = len(self.session.steps) + 1
            self.ui.console.print(f"\n[bold yellow]─── Preparando Paso {step_num} ───[/bold yellow]")

            context_str = self.session.get_context_summary()
            with self.ui.console.status(f"[bold cyan]Pensando siguiente paso {step_num}...[/bold cyan]"):
                thought = self.analyzer.solve_step(context_str, step_num)

            self.ui.display_ai_response(thought, title=f"Siguiente Paso #{step_num}")

            # Buscar posibles banderas en la deducción de la IA
            found_flags = ctf_tools.find_flags(thought)
            if found_flags:
                for f in found_flags:
                    if f not in self.session.found_flags:
                        self.session.found_flags.append(f)
                        self.ui.display_flag(f)

            # Buscar comandos para ejecutar
            cmds = extract_commands_from_markdown(thought)
            cmd_output = ""

            if cmds:
                self.ui.print_info(f"La IA sugirió {len(cmds)} comando(s).")
                for cmd in cmds:
                    confirmed = self.ui.prompt_confirm(cmd, is_dangerous=self.executor.is_dangerous(cmd))
                    if confirmed:
                        with self.ui.console.status(f"[bold green]Ejecutando '{cmd}'...[/bold green]"):
                            res = self.executor.execute(cmd, confirm=False)

                        out_text = (res.stdout + "\n" + res.stderr).strip()
                        self.ui.display_step(step_num, f"Ejecutado: {cmd}", out_text)
                        cmd_output += f"\n[Comando: {cmd}]\n{out_text}"

                        # Revisar si la salida del comando reveló la bandera
                        new_flags = ctf_tools.find_flags(out_text)
                        for f in new_flags:
                            if f not in self.session.found_flags:
                                self.session.found_flags.append(f)
                                self.ui.display_flag(f)
                    else:
                        self.ui.print_warning(f"Comando omitido: {cmd}")

            # Registrar paso en la sesión
            self.session.add_step(
                action=f"Análisis Paso {step_num}",
                output=cmd_output,
                notes=thought[:300],
            )

            if self.session.found_flags:
                self.ui.print_success(f"🚩 ¡Banderas encontradas en esta sesión!: {', '.join(self.session.found_flags)}")

            # Preguntar si continuar
            self.ui.console.print("\nPresiona [bold green][ENTER][/bold green] para avanzar al siguiente paso, o escribe [bold red]'stop'[/bold red] para pausar.")
            user_choice = self.prompt_user("continuar? > ").lower()
            if user_choice in ("stop", "s", "no", "n", "exit", "q"):
                self.ui.print_info("Resolución interactiva pausada. Puedes reanudar con 'solve' cuando gustes.")
                break

    def run(self) -> None:
        """Inicia la interfaz de consola interactiva."""
        self.ui.clear_screen()
        self.ui.display_banner()
        available_providers = self.router.get_available_providers()
        active_provider = self.router.get_current_provider_name()
        self.ui.display_providers(available_providers, active_provider)

        if not available_providers:
            self.ui.print_warning(
                "Aviso: No se encontraron API keys en el archivo .env.\n"
                "Puedes definirlas editando el archivo .env o usando el comando 'provider'."
            )

        while True:
            try:
                line = self.prompt_user()
                if not line:
                    continue

                if line in ("/", "/?"):
                    self.ui.display_slash_commands_menu()
                    continue

                parts = line.split(maxsplit=1)
                cmd = parts[0].lower().lstrip("/")
                args = parts[1] if len(parts) > 1 else ""

                if cmd in ("exit", "quit", "q"):
                    self.ui.print_info("Saliendo de CTF-AI Solver. ¡Hasta la próxima cacería de flags!")
                    break

                elif cmd in ("help", "h", "?", "ayuda"):
                    self.ui.display_help()

                elif cmd in ("tools",):
                    self.ui.display_tools_menu()

                elif cmd in ("clear", "cls"):
                    self.ui.clear_screen()
                    self.ui.display_banner()

                elif cmd in ("challenge", "c"):
                    if not args:
                        self.ui.print_warning("Uso: challenge <descripción del reto o enunciado>")
                    else:
                        self.session = CTFSession(args)
                        with self.ui.console.status("[bold cyan]Iniciando motor de evidencias e hipótesis...[/bold cyan]"):
                            init_data = self.engine.initialize_challenge(args)
                        self.ui.print_success(f"Reto clasificado como: [bold yellow]{init_data['category']}[/bold yellow]")
                        self.ui.display_ai_response(init_data["ai_strategy"], title="Estrategia y Primera Hipótesis")

                elif cmd in ("evidence", "evd"):
                    self.ui.display_evidence_inventory(self.engine.evidence)

                elif cmd in ("plan", "pl"):
                    self.ui.display_task_tree(self.engine.planner)

                elif cmd in ("report", "rep"):
                    filename = args.strip() or "ctf_writeup.md"
                    writeup_md = ReportGenerator.generate_ctf_writeup(
                        challenge_name=self.session.description[:40] or "Reto CTF",
                        category=self.session.category,
                        description=self.session.description,
                        evidence=self.engine.evidence,
                        planner=self.engine.planner,
                        verified_flag=self.engine.verified_flag,
                        duration_str=self.session.get_elapsed_time(),
                    )
                    if ReportGenerator.save_writeup_to_file(writeup_md, filename):
                        self.ui.print_success(f"Informe técnico exportado en '{filename}'")
                    else:
                        self.ui.print_error(f"Error al guardar informe en '{filename}'")

                elif cmd in ("mentor", "study", "panel"):
                    if args.strip():
                        query = args.strip()
                        with self.ui.console.status(f"[bold cyan]Consultando al Mentor de IA sobre '{query[:35]}' ...[/bold cyan]"):
                            advice = self.mentor_advisor.consult(
                                query=query,
                                student_profile=self.student_profile,
                                history=self.mentor_history,
                            )
                        self.ui.display_ai_response(advice, title=f"Mentoría IA: {query[:45]}")

                        matched_courses = self.resource_catalog.search_courses(query)
                        if matched_courses:
                            self.last_links = [
                                getattr(c, "url", c.get("url") if isinstance(c, dict) else "")
                                for c in matched_courses[:6]
                            ]
                            self.ui.display_course_catalog(matched_courses[:6], title="Recursos Verificados Coincidentes")
                    else:
                        self.ui.console.print(Panel(
                            f"[bold cyan]Perfil de Aprendizaje Activo:[/bold cyan]\n"
                            f"• Especialidad: [bold yellow]{self.student_profile.target_role}[/bold yellow]\n"
                            f"• Nivel: {self.student_profile.level}\n"
                            f"• Horas semanales: {self.student_profile.weekly_hours}h\n"
                            f"• Modalidad: {self.student_profile.budget_mode}\n\n"
                            f"[bold green]💬 Conversa con tu Mentor:[/bold green]\n"
                            f"• [white]/mentor busca cursos udemy[/white] [dim](cupones 100% gratis y filtros directos)[/dim]\n"
                            f"• [white]/mentor cómo empezar en hacking web[/white] [dim](consejos y laboratorios recomendados)[/dim]\n"
                            f"• [white]roadmap[/white] [dim](ver tu itinerario formativo personalizado)[/dim]\n"
                            f"• [white]plan-study <horas>[/white] [dim](recalibrar dedicación semanal)[/dim]\n"
                            f"• [white]quiz[/white] [dim](drill técnico socrático de autoevaluación)[/dim]",
                            title="[bold green]Cybersecurity Study Mentor Pro[/bold green]",
                            border_style="green"
                        ))

                elif cmd in ("roadmap", "rm"):
                    if args:
                        self.student_profile.target_role = args.strip()
                        self.learning_path = RoadmapGenerator.generate_for_profile(self.student_profile)
                        self.study_planner.learning_path = self.learning_path
                        self.student_profile.save_to_file()
                    md = self.learning_path.to_markdown()
                    self.ui.console.print(Panel(md, title="[bold green]Itinerario Formativo[/bold green]", border_style="green"))

                elif cmd in ("plan-study", "schedule"):
                    nums = re.findall(r"\d+", args) if args else []
                    if not nums:
                        self.ui.print_warning("Uso: plan-study <horas_semanales> (ej. plan-study 3)")
                    else:
                        res = self.study_planner.recalibrate_weekly_hours(int(nums[0]))
                        self.ui.print_success(res["message"])

                elif cmd in ("cert", "certs", "certificacion"):
                    self.handle_cert_command(args)

                elif cmd in ("quiz", "qz", "drill", "exam"):
                    self.handle_quiz_command(args)

                elif cmd in ("diag", "diagnostics"):
                    import shutil
                    from ctf_ai.core.sandbox import DockerSandbox
                    docker_check = DockerSandbox(Path.cwd() / "workspaces" / "test").is_available()
                    diag_data = {
                        "Google Gemini API": {"ok": self.config.is_provider_configured("gemini"), "detail": "Clave en .env"},
                        "OpenAI API": {"ok": self.config.is_provider_configured("openai"), "detail": "Clave en .env"},
                        "Claude API": {"ok": self.config.is_provider_configured("claude"), "detail": "Clave en .env"},
                        "Docker Daemon": {"ok": docker_check, "detail": "Aislamiento containerizado" if docker_check else "No detectado (Usa Sandbox Local)"},
                        "Local Workspace Sandbox": {"ok": True, "detail": "Confinamiento de rutas y filtrado de variables activado"},
                        "Reversing (objdump/strings)": {"ok": shutil.which("strings") is not None or shutil.which("objdump") is not None, "detail": "Herramientas binarias en PATH"},
                        "Web Tools (curl/nmap)": {"ok": shutil.which("curl") is not None or shutil.which("nmap") is not None, "detail": "Utilidades de red"},
                    }
                    self.ui.display_diagnostics(diag_data)

                elif cmd in ("mode",):
                    if args:
                        self.active_mode = args.strip().lower()
                        self.ui.print_success(f"Modo cambiado a: {self.active_mode.upper()}")
                    else:
                        self.ui.print_info(f"Modo activo: {self.active_mode.upper()} (Opciones: ctf, mentor, diag)")

                elif cmd in ("file", "f"):
                    self.handle_file_command(args)

                elif cmd in ("solve", "s"):
                    self.run_solve_loop()

                elif cmd in ("step", "st"):
                    if not self.session.description:
                        self.ui.print_warning("Primero define un reto con 'challenge <texto>'.")
                    else:
                        step_res = self.engine.execute_next_step()
                        self.ui.print_info(f"Paso ejecutado: {step_res.get('status')} - {step_res.get('task') or ''}")
                        if step_res.get("output"):
                            self.ui.console.print(Panel(step_res["output"][:600], title="Evidencia Obtenida", border_style="cyan"))
                        if step_res.get("verified_flag"):
                            self.ui.display_flag(step_res["verified_flag"])

                elif cmd in ("ask", "a"):
                    if not args:
                        self.ui.print_warning("Uso: ask <pregunta para la IA>")
                    else:
                        with self.ui.console.status("[bold cyan]Consultando a la IA...[/bold cyan]"):
                            answer = self.analyzer.consult(args, context=self.session.get_context_summary())
                        self.ui.display_ai_response(answer, title="Consulta CTF")

                elif cmd in ("tool", "t"):
                    self.handle_tool_command(args)

                elif cmd in ("exec", "!"):
                    if not args:
                        self.ui.print_warning("Uso: exec <comando_terminal>")
                    else:
                        confirmed = self.ui.prompt_confirm(args, is_dangerous=self.executor.is_dangerous(args))
                        if confirmed:
                            res = self.executor.execute(args, confirm=False)
                            out = (res.stdout + "\n" + res.stderr).strip()
                            self.ui.console.print(f"[dim]{out}[/dim]")
                            # Verificar si hay flags en la salida
                            new_flags = ctf_tools.find_flags(out)
                            for f in new_flags:
                                self.session.found_flags.append(f)
                                self.ui.display_flag(f)

                elif cmd in ("provider", "p"):
                    if not args:
                        avail = self.router.get_available_providers()
                        curr = self.router.get_current_provider_name()
                        self.ui.print_info(f"Proveedor activo: {curr.upper()}. Disponibles: {', '.join(avail)}")
                    else:
                        prov_name = args.strip().lower()
                        if self.router.set_provider(prov_name):
                            self.ui.print_success(f"Proveedor cambiado a: {prov_name.upper()}")
                        else:
                            self.ui.print_error(f"No se pudo activar '{prov_name}'. Verifica que su API key esté en .env")

                elif cmd in ("model", "m"):
                    self.handle_model_command(args)

                elif cmd in ("context", "ctx"):
                    summary = self.session.get_context_summary()
                    self.ui.console.print(summary)
                    if self.session.found_flags:
                        self.ui.print_success(f"Flags capturadas: {', '.join(self.session.found_flags)}")

                elif cmd in ("save",):
                    path = args.strip() or "ctf_session.json"
                    if self.session.save_to_file(path):
                        self.ui.print_success(f"Sesión guardada en {path}")
                    else:
                        self.ui.print_error(f"Error al guardar sesión en {path}")

                elif cmd in ("load",):
                    path = args.strip() or "ctf_session.json"
                    loaded = CTFSession.load_from_file(path)
                    if loaded:
                        self.session = loaded
                        self.ui.print_success(f"Sesión cargada desde {path} ({len(self.session.steps)} pasos).")
                    else:
                        self.ui.print_error(f"No se pudo cargar la sesión desde {path}")

                elif cmd in ("open", "o", "browse"):
                    self.handle_open_command(args)

                elif cmd in ("pt", "packet-tracer", "packettracer"):
                    self.pt_handler.handle_command(args)

                else:
                    self.ui.print_error(f"Comando no reconocido: '{cmd}'. Escribe 'help' para ver la guía.")

            except KeyboardInterrupt:
                self.ui.console.print("\n[Operación cancelada con Ctrl+C]")
            except Exception as e:
                self.ui.print_error(f"Error imprevisto: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="CTF-AI Solver - Asistente de Ciberseguridad y CTF")
    parser.add_argument("--provider", "-p", choices=["gemini", "openai", "claude"], help="Proveedor de IA inicial")
    parser.add_argument("--model", "-m", help="Modelo de IA específico a utilizar")
    parser.add_argument("--challenge", "-c", help="Descripción del reto para iniciar directamente")
    parser.add_argument("--file", "-f", help="Cargar reto desde un archivo")

    args = parser.parse_args()
    app = CTFApp(initial_provider=args.provider, initial_model=args.model)

    if args.challenge:
        app.session.set_description(args.challenge)
    elif args.file:
        app.handle_file_command(args.file)

    app.run()


if __name__ == "__main__":
    main()
