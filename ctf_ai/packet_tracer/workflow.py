"""Caso de uso completo: analizar, validar, ejecutar y producir resultados comprobados."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from ctf_ai.ai_providers import AIRouter
from ctf_ai.packet_tracer.agent import PacketTracerAgent
from ctf_ai.packet_tracer.models import AgentState, NetworkBlueprint
from ctf_ai.packet_tracer.pdf_parser import PracticeAnalyzer
from ctf_ai.packet_tracer.validator import BlueprintIssue, validate_blueprint


@dataclass
class PacketTracerSolveResult:
    """Resultado auditable de una ejecución; no convierte simulaciones en pruebas reales."""

    blueprint: NetworkBlueprint
    issues: list[BlueprintIssue]
    state: AgentState
    source_text: str
    tool_results: list[dict] | None = None

    @property
    def completed(self) -> bool:
        return self.state.status == "completed" and not any(
            issue.severity == "error" for issue in self.issues
        )

    def render_report(self) -> str:
        """Genera un informe basado en estados y respuestas observadas."""
        lines = [
            f"# Informe Packet Tracer: {self.blueprint.title}",
            "",
            f"- **Estado:** {self.state.status}",
            f"- **Progreso:** {self.state.progress_percent:.1f}%",
            f"- **Dispositivos del plano:** {len(self.blueprint.devices)}",
            f"- **Enlaces del plano:** {len(self.blueprint.links)}",
            "",
            "## Validación",
        ]
        if self.issues:
            lines.extend(f"- **{issue.severity.upper()}** `{issue.code}`: {issue.message}" for issue in self.issues)
        else:
            lines.append("- Sin incidencias deterministas.")
        lines.extend(["", "## Operaciones confirmadas"])
        if self.tool_results:
            lines.extend(f"- `{item['operation']}`: `{item['result']}`" for item in self.tool_results)
        else:
            lines.append("- No hay operaciones confirmadas por un adaptador.")
        lines.extend(["", "## Registro"])
        lines.extend(f"- {message}" for message in self.state.logs)
        return "\n".join(lines)


class PacketTracerWorkflow:
    """Orquesta el caso de uso sin permitir que el modelo ejecute código arbitrario."""

    def __init__(self, router: AIRouter, agent: Optional[PacketTracerAgent] = None):
        self.analyzer = PracticeAnalyzer(router)
        self.agent = agent or PacketTracerAgent()

    def solve(
        self,
        practice_text: str = "",
        pdf_paths: Optional[list[str]] = None,
        instructions: str = "",
        save_path: Optional[str] = None,
        on_update: Optional[Callable[[AgentState], None]] = None,
    ) -> PacketTracerSolveResult:
        ok, source_text = self.analyzer.extract_documents(pdf_paths or [], practice_text)
        if not ok:
            blueprint = NetworkBlueprint(title="Práctica sin datos", notes=[source_text])
            state = AgentState(status="error", error_message=source_text)
            return PacketTracerSolveResult(blueprint, validate_blueprint(blueprint), state, source_text, [])

        if instructions.strip():
            source_text += f"\n\n--- Instrucciones adicionales ---\n{instructions.strip()}"
        blueprint = self.analyzer.generate_blueprint_from_text(source_text)
        issues = validate_blueprint(blueprint)
        if any(issue.severity == "error" for issue in issues):
            state = AgentState(status="error", error_message="El plano contiene errores de validación.")
        else:
            state = self.agent.execute_blueprint_sync(
                blueprint,
                save_path=save_path,
                on_update=on_update,
            )
        return PacketTracerSolveResult(
            blueprint,
            issues,
            state,
            source_text,
            list(self.agent.last_results),
        )
