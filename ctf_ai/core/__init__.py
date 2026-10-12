"""
Módulo Core de CTF-AI Solver Pro
Contiene el motor autónomo de resolución, inventario de evidencias, planificador operacional y sandbox.
"""

from ctf_ai.core.evidence import EvidenceItem, EvidenceType, EvidenceInventory
from ctf_ai.core.planner import Task, TaskStatus, OperationalPlanner
from ctf_ai.core.sandbox import SandboxBase, LocalWorkspaceSandbox, DockerSandbox, get_active_sandbox
from ctf_ai.core.engine import AutonomousCTFEngine

__all__ = [
    "EvidenceItem",
    "EvidenceType",
    "EvidenceInventory",
    "Task",
    "TaskStatus",
    "OperationalPlanner",
    "SandboxBase",
    "LocalWorkspaceSandbox",
    "DockerSandbox",
    "get_active_sandbox",
    "AutonomousCTFEngine",
]
