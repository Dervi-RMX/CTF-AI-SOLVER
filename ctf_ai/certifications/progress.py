"""
Módulo de Persistencia Local de Progreso de Certificaciones.
Guarda y gestiona el avance del estudiante de forma 100% local en su máquina
(resiliente a reinicios y apagados de PC, completamente excluido de GitHub vía .gitignore).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_PROGRESS_FILE = Path.cwd() / "cert_progress.json"


class CertificationProgressTracker:
    """Gestiona el seguimiento persistente de aprendizaje, módulos completados y exámenes finales."""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or DEFAULT_PROGRESS_FILE
        self.data: Dict[str, Any] = {
            "active_cert": None,
            "certifications": {},
            "last_updated": None,
        }
        self.load()

    def load(self) -> None:
        """Carga el progreso guardado desde el archivo local si existe."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                # Si está dañado, inicializar estructura limpia
                self.data = {
                    "active_cert": None,
                    "certifications": {},
                    "last_updated": None,
                }

    def save(self) -> bool:
        """Guarda el estado actual en el disco de la máquina local del usuario."""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get_cert_progress(self, cert_id: str, total_modules: int = 1) -> Dict[str, Any]:
        """Obtiene o inicializa el registro de progreso para una certificación específica."""
        if "certifications" not in self.data:
            self.data["certifications"] = {}

        if cert_id not in self.data["certifications"]:
            self.data["certifications"][cert_id] = {
                "cert_id": cert_id,
                "current_module_index": 0,
                "completed_modules": [],
                "module_scores": {},
                "all_modules_completed": False,
                "final_exam_unlocked": False,
                "final_exam_results": [],
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
            }
            self.save()

        record = self.data["certifications"][cert_id]
        # Asegurar cálculo de campos derivados
        completed_count = len(record.get("completed_modules", []))
        record["completion_percentage"] = round((completed_count / max(1, total_modules)) * 100, 1)
        record["all_modules_completed"] = completed_count >= total_modules
        if record["all_modules_completed"]:
            record["final_exam_unlocked"] = True
        return record

    def set_active_cert(self, cert_id: str) -> None:
        """Establece la certificación activa actual."""
        self.data["active_cert"] = cert_id
        if "certifications" in self.data and cert_id in self.data["certifications"]:
            self.data["certifications"][cert_id]["last_active"] = datetime.now().isoformat()
        self.save()

    def mark_module_completed(
        self,
        cert_id: str,
        module_index: int,
        score: int,
        total: int,
        total_modules: int,
    ) -> Dict[str, Any]:
        """
        Registra la superación exitosa de un módulo de estudio,
        guarda la puntuación y avanza el índice al siguiente módulo.
        """
        record = self.get_cert_progress(cert_id, total_modules=total_modules)
        completed = record.setdefault("completed_modules", [])
        if module_index not in completed:
            completed.append(module_index)
            completed.sort()

        scores = record.setdefault("module_scores", {})
        scores[str(module_index)] = {
            "score": score,
            "total": total,
            "percentage": round((score / max(1, total)) * 100, 1),
            "date": datetime.now().isoformat(),
        }

        # Avanzar el puntero si completó el módulo actual
        if module_index >= record.get("current_module_index", 0):
            record["current_module_index"] = min(module_index + 1, total_modules)

        # Verificar si completó todos los módulos de la certificación
        if len(completed) >= total_modules:
            record["all_modules_completed"] = True
            record["final_exam_unlocked"] = True

        record["last_active"] = datetime.now().isoformat()
        self.save()
        return record

    def get_step_progress(self, cert_id: str, module_index: int) -> Dict[str, Any]:
        """Obtiene el avance de pasos y conceptos individuales dentro de un módulo específico."""
        record = self.get_cert_progress(cert_id)
        steps_map = record.setdefault("module_steps", {})
        mod_key = str(module_index)
        if mod_key not in steps_map:
            steps_map[mod_key] = {
                "current_step_index": 0,
                "completed_steps": [],
                "ready_for_module_exam": False,
            }
            self.save()
        return steps_map[mod_key]

    def mark_step_completed(self, cert_id: str, module_index: int, step_index: int, total_steps: int) -> Dict[str, Any]:
        """Marca un concepto individual del módulo como comprendido y avanza el paso."""
        record = self.get_cert_progress(cert_id)
        steps_map = record.setdefault("module_steps", {})
        mod_key = str(module_index)
        mod_data = steps_map.setdefault(mod_key, {
            "current_step_index": 0,
            "completed_steps": [],
            "ready_for_module_exam": False,
        })
        completed = mod_data.setdefault("completed_steps", [])
        if step_index not in completed:
            completed.append(step_index)
            completed.sort()

        if step_index >= mod_data.get("current_step_index", 0):
            mod_data["current_step_index"] = min(step_index + 1, total_steps)

        if len(completed) >= total_steps:
            mod_data["ready_for_module_exam"] = True

        record["last_active"] = datetime.now().isoformat()
        self.save()
        return mod_data

    def save_paused_exam(self, cert_id: str, exam_data: Dict[str, Any]) -> None:
        """Guarda una sesión de examen en pausa (ej. examen de 100 preguntas)."""
        record = self.get_cert_progress(cert_id)
        record["paused_exam"] = exam_data
        record["last_active"] = datetime.now().isoformat()
        self.save()

    def get_paused_exam(self, cert_id: str) -> Optional[Dict[str, Any]]:
        """Recupera la sesión de examen pausada si existe."""
        record = self.get_cert_progress(cert_id)
        return record.get("paused_exam")

    def clear_paused_exam(self, cert_id: str) -> None:
        """Limpia la sesión de examen pausada una vez finalizado el examen."""
        record = self.get_cert_progress(cert_id)
        if "paused_exam" in record:
            del record["paused_exam"]
            self.save()

    def record_final_exam(
        self,
        cert_id: str,
        score: int,
        total: int,
        percentage: float,
        passed: bool,
    ) -> Dict[str, Any]:
        """Registra el resultado de un intento del Gran Examen Final de 100 preguntas."""
        record = self.get_cert_progress(cert_id)
        exam_history = record.setdefault("final_exam_results", [])
        attempt = {
            "attempt_number": len(exam_history) + 1,
            "score": score,
            "total": total,
            "percentage": percentage,
            "passed": passed,
            "date": datetime.now().isoformat(),
        }
        exam_history.append(attempt)
        record["last_active"] = datetime.now().isoformat()
        self.clear_paused_exam(cert_id)
        self.save()
        return attempt

    def reset_progress(self, cert_id: str) -> None:
        """Reinicia el progreso para una certificación si el usuario lo desea."""
        if "certifications" in self.data and cert_id in self.data["certifications"]:
            del self.data["certifications"][cert_id]
            self.save()

