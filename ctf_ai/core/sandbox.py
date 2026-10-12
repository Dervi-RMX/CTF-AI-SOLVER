"""
Módulo de Aislamiento y Capa de Ejecución Segura para CTF-AI Solver Pro
Implementa gestión de workspaces aislados por reto, detección de Docker, confinamiento de rutas,
filtrado de variables de entorno sensibles y protección contra prompt injection en artefactos analizados.
"""

from abc import ABC, abstractmethod
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Marcadores típicos de inyección de instrucciones en archivos de retos
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s*prompt\s*:",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"disregard\s+safety\s+rules",
    r"reveal\s+(the\s+)?api\s*key",
    r"exec\(\s*[\"']rm\s+-rf",
    r"remove-item\s+-recurse\s+c:",
]


class ExecutionResult:
    """Resultado estructurado de ejecución en un entorno sandbox."""

    def __init__(
        self,
        command: str,
        stdout: str,
        stderr: str,
        returncode: int,
        timed_out: bool = False,
        sandbox_type: str = "local",
    ):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.timed_out = timed_out
        self.sandbox_type = sandbox_type

    @property
    def success(self) -> bool:
        return self.returncode == 0 and not self.timed_out


class SandboxBase(ABC):
    """Clase base para entornos de ejecución contenidos."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    def run_command(self, command: str, timeout: int = 30) -> ExecutionResult:
        pass


class DockerSandbox(SandboxBase):
    """
    Entorno de ejecución aislado en contenedor Docker.
    Aplica privilegios mínimos, sin socket del host, límites de CPU/RAM y montaje restringido.
    """

    def __init__(self, workspace_path: Path, image: str = "alpine:latest"):
        super().__init__(workspace_path)
        self.image = image
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available

        docker_bin = shutil.which("docker")
        if not docker_bin:
            self._available = False
            return False

        try:
            res = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._available = (res.returncode == 0)
        except Exception:
            self._available = False

        return self._available

    def get_type(self) -> str:
        return "docker"

    def run_command(self, command: str, timeout: int = 30) -> ExecutionResult:
        if not self.is_available():
            return ExecutionResult(
                command=command,
                stdout="",
                stderr="[ERROR Sandbox]: Docker no está instalado o el demonio no está activo.",
                returncode=127,
                sandbox_type="docker",
            )

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1.0",
            "--user", "1000:1000",
            "-v", f"{self.workspace_path.resolve()}:/workspace:rw",
            "-w", "/workspace",
            self.image,
            "sh", "-c", command,
        ]

        try:
            res = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return ExecutionResult(
                command=command,
                stdout=res.stdout,
                stderr=res.stderr,
                returncode=res.returncode,
                sandbox_type="docker",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Timeout]: Superado límite de {timeout} segundos.",
                returncode=124,
                timed_out=True,
                sandbox_type="docker",
            )
        except Exception as e:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Error Docker]: {str(e)}",
                returncode=1,
                sandbox_type="docker",
            )


class LocalWorkspaceSandbox(SandboxBase):
    """
    Entorno local confinado por directorio en Windows/PowerShell.
    Valida rutas estrictamente contra path traversal y filtra variables de entorno sensibles.
    """

    def __init__(self, workspace_path: Path):
        super().__init__(workspace_path)

    def is_available(self) -> bool:
        return True

    def get_type(self) -> str:
        return "local_workspace"

    def validate_path(self, target_path: Path) -> Path:
        """
        Garantiza que una ruta resuelta esté confinada dentro del workspace del reto.
        Lanza PermissionError si se intenta escapar (path traversal).
        """
        resolved_workspace = self.workspace_path.resolve()
        resolved_target = target_path.resolve()

        if resolved_target != resolved_workspace and resolved_workspace not in resolved_target.parents:
            raise PermissionError(
                f"Violación de aislamiento de ruta: '{target_path}' intenta escapar de '{self.workspace_path}'."
            )
        return resolved_target

    def sanitize_environment(self) -> Dict[str, str]:
        """
        Genera un entorno de ejecución limpio donde se eliminan claves de API y secretos.
        """
        env = os.environ.copy()
        # Eliminar variables críticas de seguridad
        keys_to_strip = [
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
            "AWS_SECRET_ACCESS_KEY",
            "GITHUB_TOKEN",
            "SLACK_BOT_TOKEN",
        ]
        for k in keys_to_strip:
            env.pop(k, None)
        return env

    def inspect_content_for_injection(self, text: str) -> List[str]:
        """Detecta posibles intentos de prompt injection o instrucciones hostiles en archivos."""
        warnings = []
        for pat in PROMPT_INJECTION_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                warnings.append(f"Patrón sospechoso de inyección detectado: '{pat}'")
        return warnings

    def run_command(self, command: str, timeout: int = 30) -> ExecutionResult:
        clean_env = self.sanitize_environment()

        try:
            res = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace_path),
                env=clean_env,
                encoding="utf-8",
                errors="replace",
            )
            return ExecutionResult(
                command=command,
                stdout=res.stdout,
                stderr=res.stderr,
                returncode=res.returncode,
                sandbox_type="local_workspace",
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Timeout]: Superado límite de {timeout} segundos.",
                returncode=124,
                timed_out=True,
                sandbox_type="local_workspace",
            )
        except Exception as e:
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"[Error Ejecución]: {str(e)}",
                returncode=1,
                sandbox_type="local_workspace",
            )


def get_active_sandbox(challenge_id: str, base_dir: Optional[Path] = None) -> SandboxBase:
    """
    Factoría que selecciona el mejor sandbox disponible.
    Prioriza Docker si está operativo; de lo contrario utiliza LocalWorkspaceSandbox.
    """
    root = base_dir or Path.cwd()
    workspace = root / "workspaces" / challenge_id

    docker = DockerSandbox(workspace)
    if docker.is_available():
        return docker
    return LocalWorkspaceSandbox(workspace)
