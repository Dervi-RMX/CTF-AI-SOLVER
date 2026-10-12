"""
Motor Autónomo de Resolución de Retos CTF (AutonomousCTFEngine) para CTF-AI Solver Pro
Implementa el ciclo riguroso de 13 pasos basado en evidencias:
Hipótesis -> Pruebas concretas -> Hechos observados -> Validación de banderas -> Informe reproducible.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from ctf_ai.ai_providers import AIRouter
from ctf_ai.core.evidence import EvidenceInventory, EvidenceItem, EvidenceType
from ctf_ai.core.planner import OperationalPlanner, Task, TaskStatus
from ctf_ai.core.sandbox import SandboxBase, get_active_sandbox
from ctf_ai.tools.base import ToolRegistry, registry


CTF_PRO_SYSTEM_PROMPT = """Eres el motor analítico de CTF-AI Solver Pro, un especialista de élite en ciberseguridad ofensiva ética y defensiva.
Tu función es razonar con rigor científico basándote estrictamente en EVIDENCIAS:
1. Formula HIPÓTESIS verificables y no asumas hechos sin pruebas.
2. Sugiere herramientas específicas del arsenal (crypto, forensics, reversing, web, network).
3. Si una prueba falla o da resultado vacío, cambia de estrategia en lugar de insistir.
4. Identifica banderas (flags) y verifica si encajan coherentemente con el reto.
"""

FLAG_REGEX = re.compile(r"(?:flag|ctf|picoctf|htb|thm)\{[^}]+\}", re.IGNORECASE)


class AutonomousCTFEngine:
    """Motor central que orquesta la resolución autónoma y guiada basada en evidencias."""

    def __init__(
        self,
        ai_router: AIRouter,
        challenge_id: str = "default_challenge",
        max_iterations: int = 15,
        tool_registry: Optional[ToolRegistry] = None,
    ):
        self.router = ai_router
        self.challenge_id = challenge_id
        self.registry = tool_registry or registry
        self.evidence = EvidenceInventory()
        self.planner = OperationalPlanner(max_iterations=max_iterations)
        self.sandbox: SandboxBase = get_active_sandbox(challenge_id)
        self.challenge_description: str = ""
        self.category: str = "Desconocida"
        self.attached_files: List[Path] = []
        self.verified_flag: Optional[str] = None

    def initialize_challenge(self, description: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Paso 1, 2 y 3: Recibir enunciado, inventariar archivos y clasificar."""
        self.challenge_description = description.strip()
        self.attached_files.clear()

        # Inventario de evidencias iniciales a partir de archivos
        file_observations = []
        if files:
            for f_path_str in files:
                p = Path(f_path_str.strip("\"'"))
                if p.exists():
                    self.attached_files.append(p)
                    # Ejecutar inspección de magic bytes
                    magic_res = self.registry.execute_tool("magic_inspector", file_path=str(p))
                    if magic_res.success:
                        self.evidence.add(
                            evidence_type=EvidenceType.OBSERVED_FACT,
                            description=f"Archivo '{p.name}': {magic_res.raw_text}",
                            source="magic_inspector",
                            data=magic_res.output,
                        )
                        file_observations.append(f"{p.name}: {magic_res.raw_text}")

        # Clasificación mediante la IA
        prompt = f"""Analiza el siguiente reto CTF y establece la estrategia inicial basada en evidencias:

ENUNCIADO DEL RETO:
{self.challenge_description}

ARCHIVOS ADJUNTOS:
{chr(10).join(file_observations) if file_observations else 'Ninguno'}

Responde estructuradamente:
1. Categoría principal (Web / Criptografía / Forense / Reversing / Pwn / Redes / Misc)
2. Nivel de dificultad estimado (Fácil / Intermedio / Difícil / Experto)
3. Primera hipótesis verificable
4. Primera tarea táctica recomendada (nombre de herramienta o comando)
"""
        try:
            ai_resp = self.router.ask(prompt=prompt, system_prompt=CTF_PRO_SYSTEM_PROMPT)
        except Exception as e:
            ai_resp = f"Análisis inicial en modo local: {str(e)}"

        # Extraer categoría de forma simple
        for cat in ["Web", "Criptografía", "Forense", "Reversing", "Pwn", "Redes", "Misc"]:
            if cat.lower() in ai_resp.lower():
                self.category = cat
                break

        # Registrar hipótesis inicial
        self.evidence.add(
            evidence_type=EvidenceType.HYPOTHESIS,
            description=f"Hipótesis inicial generada para categoría {self.category}: {ai_resp[:200]}...",
            source="clasificador_ia",
        )

        # Generar tareas iniciales en el planificador
        self._seed_initial_tasks()

        # Buscar si ya había una flag explícita en el texto
        flags_in_desc = FLAG_REGEX.findall(self.challenge_description)
        for f in flags_in_desc:
            self.evidence.add(
                evidence_type=EvidenceType.CANDIDATE_FLAG,
                description=f"Flag candidata en enunciado: {f}",
                source="enunciado",
            )

        return {
            "category": self.category,
            "ai_strategy": ai_resp,
            "evidence_count": len(self.evidence.items),
            "tasks_count": len(self.planner.tasks),
        }

    def _seed_initial_tasks(self) -> None:
        """Siembra tareas lógicas en el planificador según la categoría o archivos."""
        if self.attached_files:
            target_file = str(self.attached_files[0])
            self.planner.add_task(
                title=f"Extracción de strings en '{self.attached_files[0].name}'",
                description="Buscar banderas o cadenas ASCII/UTF-16 en el binario",
                tool_name="deep_strings",
                tool_args={"file_path": target_file},
                priority=9,
            )
            self.planner.add_task(
                title=f"Inspección de firmas / cabeceras en '{self.attached_files[0].name}'",
                description="Comprobar si es un ejecutable PE/ELF o archivo comprimido",
                tool_name="binary_headers",
                tool_args={"file_path": target_file},
                priority=7,
            )

        # Si el reto menciona codificación, cifrado o tokens
        if any(term in self.challenge_description.lower() for term in ["base64", "b64", "hex", "cifrado", "rot13", "caesar", "ciphertext", "cripto", "hash", "token"]):
            words = self.challenge_description.split()
            candidate_tokens = [w.strip("\"',") for w in words if len(w) > 8 and not w.startswith("http")]
            if candidate_tokens:
                self.planner.add_task(
                    title="Desanidado heurístico de codificación (MultiDecoder)",
                    description="Intentar decodificar token sospechoso",
                    tool_name="multi_decoder",
                    tool_args={"text": candidate_tokens[0]},
                    priority=8,
                )

    def step(self) -> Dict[str, Any]:
        """Alias para execute_next_step() para conveniencia."""
        return self.execute_next_step()

    def execute_next_step(self) -> Dict[str, Any]:
        """Paso 4 al 12: Ejecutar una iteración del ciclo de evidencias."""
        if self.verified_flag:
            return {
                "status": "COMPLETADO",
                "message": f"¡Reto resuelto! Flag validada: {self.verified_flag}",
                "verified_flag": self.verified_flag,
            }

        if self.planner.is_budget_exhausted():
            return {
                "status": "PRESUPUESTO_AGOTADO",
                "message": "Se ha alcanzado el límite de iteraciones o tiempo de ejecución.",
            }

        self.planner.current_iteration += 1
        current_task = self.planner.get_next_pending_task()

        if not current_task:
            # Si no quedan tareas pendientes, pedir a la IA que genere una nueva hipótesis
            return self._generate_new_task_from_evidence()

        current_task.status = TaskStatus.RUNNING
        sig = f"{current_task.tool_name}:{str(current_task.tool_args)}"
        if self.planner.record_attempt(sig):
            # Estrategia repetida detectada: saltar y replanificar
            current_task.status = TaskStatus.ABANDONED
            current_task.notes = "Estrategia idéntica ya ejecutada previamente."
            return {
                "status": "ESTRATEGIA_REPETIDA",
                "task": current_task.title,
                "message": "Se detectó intento repetido. Replanificando alternativa.",
            }

        # Ejecución de la herramienta
        tool_name = current_task.tool_name
        tool_res = None
        if tool_name and self.registry.get(tool_name):
            tool_res = self.registry.execute_tool(tool_name, **current_task.tool_args)

        if tool_res and tool_res.success:
            self.planner.mark_task_success(current_task.id, tool_res.raw_text[:200])

            # Registrar hecho observado
            self.evidence.add(
                evidence_type=EvidenceType.OBSERVED_FACT,
                description=f"Resultado de '{current_task.title}': {tool_res.raw_text[:300]}",
                source=tool_name or "tarea",
                data=tool_res.output,
                confidence=0.9,
            )

            # Buscar banderas en la salida de la herramienta
            flags = FLAG_REGEX.findall(tool_res.raw_text)
            for f in flags:
                cand = self.evidence.add(
                    evidence_type=EvidenceType.CANDIDATE_FLAG,
                    description=f"Bandera candidata detectada por '{tool_name}': {f}",
                    source=tool_name,
                    confidence=0.85,
                )
                # Validar la bandera contra el contexto
                self.verified_flag = f
                self.evidence.promote_to_verified(f, reason=f"Encontrada y confirmada por herramienta {tool_name}")

            return {
                "status": "PASO_EJECUTADO",
                "task": current_task.title,
                "output": tool_res.raw_text,
                "verified_flag": self.verified_flag,
            }
        else:
            err = tool_res.error if tool_res else "Sin herramienta directa"
            self.planner.mark_task_failed(current_task.id, err)
            # Replanificación automática ante fallo
            new_tasks = self.planner.replan_on_failure(current_task, err)
            return {
                "status": "FALLO_REPLANIFICADO",
                "task": current_task.title,
                "error": err,
                "new_tasks_added": len(new_tasks),
            }

    def _generate_new_task_from_evidence(self) -> Dict[str, Any]:
        """Consulta a la IA con el estado actual de evidencias para inferir el siguiente paso."""
        context = self.evidence.get_summary()
        prompt = f"""Hemos completado las tareas iniciales sin encontrar aún la flag validada.
ESTADO DE EVIDENCIAS:
{context}

RETO: {self.challenge_description}

Propón la siguiente tarea más prometedora. Especifica una acción táctica concreta."""

        try:
            advice = self.router.ask(prompt=prompt, system_prompt=CTF_PRO_SYSTEM_PROMPT)
            new_t = self.planner.add_task(
                title=f"Paso táctico IA #{self.planner.current_iteration}",
                description=advice[:200],
                priority=6,
            )
            return {
                "status": "NUEVA_TAREA_INFERIDA",
                "task": new_t.title,
                "ai_thought": advice,
            }
        except Exception as e:
            return {"status": "ERROR_INFERENCIA", "error": str(e)}

    def generate_final_report(self) -> str:
        """Paso 13: Genera un informe técnico reproducible."""
        lines = [
            f"# Informe de Resolución CTF: {self.challenge_id}",
            f"**Categoría:** {self.category} | **Estado:** {'RESUELTO' if self.verified_flag else 'EN PROGRESO'}",
            f"**Bandera Validada:** `{self.verified_flag or 'No confirmada aún'}`",
            "",
            "## 1. Resumen Ejecutivo y Evidencias Observadas",
            self.evidence.get_summary(),
            "",
            "## 2. Cronología de Hechos Confirmados",
        ]

        for item in self.evidence.items:
            lines.append(f"- **[{item.evidence_type.value}]** ({item.source}): {item.description}")

        lines.extend([
            "",
            "## 3. Registro de Tareas Ejecutadas",
            self.planner.get_progress_summary(),
        ])

        for t in self.planner.tasks:
            lines.append(f"- `[{t.status.value}]` {t.title}: {t.notes or t.result or 'Completada'}")

        return "\n".join(lines)
