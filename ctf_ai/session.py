"""
Módulo de Gestión de Sesiones para CTF-AI Solver
Almacena el estado, pasos realizados, banderas capturadas y persistencia en disco.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ctf_ai.tools import find_flags
from ctf_ai.core.evidence import EvidenceInventory, EvidenceType
from ctf_ai.core.planner import OperationalPlanner


class CTFStep:
    """Representa un paso individual en el proceso de resolución."""

    def __init__(
        self,
        step_number: int,
        action: str,
        output: str = "",
        notes: str = "",
        timestamp: Optional[str] = None,
    ):
        self.step_number = step_number
        self.action = action
        self.output = output
        self.notes = notes
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "output": self.output,
            "notes": self.notes,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CTFStep":
        return cls(
            step_number=data.get("step_number", 1),
            action=data.get("action", ""),
            output=data.get("output", ""),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp"),
        )


class CTFSession:
    """Gestiona la sesión actual de resolución de un reto CTF."""

    def __init__(self, description: str = ""):
        self.description: str = description
        self.category: str = "Desconocida"
        self.steps: List[CTFStep] = []
        self.found_flags: List[str] = []
        self.evidence: EvidenceInventory = EvidenceInventory()
        self.planner: OperationalPlanner = OperationalPlanner()
        self.created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.start_timestamp: float = time.time()

        if description:
            # Detectar banderas iniciales
            self._check_and_add_flags(description)

    def _check_and_add_flags(self, text: str) -> None:
        """Busca banderas en el texto y las agrega si no están presentes."""
        flags = find_flags(text)
        for f in flags:
            if f not in self.found_flags:
                self.found_flags.append(f)

    def set_description(self, description: str) -> None:
        """Establece o actualiza la descripción del reto."""
        self.description = description
        self._check_and_add_flags(description)

    def add_step(self, action: str, output: str = "", notes: str = "") -> CTFStep:
        """Añade un nuevo paso y comprueba si se encontró una bandera."""
        step_num = len(self.steps) + 1
        step = CTFStep(
            step_number=step_num,
            action=action,
            output=output,
            notes=notes,
        )
        self.steps.append(step)
        if output:
            self._check_and_add_flags(output)
        if notes:
            self._check_and_add_flags(notes)
        return step

    def get_context_summary(self, max_recent_steps: int = 4) -> str:
        """Genera un resumen textual estructurado para pasar como contexto a la IA."""
        lines = [
            f"RETO: {self.description or 'No especificado'}",
            f"CATEGORÍA: {self.category}",
            f"PASOS COMPLETADOS: {len(self.steps)}",
        ]

        if self.found_flags:
            lines.append(f"FLAGS DESCUBIERTAS: {', '.join(self.found_flags)}")

        recent_steps = self.steps[-max_recent_steps:] if self.steps else []
        if recent_steps:
            lines.append("\n--- HISTORIAL DE PASOS RECIENTES ---")
            for s in recent_steps:
                lines.append(f"[Paso {s.step_number}]: {s.action}")
                if s.output:
                    # Truncar salida si es excesivamente larga para ahorrar tokens
                    out_snippet = s.output[:600] + ("..." if len(s.output) > 600 else "")
                    lines.append(f"  Resultado: {out_snippet}")
                if s.notes:
                    lines.append(f"  Conclusiones: {s.notes}")

        return "\n".join(lines)

    def get_elapsed_time(self) -> str:
        """Calcula el tiempo transcurrido desde el inicio de la sesión."""
        elapsed_sec = int(time.time() - self.start_timestamp)
        mins, secs = divmod(elapsed_sec, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours}h {mins}m {secs}s"
        return f"{mins}m {secs}s"

    def save_to_file(self, file_path: str) -> bool:
        """Guarda la sesión actual en formato JSON."""
        data = {
            "description": self.description,
            "category": self.category,
            "found_flags": self.found_flags,
            "created_at": self.created_at,
            "steps": [s.to_dict() for s in self.steps],
            "evidence": self.evidence.to_dict_list(),
            "planner": self.planner.to_dict(),
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @classmethod
    def load_from_file(cls, file_path: str) -> Optional["CTFSession"]:
        """Carga una sesión previa desde un archivo JSON."""
        p = Path(file_path)
        if not p.exists():
            return None

        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)

            session = cls(description=data.get("description", ""))
            session.category = data.get("category", "Desconocida")
            session.found_flags = data.get("found_flags", [])
            session.created_at = data.get("created_at", session.created_at)
            session.steps = [CTFStep.from_dict(s) for s in data.get("steps", [])]

            if "evidence" in data and isinstance(data["evidence"], list):
                session.evidence.load_from_dict_list(data["evidence"])

            if "planner" in data and isinstance(data["planner"], dict):
                session.planner.load_from_dict(data["planner"])

            return session
        except Exception:
            return None
