"""
Módulo de Proveedores de IA para CTF-AI Solver
Soporte unificado y enrutador para Google Gemini, OpenAI y Anthropic Claude.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import time

from ctf_ai.config import Config, get_config


class AIProvider(ABC):
    """Clase base abstracta para proveedores de Inteligencia Artificial."""

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Envía una consulta al modelo de IA y retorna la respuesta como texto."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Retorna el nombre identificador del proveedor."""
        pass

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna la lista de modelos soportados y sus metadatos descriptivos."""
        return []


class GeminiProvider(AIProvider):
    """Proveedor para Google Gemini API usando el SDK oficial google-genai."""

    DEFAULT_FALLBACK_MODELS = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
    ]

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        super().__init__(api_key, default_model or "gemini-3.8-flash")
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except ImportError:
            self._client = None
        except Exception:
            self._client = None

    def get_name(self) -> str:
        return "gemini"

    def get_available_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "gemini-3.8-flash",
                "name": "Gemini 3.8 Flash",
                "description": "Recomendado | Rápido, alta cuota diaria y precisión en retos CTF",
                "recommended": True,
            },
            {
                "id": "gemini-3.7-flash",
                "name": "Gemini 3.7 Flash",
                "description": "Híbrido | Razonamiento avanzado, ideal para criptografía y reversing",
                "recommended": False,
            },
            {
                "id": "gemini-3.5-flash",
                "name": "Gemini 3.5 Flash",
                "description": "Estándar | Multimodal balanceado para análisis general de retos",
                "recommended": False,
            },
            {
                "id": "gemini-3.1-flash-lite",
                "name": "Gemini 3.1 Flash Lite",
                "description": "Ultra-rápido | Máxima velocidad de inferencia y mínimo consumo",
                "recommended": False,
            },
            {
                "id": "gemini-flash-latest",
                "name": "Gemini Flash Latest",
                "description": "Dinámico | Alias al último modelo de la familia Flash de Google",
                "recommended": False,
            },
        ]

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        if self._client is None:
            self._init_client()

        if self._client is None:
            raise RuntimeError(
                "La librería oficial 'google-genai' no está disponible o no se pudo inicializar. "
                "Por favor, instala la dependencia ejecutando: pip install google-genai"
            )

        requested_model = (model or self.default_model or "gemini-3.8-flash").strip()
        # Mapear modelos descontinuados al modelo actual recomendado
        if requested_model in (
            "gemini-2.0-flash",
            "gemini-2.5-flash",
            "gemini-1.5-flash",
            "gemini-2.5-pro",
            "models/gemini-2.0-flash",
            "models/gemini-2.5-flash",
            "models/gemini-1.5-flash",
        ):
            requested_model = "gemini-3.8-flash"

        full_prompt = ""
        if context:
            full_prompt += f"--- CONTEXTO DEL RETO CTF ---\n{context}\n\n"
        full_prompt += prompt

        models_to_try = [requested_model]
        for fb in self.DEFAULT_FALLBACK_MODELS:
            if fb not in models_to_try:
                models_to_try.append(fb)

        from google.genai import types
        from google.genai.errors import APIError

        gen_config = None
        if system_prompt:
            gen_config = types.GenerateContentConfig(system_instruction=system_prompt)

        last_error = None
        for current_model in models_to_try:
            try:
                kwargs = {
                    "model": current_model,
                    "contents": full_prompt,
                }
                if gen_config:
                    kwargs["config"] = gen_config

                response = self._client.models.generate_content(**kwargs)
                if response and response.text:
                    return response.text.strip()
                return "No se recibió texto en la respuesta de Gemini."
            except APIError as e:
                err_code = getattr(e, "code", None)
                err_msg = str(e)
                # Ante 404 (modelo descontinuado), 503 (alta demanda) o 429 (cuota de este modelo agotada),
                # intentar el siguiente modelo de fallback que tiene cuota separada
                if (
                    err_code in (404, 503, 429)
                    or "404" in err_msg
                    or "503" in err_msg
                    or "429" in err_msg
                    or "resource_exhausted" in err_msg.lower()
                    or "not found" in err_msg.lower()
                    or "is no longer available" in err_msg.lower()
                    or "unavailable" in err_msg.lower()
                ):
                    last_error = e
                    continue
                # Error de autenticación (401 / 403)
                elif err_code in (401, 403) or "401" in err_msg or "403" in err_msg or "api_key" in err_msg.lower():
                    raise RuntimeError(
                        "Error de autenticación en Gemini API (401/403): Clave de API inválida o sin permisos. "
                        "Verifica tu GEMINI_API_KEY en el archivo .env"
                    )
                else:
                    raise RuntimeError(f"Error en Gemini API ({err_code or 'desconocido'}): {err_msg}")
            except Exception as e:
                err_name = type(e).__name__
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    last_error = e
                    continue
                raise

        # Si se agotaron todos los modelos candidatos
        if last_error:
            if "429" in str(last_error) or "resource_exhausted" in str(last_error).lower():
                raise RuntimeError(
                    "Límite de cuota diario excedido en todos los modelos de Gemini. "
                    "Por favor espera a que se renueve la cuota o utiliza otro proveedor con 'provider <nombre>'."
                )
            if "connection" in str(last_error).lower() or "timeout" in str(last_error).lower():
                raise RuntimeError(
                    f"Error de conexión con Gemini: No se pudo contactar con los servidores de Google. "
                    "Verifica tu conexión a internet o proxy."
                )
            raise RuntimeError(f"No se pudo completar la consulta con ningún modelo de Gemini: {str(last_error)}")

        raise RuntimeError(
            f"El modelo '{requested_model}' y los modelos alternativos no están disponibles. "
            f"Modelos probados: {', '.join(models_to_try)}."
        )


class OpenAIProvider(AIProvider):
    """Proveedor para OpenAI (ChatGPT / GPT-4o)."""

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        super().__init__(api_key, default_model or "gpt-4o-mini")
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        except ImportError:
            self._client = None

    def get_name(self) -> str:
        return "openai"

    def get_available_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "description": "Recomendado | Flagship multimodal, alta inteligencia y código",
                "recommended": True,
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "description": "Económico | Rápido y eficiente para tareas cotidianas y scripts",
                "recommended": False,
            },
            {
                "id": "o3-mini",
                "name": "o3-mini",
                "description": "Razonamiento STEM | Especializado en lógica matemática y criptografía",
                "recommended": False,
            },
            {
                "id": "o1-preview",
                "name": "o1-preview",
                "description": "Razonamiento profundo | Planificación paso a paso para retos complejos",
                "recommended": False,
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Contexto amplio (128k) | Para inspeccionar volcados de memoria y logs extensos",
                "recommended": False,
            },
        ]

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        if self._client is None:
            raise RuntimeError(
                "La librería 'openai' no está instalada. Ejecuta: pip install openai"
            )

        model_name = model or self.default_model or "gpt-4o-mini"
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = ""
        if context:
            user_content += f"--- CONTEXTO DEL RETO CTF ---\n{context}\n\n"
        user_content += prompt

        messages.append({"role": "user", "content": user_content})

        try:
            response = self._client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise RuntimeError(f"Error en OpenAI API: {str(e)}")


class ClaudeProvider(AIProvider):
    """Proveedor para Anthropic Claude."""

    def __init__(self, api_key: str, default_model: Optional[str] = None):
        super().__init__(api_key, default_model or "claude-3-5-sonnet-20241022")
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            self._client = None

    def get_name(self) -> str:
        return "claude"

    def get_available_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "claude-3-5-sonnet-latest",
                "name": "Claude 3.5 Sonnet",
                "description": "Recomendado | El referente en reversing, binarios y exploits",
                "recommended": True,
            },
            {
                "id": "claude-3-5-haiku-latest",
                "name": "Claude 3.5 Haiku",
                "description": "Ultra-rápido | Respuestas instantáneas y análisis sintético",
                "recommended": False,
            },
            {
                "id": "claude-3-opus-latest",
                "name": "Claude 3 Opus",
                "description": "Profundo | Análisis contextual masivo para cadenas de explotación",
                "recommended": False,
            },
        ]

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        if self._client is None:
            raise RuntimeError(
                "La librería 'anthropic' no está instalada. Ejecuta: pip install anthropic"
            )

        model_name = model or self.default_model or "claude-3-5-sonnet-20241022"
        user_content = ""
        if context:
            user_content += f"--- CONTEXTO DEL RETO CTF ---\n{context}\n\n"
        user_content += prompt

        try:
            kwargs = {
                "model": model_name,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": user_content}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = self._client.messages.create(**kwargs)
            return response.content[0].text.strip()
        except Exception as e:
            raise RuntimeError(f"Error en Anthropic Claude API: {str(e)}")


class AIRouter:
    """Enrutador central para administrar y alternar proveedores de IA."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.providers: Dict[str, AIProvider] = {}
        self.active_provider_name: str = self.config.default_provider
        self.active_model: Optional[str] = self.config.default_model
        self._init_providers()

    def _init_providers(self) -> None:
        """Inicializa los proveedores disponibles basándose en las API keys configuradas."""
        self.providers.clear()

        if self.config.gemini_api_key:
            self.providers["gemini"] = GeminiProvider(
                api_key=self.config.gemini_api_key,
                default_model=self.config.default_model if self.active_provider_name == "gemini" else None,
            )

        if self.config.openai_api_key:
            self.providers["openai"] = OpenAIProvider(
                api_key=self.config.openai_api_key,
                default_model=self.config.default_model if self.active_provider_name == "openai" else None,
            )

        if self.config.anthropic_api_key:
            self.providers["claude"] = ClaudeProvider(
                api_key=self.config.anthropic_api_key,
                default_model=self.config.default_model if self.active_provider_name == "claude" else None,
            )

        # Si el proveedor por defecto no tiene key configurada, seleccionar el primer disponible
        if self.active_provider_name not in self.providers and self.providers:
            self.active_provider_name = next(iter(self.providers.keys()))

    def reload(self) -> None:
        """Recarga la configuración y reinicializa los proveedores."""
        self.config = get_config(reload=True)
        self._init_providers()

    def get_available_providers(self) -> List[str]:
        """Retorna la lista de proveedores inicializados y listos para usar."""
        return list(self.providers.keys())

    def get_current_provider_name(self) -> str:
        """Retorna el nombre del proveedor actualmente activo."""
        return self.active_provider_name

    def set_provider(self, name: str) -> bool:
        """Cambia el proveedor activo."""
        name = name.lower()
        if name in ("chatgpt", "gpt"):
            name = "openai"
        elif name in ("anthropic",):
            name = "claude"

        if name not in self.providers:
            return False

        self.active_provider_name = name
        return True

    def set_model(self, model_name: Optional[str]) -> None:
        """Configura el modelo a utilizar para las peticiones."""
        self.active_model = model_name.strip() if model_name else None
        if self.active_provider_name in self.providers and self.active_model:
            self.providers[self.active_provider_name].default_model = self.active_model

    def get_available_models(self, provider_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retorna la lista de modelos soportados para el proveedor especificado o activo."""
        p_name = (provider_name or self.active_provider_name).lower()
        if p_name in ("chatgpt", "gpt"):
            p_name = "openai"
        elif p_name in ("anthropic",):
            p_name = "claude"

        if p_name in self.providers:
            return self.providers[p_name].get_available_models()

        # Si el proveedor no tiene API key configurada, retornar el catálogo estático
        if p_name == "gemini":
            return GeminiProvider("", "").get_available_models()
        elif p_name == "openai":
            return OpenAIProvider("", "").get_available_models()
        elif p_name == "claude":
            return ClaudeProvider("", "").get_available_models()
        return []

    def get_active_model_name(self) -> str:
        """Retorna el identificador del modelo actualmente seleccionado."""
        if self.active_model:
            return self.active_model
        if self.active_provider_name in self.providers and self.providers[self.active_provider_name].default_model:
            return self.providers[self.active_provider_name].default_model
        defaults = {
            "gemini": "gemini-3.8-flash",
            "openai": "gpt-4o-mini",
            "claude": "claude-3-5-sonnet-latest",
        }
        return defaults.get(self.active_provider_name, "predeterminado")

    def set_model_by_index(self, index: int) -> Optional[str]:
        """Selecciona un modelo por su índice (1..N) en la lista disponible."""
        models = self.get_available_models()
        if 1 <= index <= len(models):
            chosen = models[index - 1]["id"]
            self.set_model(chosen)
            return chosen
        return None

    def ask(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        provider_name: Optional[str] = None,
    ) -> str:
        """Envía la solicitud al proveedor especificado o al activo."""
        p_name = provider_name.lower() if provider_name else self.active_provider_name

        if p_name in ("chatgpt", "gpt"):
            p_name = "openai"
        elif p_name in ("anthropic",):
            p_name = "claude"

        if not self.providers:
            raise RuntimeError(
                "No hay ningún proveedor de IA configurado. Por favor, añade tu clave API "
                "(GEMINI_API_KEY, OPENAI_API_KEY o ANTHROPIC_API_KEY) en el archivo .env"
            )

        if p_name not in self.providers:
            available = ", ".join(self.providers.keys())
            raise ValueError(
                f"El proveedor '{p_name}' no está configurado. Disponibles: {available}"
            )

        provider = self.providers[p_name]
        return provider.ask(
            prompt=prompt,
            system_prompt=system_prompt,
            context=context,
            model=self.active_model,
        )
