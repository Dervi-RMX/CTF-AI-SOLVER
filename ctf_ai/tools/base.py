"""
Módulo Base de la Arquitectura de Herramientas Estructuradas para CTF-AI Solver Pro
Define contratos uniformes, validación de argumentos, esquemas, límites de ejecución y registro centralizado.
"""

from abc import ABC, abstractmethod
import time
from typing import Any, Callable, Dict, List, Optional, Tuple


class ToolResult:
    """Resultado estandarizado de la invocación de una herramienta."""

    def __init__(
        self,
        success: bool,
        output: Any = None,
        raw_text: str = "",
        artifacts: Optional[List[str]] = None,
        error: Optional[str] = None,
        execution_time_ms: float = 0.0,
    ):
        self.success = success
        self.output = output
        self.raw_text = raw_text or (str(output) if output is not None else "")
        self.artifacts = artifacts or []
        self.error = error
        self.execution_time_ms = execution_time_ms

    @property
    def data(self) -> Any:
        return self.output

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "raw_text": self.raw_text,
            "artifacts": self.artifacts,
            "error": self.error,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }

    def __repr__(self) -> str:
        status = "OK" if self.success else f"ERROR: {self.error}"
        return f"ToolResult({status}, time={self.execution_time_ms:.1f}ms)"


class BaseTool(ABC):
    """Clase base que todas las herramientas profesionales de CTF deben implementar."""

    name: str = "base_tool"
    description: str = "Herramienta base abstracta"
    category: str = "misc"  # crypto, forensics, reversing, web, network, misc
    arguments_schema: Dict[str, Dict[str, Any]] = {}
    required_binaries: List[str] = []

    def is_available(self) -> bool:
        """Comprueba si las dependencias o ejecutables requeridos están presentes en el sistema."""
        import shutil
        return all(shutil.which(b) is not None for b in self.required_binaries)

    def validate_args(self, kwargs: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Valida los argumentos proporcionados contra el esquema definido."""
        for arg_name, arg_meta in self.arguments_schema.items():
            if arg_meta.get("required", False) and arg_name not in kwargs:
                return False, f"Falta argumento requerido: '{arg_name}'"
        return True, None

    def run(self, **kwargs) -> ToolResult:
        """Punto de entrada seguro que mide tiempo de ejecución y captura excepciones."""
        valid, err_msg = self.validate_args(kwargs)
        if not valid:
            return ToolResult(success=False, error=err_msg)

        if not self.is_available():
            missing = ", ".join(self.required_binaries)
            return ToolResult(
                success=False,
                error=f"Herramienta no disponible. Requiere binario(s) no encontrados en PATH: {missing}",
            )

        start_time = time.perf_counter()
        try:
            res = self.execute(**kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            res.execution_time_ms = elapsed_ms
            return res
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolResult(
                success=False,
                error=f"Excepción en '{self.name}': {str(e)}",
                execution_time_ms=elapsed_ms,
            )

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Lógica interna de ejecución que cada herramienta especializada implementa."""
        pass


class ToolRegistry:
    """Registro global y fábrica de herramientas estructuradas."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_class: Any) -> None:
        """Instancia y registra una herramienta."""
        tool = tool_class() if isinstance(tool_class, type) else tool_class
        self._tools[tool.name.lower()] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name.lower())

    def get_by_category(self, category: str) -> List[BaseTool]:
        cat_lower = category.lower()
        return [t for t in self._tools.values() if t.category.lower() == cat_lower]

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "schema": t.arguments_schema,
                "available": t.is_available(),
            }
            for t in self._tools.values()
        ]

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(success=False, error=f"Herramienta '{name}' no encontrada en el registro.")
        return tool.run(**kwargs)


# Registro singleton global
registry = ToolRegistry()
