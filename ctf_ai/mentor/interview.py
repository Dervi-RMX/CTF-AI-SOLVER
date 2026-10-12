"""
Módulo de Entrevista de Diagnóstico para Cybersecurity Study Mentor
Recopila datos esenciales para personalizar la ruta de aprendizaje sin pedir datos innecesarios.
"""

from typing import Any, Dict, List, Optional
import json
from pathlib import Path


class StudentProfile:
    """Perfil del estudiante con sus metas, disponibilidad y preferencias."""

    def __init__(
        self,
        level: str = "Principiante",
        target_role: str = "Pentester / Seguridad Ofensiva",
        weekly_hours: int = 5,
        budget_mode: str = "100% Gratuito",
        background: str = "Conocimientos generales de informática",
        desired_certs: Optional[List[str]] = None,
        learning_preference: str = "Práctica + Laboratorios",
        completed_topics: Optional[List[str]] = None,
    ):
        self.level = level
        self.target_role = target_role
        self.weekly_hours = max(1, int(weekly_hours))
        self.budget_mode = budget_mode
        self.background = background
        self.desired_certs = desired_certs or []
        self.learning_preference = learning_preference
        self.completed_topics = completed_topics or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "target_role": self.target_role,
            "weekly_hours": self.weekly_hours,
            "budget_mode": self.budget_mode,
            "background": self.background,
            "desired_certs": self.desired_certs,
            "learning_preference": self.learning_preference,
            "completed_topics": self.completed_topics,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        return cls(
            level=data.get("level", "Principiante"),
            target_role=data.get("target_role", "Pentester / Seguridad Ofensiva"),
            weekly_hours=data.get("weekly_hours", 5),
            budget_mode=data.get("budget_mode", "100% Gratuito"),
            background=data.get("background", "Conocimientos generales"),
            desired_certs=data.get("desired_certs", []),
            learning_preference=data.get("learning_preference", "Práctica + Laboratorios"),
            completed_topics=data.get("completed_topics", []),
        )

    def save_to_file(self, file_path: str = "study_profile.json") -> bool:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @classmethod
    def load_from_file(cls, file_path: str = "study_profile.json") -> Optional["StudentProfile"]:
        p = Path(file_path)
        if not p.exists():
            return None
        try:
            with open(p, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        except Exception:
            return None


class StudyInterviewer:
    """Gestiona el flujo de diagnóstico conversacional o guiado."""

    ROLES_MAP = {
        "1": "Pentester / Seguridad Ofensiva",
        "2": "Blue Team / Analista SOC",
        "3": "Analista Forense Digital (DFIR)",
        "4": "Ingeniería Inversa y Malware",
        "5": "Seguridad Cloud (AWS/Azure/GCP)",
        "6": "Fundamentos Globales de Ciberseguridad",
    }

    LEVELS_MAP = {
        "1": "Principiante (Desde Cero)",
        "2": "Intermedio (Bases de Redes y Linux)",
        "3": "Avanzado (Profesional en IT o Dev)",
    }

    BUDGET_MAP = {
        "1": "100% Gratuito y Recursos Libres",
        "2": "Bajo Costo (Suscripciones mensuales asequibles)",
        "3": "Preparación para Certificaciones Oficiales",
    }

    @classmethod
    def quick_profile(
        cls,
        target_role: str = "Pentester / Seguridad Ofensiva",
        level: str = "Principiante",
        weekly_hours: int = 5,
        budget: str = "100% Gratuito",
    ) -> StudentProfile:
        """Crea un perfil rápido directamente con valores dados."""
        return StudentProfile(
            level=level,
            target_role=target_role,
            weekly_hours=weekly_hours,
            budget_mode=budget,
        )
