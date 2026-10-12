"""
Módulo del Planificador Operacional y Gestión de Presupuesto para CTF-AI Solver Pro
Gestiona árboles de tareas, priorización, memoria de intentos, detección de estrategias repetidas
y replanificación automática ante fallos o resultados vacíos.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
import datetime
import uuid


class TaskStatus(str, Enum):
    PENDING = "PENDIENTE"
    RUNNING = "EN_EJECUCIÓN"
    SUCCESS = "ÉXITO"
    FAILED = "FALLIDA"
    ABANDONED = "ABANDONADA"


class Task:
    """Representa una tarea o subtarea orientada a un objetivo concreto."""

    def __init__(
        self,
        title: str,
        description: str = "",
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        expected_information: str = "",
        task_id: Optional[str] = None,
        status: TaskStatus = TaskStatus.PENDING,
    ):
        self.id = task_id or f"TSK-{uuid.uuid4().hex[:6].upper()}"
        self.title = title.strip()
        self.description = description.strip()
        self.tool_name = tool_name
        self.tool_args = tool_args or {}
        self.priority = max(1, min(10, int(priority)))
        self.expected_information = expected_information.strip()
        self.status = status if isinstance(status, TaskStatus) else TaskStatus(status)
        self.result: Optional[str] = None
        self.notes: str = ""
        self.created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "priority": self.priority,
            "expected_information": self.expected_information,
            "status": self.status.value,
            "result": self.result,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        raw_status = data.get("status", TaskStatus.PENDING.value)
        status = TaskStatus.PENDING
        for s in TaskStatus:
            if s.value == raw_status or s.name == raw_status:
                status = s
                break

        t = cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            tool_name=data.get("tool_name"),
            tool_args=data.get("tool_args", {}),
            priority=data.get("priority", 5),
            expected_information=data.get("expected_information", ""),
            task_id=data.get("id"),
            status=status,
        )
        t.result = data.get("result")
        t.notes = data.get("notes", "")
        t.created_at = data.get("created_at", t.created_at)
        return t

    def __repr__(self) -> str:
        return f"[{self.id}|{self.status.value}|P{self.priority}] {self.title}"


class OperationalPlanner:
    """Planificador que supervisa la secuencia de tareas, presupuesto y replanificación."""

    def __init__(self, max_iterations: int = 15, timeout_seconds: int = 300):
        self.tasks: List[Task] = []
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.current_iteration = 0
        self.attempted_signatures: List[str] = []
        self.consecutive_empty_results = 0
        self.start_time = datetime.datetime.now()

    def add_task(
        self,
        title: str,
        description: str = "",
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        expected_information: str = "",
    ) -> Task:
        """Crea y añade una tarea priorizada."""
        task = Task(
            title=title,
            description=description,
            tool_name=tool_name,
            tool_args=tool_args,
            priority=priority,
            expected_information=expected_information,
        )
        self.tasks.append(task)
        # Reordenar tareas por prioridad descendente (mayor número primero)
        self.tasks.sort(key=lambda t: t.priority, reverse=True)
        return task

    def get_next_pending_task(self) -> Optional[Task]:
        """Obtiene la siguiente tarea pendiente con mayor prioridad."""
        for t in self.tasks:
            if t.status == TaskStatus.PENDING:
                return t
        return None

    def record_attempt(self, strategy_signature: str) -> bool:
        """
        Registra una estrategia ejecutada.
        Retorna True si ya había sido intentada previamente (estrategia repetida).
        """
        sig_clean = strategy_signature.strip().lower()
        if sig_clean in self.attempted_signatures:
            return True
        self.attempted_signatures.append(sig_clean)
        return False

    def complete_task(self, task_id: str, result: str = "") -> None:
        """Alias para mark_task_success."""
        self.mark_task_success(task_id, result)

    def fail_task(self, task_id: str, error_reason: str = "") -> None:
        """Alias para mark_task_failed."""
        self.mark_task_failed(task_id, error_reason)

    def mark_task_success(self, task_id: str, result_summary: str) -> None:
        """Marca una tarea como completada exitosamente y reinicia contador de fallos vacíos."""
        for t in self.tasks:
            if t.id == task_id:
                t.status = TaskStatus.SUCCESS
                t.result = result_summary
                self.consecutive_empty_results = 0
                break

    def mark_task_failed(self, task_id: str, error_reason: str) -> None:
        """Registra un fallo en la tarea y activa lógica de contingencia."""
        for t in self.tasks:
            if t.id == task_id:
                t.status = TaskStatus.FAILED
                t.notes = error_reason
                self.consecutive_empty_results += 1
                break

    def replan_on_failure(self, failed_task: Task, reason: str = "") -> List[Task]:
        """
        Genera automáticamente tareas alternativas si una técnica fracasó o no arrojó información.
        """
        new_tasks = []
        task_title = failed_task.title.lower()

        # Estrategias adaptativas según la naturaleza del fallo
        if "exif" in task_title or "metadatos" in task_title:
            new_tasks.append(
                self.add_task(
                    title="Extracción profunda de cadenas legibles (strings ASCII + UTF-16)",
                    description="Los metadatos no arrojaron pistas. Analizar contenido crudo del archivo.",
                    tool_name="strings",
                    priority=6,
                )
            )
            new_tasks.append(
                self.add_task(
                    title="Inspección de firmas binarias / Magic bytes y overlays",
                    description="Comprobar si hay un archivo incrustado o comprimido al final de la imagen.",
                    tool_name="magic",
                    priority=5,
                )
            )
        elif "base64" in task_title or "rot13" in task_title:
            new_tasks.append(
                self.add_task(
                    title="Fuerza bruta de cifrado César / rotación",
                    description="Decodificación directa falló. Probar todas las 25 rotaciones.",
                    tool_name="caesar",
                    priority=7,
                )
            )
            new_tasks.append(
                self.add_task(
                    title="Multi-decoder en cadena (heurística recursiva)",
                    description="Intentar desanidar capas múltiples de codificación combinada.",
                    tool_name="multi_decoder",
                    priority=6,
                )
            )
        elif "web" in task_title or "url" in task_title:
            new_tasks.append(
                self.add_task(
                    title="Análisis estático de código fuente y scripts JS",
                    description="Revisar código fuente en busca de endpoints, secretos y lógica de frontend.",
                    tool_name="web_scan_secrets",
                    priority=6,
                )
            )
        elif "rsa" in task_title or failed_task.tool_name == "rsa_math" or "key" in task_title:
            new_tasks.append(
                self.add_task(
                    title="Análisis estadístico e inspección de módulo/claves",
                    description="El ataque RSA directo falló. Evaluar entropía o posibles pistas en texto plano.",
                    tool_name="crypto_stats",
                    priority=6,
                )
            )
        else:
            new_tasks.append(
                self.add_task(
                    title="Análisis alternativo y replanteamiento de hipótesis",
                    description=f"La tarea '{failed_task.title}' no arrojó resultados ({reason or 'fallo'}). Explorar vector alternativo.",
                    priority=5,
                )
            )

        return new_tasks

    def is_budget_exhausted(self) -> bool:
        """Verifica si se ha alcanzado el límite de iteraciones o tiempo."""
        if self.current_iteration >= self.max_iterations:
            return True
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        if elapsed >= self.timeout_seconds:
            return True
        return False

    def get_progress_summary(self) -> str:
        """Devuelve un resumen del estado del planificador."""
        total = len(self.tasks)
        success = sum(1 for t in self.tasks if t.status == TaskStatus.SUCCESS)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)

        return (
            f"Iteración {self.current_iteration}/{self.max_iterations} | "
            f"Tareas: {total} (Completadas: {success}, Fallidas: {failed}, Pendientes: {pending})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_iterations": self.max_iterations,
            "current_iteration": self.current_iteration,
            "tasks": [t.to_dict() for t in self.tasks],
            "attempted_signatures": self.attempted_signatures,
            "consecutive_empty_results": self.consecutive_empty_results,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        self.max_iterations = data.get("max_iterations", 15)
        self.current_iteration = data.get("current_iteration", 0)
        self.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        self.attempted_signatures = data.get("attempted_signatures", [])
        self.consecutive_empty_results = data.get("consecutive_empty_results", 0)
