"""
Módulo de Configuración para CTF-AI Solver
Gestiona variables de entorno, claves de API y opciones por defecto.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv


class Config:
    """Clase principal de configuración."""

    def __init__(self, env_path: Optional[Path] = None):
        # Buscar archivo .env en directorio actual o en la raíz del proyecto
        if env_path is None:
            # Buscar en el directorio actual o en la carpeta superior
            base_dir = Path(__file__).resolve().parent.parent
            env_file = base_dir / ".env"
            if not env_file.exists():
                env_file = Path.cwd() / ".env"
            self.env_path = env_file
        else:
            self.env_path = Path(env_path)

        if self.env_path.exists():
            load_dotenv(dotenv_path=self.env_path, override=True)
        else:
            load_dotenv(override=True)

        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "").strip() or None
        self.anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY", "").strip() or None
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", "").strip() or None

        self.default_provider: str = os.getenv("DEFAULT_PROVIDER", "gemini").strip().lower()
        self.default_model: Optional[str] = os.getenv("DEFAULT_MODEL", "").strip() or None

    def get_available_providers(self) -> List[str]:
        """Retorna una lista con los proveedores que tienen una API key configurada."""
        providers = []
        if self.gemini_api_key:
            providers.append("gemini")
        if self.openai_api_key:
            providers.append("openai")
        if self.anthropic_api_key:
            providers.append("claude")
        return providers

    def is_provider_configured(self, provider: str) -> bool:
        """Verifica si un proveedor específico tiene su API key configurada."""
        provider = provider.lower()
        if provider == "gemini":
            return bool(self.gemini_api_key)
        elif provider in ("openai", "chatgpt"):
            return bool(self.openai_api_key)
        elif provider in ("claude", "anthropic"):
            return bool(self.anthropic_api_key)
        return False

    def get_api_key(self, provider: str) -> Optional[str]:
        """Obtiene la clave de API para un proveedor específico."""
        provider = provider.lower()
        if provider == "gemini":
            return self.gemini_api_key
        elif provider in ("openai", "chatgpt"):
            return self.openai_api_key
        elif provider in ("claude", "anthropic"):
            return self.anthropic_api_key
        return None

    def set_api_key(self, provider: str, key: str) -> None:
        """Actualiza la clave en memoria y la persiste en el archivo .env."""
        provider = provider.lower()
        env_var_name = ""
        if provider == "gemini":
            self.gemini_api_key = key
            env_var_name = "GEMINI_API_KEY"
        elif provider in ("openai", "chatgpt"):
            self.openai_api_key = key
            env_var_name = "OPENAI_API_KEY"
        elif provider in ("claude", "anthropic"):
            self.anthropic_api_key = key
            env_var_name = "ANTHROPIC_API_KEY"

        if env_var_name:
            os.environ[env_var_name] = key
            self._update_env_file(env_var_name, key)

    def _update_env_file(self, key_name: str, key_val: str) -> None:
        """Actualiza o añade una clave al archivo .env."""
        lines = []
        found = False
        if self.env_path.exists():
            with open(self.env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key_name}="):
                new_lines.append(f"{key_name}={key_val}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key_name}={key_val}\n")

        with open(self.env_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    def __repr__(self) -> str:
        return (
            f"Config(default_provider={self.default_provider!r}, "
            f"default_model={self.default_model!r}, "
            f"available_providers={self.get_available_providers()!r})"
        )


# Instancia global reutilizable
_config_instance: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Obtiene la instancia singleton de configuración."""
    global _config_instance
    if _config_instance is None or reload:
        _config_instance = Config()
    return _config_instance
