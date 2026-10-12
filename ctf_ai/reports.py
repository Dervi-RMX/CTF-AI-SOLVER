"""
Módulo Generador de Informes Técnicos y Writeups para CTF-AI Solver Pro
Exporta writeups de CTF profesionales e itinerarios de estudio a Markdown y JSON estructurado.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from ctf_ai.core.evidence import EvidenceInventory, EvidenceType
from ctf_ai.core.planner import OperationalPlanner
from ctf_ai.mentor.roadmap import LearningPath


class ReportGenerator:
    """Generador centralizado de informes técnicos y documentación."""

    @classmethod
    def generate_ctf_writeup(
        cls,
        challenge_name: str,
        category: str,
        description: str,
        evidence: EvidenceInventory,
        planner: OperationalPlanner,
        verified_flag: Optional[str] = None,
        duration_str: str = "N/A",
    ) -> str:
        """Construye un writeup técnico reproducible en Markdown."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ RESUELTO" if verified_flag else "⏳ EN ANÁLISIS"

        lines = [
            f"# 🛡️ CTF Writeup: {challenge_name}",
            f"> **Fecha:** {now} | **Categoría:** {category} | **Estado:** {status} | **Tiempo:** {duration_str}",
            "",
            "---",
            "",
            "## 1. Enunciado y Contexto",
            description,
            "",
            "## 2. Bandera Obtenida (Flag)",
        ]

        if verified_flag:
            lines.append(f"```text\n{verified_flag}\n```\n*Validada y contrastada contra evidencias.*")
        else:
            lines.append("*Bandera aún no confirmada o validada.*")

        lines.extend([
            "",
            "## 3. Matriz de Evidencias e Hipótesis",
            "| ID | Tipo | Fuente | Descripción | Confianza |",
            "|---|---|---|---|---|",
        ])

        for ev in evidence.items:
            conf_pct = f"{int(ev.confidence * 100)}%"
            lines.append(f"| {ev.id} | {ev.evidence_type.value} | {ev.source} | {ev.description[:80]} | {conf_pct} |")

        lines.extend([
            "",
            "## 4. Secuencia de Tareas y Metodología Reproducible",
        ])

        for t in planner.tasks:
            lines.append(f"### 🔹 {t.title} (`{t.status.value}`)")
            if t.tool_name:
                lines.append(f"- **Herramienta:** `{t.tool_name}`")
            if t.result:
                lines.append(f"- **Resultado observado:**\n  ```text\n  {t.result[:300]}\n  ```")
            if t.notes:
                lines.append(f"- **Conclusiones:** {t.notes}")
            lines.append("")

        lines.extend([
            "## 5. Lecciones Aprendidas y Conclusión",
            "Este writeup distingue formalmente entre hipótesis preliminares y evidencias reproducibles observadas durante la ejecución.",
        ])

        return "\n".join(lines)

    @classmethod
    def save_writeup_to_file(cls, markdown_content: str, file_path: str) -> bool:
        """Guarda el informe en disco."""
        try:
            p = Path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(markdown_content, encoding="utf-8")
            return True
        except Exception:
            return False
