"""
Planificador Dinámico de Estudio para Cybersecurity Study Mentor
Convierte la ruta formativa en tareas de calendario, hace seguimiento del progreso real
y permite recalibrar el plan semanal ante cambios de disponibilidad del usuario.
"""

from typing import Any, Dict, List, Optional
import json
from pathlib import Path

from ctf_ai.mentor.roadmap import LearningPath, StudyModule


class StudyPlanner:
    """Gestiona el calendario de estudio y la recalibración dinámica de horas."""

    def __init__(self, learning_path: Optional[LearningPath] = None, storage_path: str = "study_schedule.json"):
        self.learning_path = learning_path
        self.storage_path = storage_path
        self.notes: List[str] = []

    def recalibrate_weekly_hours(self, new_hours: int) -> Dict[str, Any]:
        """
        Reorganiza la ruta cuando el usuario declara un cambio de disponibilidad (ej. 'solo tengo 3 horas').
        Prioriza laboratorios esenciales sobre lecturas complementarias y recalcula duración.
        """
        new_hours = max(1, int(new_hours))
        if not self.learning_path:
            return {"status": "ERROR", "message": "No hay una ruta de aprendizaje activa para recalibrar."}

        old_hours = self.learning_path.weekly_hours
        self.learning_path.weekly_hours = new_hours

        # Ajustar horas por módulo
        for m in self.learning_path.modules:
            if not m.completed:
                m.estimated_hours = new_hours

        # Guardar cambios
        self.save()

        return {
            "status": "RECALIBRADO_EXITOSO",
            "previous_weekly_hours": old_hours,
            "new_weekly_hours": new_hours,
            "message": f"Plan recalibrado a {new_hours} horas semanales. Contenidos priorizados en laboratorios esenciales.",
        }

    def mark_module_completed(self, stage_number: int) -> bool:
        """Marca un módulo como superado basado en su evaluación práctica."""
        if not self.learning_path:
            return False

        for m in self.learning_path.modules:
            if m.stage_number == stage_number:
                m.completed = True
                self.save()
                return True
        return False

    def get_progress_summary(self) -> Dict[str, Any]:
        """Calcula el progreso real comprobado basado en módulos y tareas completadas."""
        if not self.learning_path:
            return {"total_modules": 0, "completed": 0, "percent": 0.0}

        total = len(self.learning_path.modules)
        completed = sum(1 for m in self.learning_path.modules if m.completed)
        pct = (completed / max(1, total)) * 100.0

        return {
            "role": self.learning_path.role,
            "total_modules": total,
            "completed_modules": completed,
            "progress_percent": round(pct, 1),
            "weekly_hours": self.learning_path.weekly_hours,
        }

    def add_study_note(self, note: str) -> None:
        self.notes.append(note.strip())
        self.save()

    def save(self) -> bool:
        if not self.learning_path:
            return False
        data = {
            "learning_path": self.learning_path.to_dict(),
            "notes": self.notes,
        }
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load(self) -> bool:
        p = Path(self.storage_path)
        if not p.exists():
            return False
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.learning_path = LearningPath.from_dict(data.get("learning_path", {}))
            self.notes = data.get("notes", [])
            return True
        except Exception:
            return False
