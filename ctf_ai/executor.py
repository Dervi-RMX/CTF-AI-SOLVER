"""
Módulo de Ejecución de Comandos para CTF-AI Solver
Ejecuta comandos de sistema o scripts Python con confirmación previa y registro de historial.
"""

import datetime
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


# Lista de patrones o comandos potencialmente destructivos
DANGEROUS_PATTERNS = [
    "format ",
    "rmdir /s",
    "del /s",
    "del /f",
    "remove-item -recurse c:",
    "remove-item -recurse /",
    "rm -rf /",
    "mkfs",
    ":(){ :|:& };:",
    "diskpart",
    "drop database",
]


class CommandExecutionResult:
    """Resultado de la ejecución de un comando."""

    def __init__(
        self,
        command: str,
        stdout: str,
        stderr: str,
        returncode: int,
        executed: bool = True,
        cancelled: bool = False,
    ):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.executed = executed
        self.cancelled = cancelled
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict:
        return {
            "command": self.command,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
            "executed": self.executed,
            "cancelled": self.cancelled,
            "timestamp": self.timestamp,
        }


class CommandExecutor:
    """Controlador de ejecución con salvaguardas y confirmación interactiva."""

    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.history: List[CommandExecutionResult] = []

    def is_dangerous(self, command: str) -> bool:
        """Comprueba si un comando contiene patrones destructivos para el sistema."""
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in DANGEROUS_PATTERNS)

    def execute(
        self,
        command: str,
        confirm: bool = True,
        confirm_callback: Optional[callable] = None,
        timeout: Optional[int] = None,
    ) -> CommandExecutionResult:
        """
        Ejecuta un comando en la terminal.
        Si confirm=True, invoca confirm_callback o solicita confirmación por consola.
        """
        command = command.strip()
        if not command:
            return CommandExecutionResult("", "", "Comando vacío", 1, executed=False)

        is_danger = self.is_dangerous(command)

        if confirm:
            if confirm_callback:
                allowed = confirm_callback(command, is_danger)
            else:
                warning_prefix = "⚠️  [PELIGROSO] " if is_danger else ""
                sys.stdout.write(f"\n{warning_prefix}¿Ejecutar comando: '{command}'? [S/n]: ")
                sys.stdout.flush()
                try:
                    choice = sys.stdin.readline().strip().lower()
                    allowed = choice in ("", "s", "si", "y", "yes")
                except (KeyboardInterrupt, EOFError):
                    allowed = False

            if not allowed:
                res = CommandExecutionResult(
                    command=command,
                    stdout="",
                    stderr="[Cancelado por el usuario]",
                    returncode=130,
                    executed=False,
                    cancelled=True,
                )
                self.history.append(res)
                return res

        # Ejecución del comando en subproceso
        t_out = timeout or self.default_timeout
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=t_out,
                encoding="utf-8",
                errors="replace",
            )
            res = CommandExecutionResult(
                command=command,
                stdout=process.stdout,
                stderr=process.stderr,
                returncode=process.returncode,
                executed=True,
            )
        except subprocess.TimeoutExpired:
            res = CommandExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Timeout]: El comando tardó más de {t_out} segundos y fue detenido.",
                returncode=124,
                executed=True,
            )
        except Exception as e:
            res = CommandExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Error de ejecución]: {str(e)}",
                returncode=1,
                executed=True,
            )

        self.history.append(res)
        return res

    def execute_python_code(
        self,
        code_str: str,
        confirm: bool = True,
        confirm_callback: Optional[callable] = None,
    ) -> CommandExecutionResult:
        """Ejecuta un script o fragmento de Python en un subproceso aislado."""
        python_cmd = sys.executable or "python"
        command = f'{python_cmd} -c "{code_str}"'
        return self.execute(command, confirm=confirm, confirm_callback=confirm_callback)

    def get_history(self) -> List[CommandExecutionResult]:
        """Obtiene el historial de comandos ejecutados en la sesión."""
        return self.history
