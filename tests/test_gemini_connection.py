"""
Script de prueba y validación para CTF-AI Solver
Prueba herramientas locales, configuración segura y conexión real a Gemini API.
"""

import sys
from pathlib import Path

# Configurar codificación UTF-8 en terminal de Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Añadir raíz del proyecto al path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ctf_ai.config import get_config
from ctf_ai.ai_providers import AIRouter
import ctf_ai.tools as ctf_tools


def test_offline_tools():
    print("[TEST 1/4] Verificando herramientas locales de CTF...")
    # Base64
    b64_res = ctf_tools.decode_base64("ZmxhZ3t0ZXN0X2ZsYWd9")
    assert b64_res == "flag{test_flag}", f"Error en base64: {b64_res}"
    
    # ROT13
    rot_res = ctf_tools.rot13("synt{grfg}")
    assert rot_res == "flag{test}", f"Error en rot13: {rot_res}"
    
    # Hash ID
    hash_res = ctf_tools.identify_hash("5d41402abc4b2a76b9719d911017c592")
    assert "MD5" in hash_res, f"Error en hashid: {hash_res}"
    
    # Flag search
    flags = ctf_tools.find_flags("Contenido encontrado con flag{secret_123} dentro.")
    assert "flag{secret_123}" in flags, f"Error en flag detection: {flags}"
    
    print("  [OK] Todas las herramientas locales funcionan correctamente.")


def test_config_security():
    print("[TEST 2/4] Verificando seguridad de configuración y claves...")
    config = get_config(reload=True)
    repr_str = repr(config)
    
    # Verificar que las claves reales NO aparezcan en repr o logs
    if config.gemini_api_key:
        assert config.gemini_api_key not in repr_str, "ALERTA: La API key de Gemini está expuesta en repr(config)"
    if config.openai_api_key:
        assert config.openai_api_key not in repr_str, "ALERTA: La API key de OpenAI está expuesta en repr(config)"
    if config.anthropic_api_key:
        assert config.anthropic_api_key not in repr_str, "ALERTA: La API key de Claude está expuesta en repr(config)"
        
    print(f"  [OK] Configuración segura. Proveedores disponibles: {config.get_available_providers()}")


def test_ai_router_initialization():
    print("[TEST 3/4] Verificando inicialización de AIRouter...")
    config = get_config()
    router = AIRouter(config)
    avail = router.get_available_providers()
    assert "gemini" in avail, "Gemini debería estar en proveedores disponibles basándose en .env"
    print("  [OK] AIRouter listo. Proveedor activo:", router.get_current_provider_name())


def test_live_gemini_query():
    print("[TEST 4/4] Ejecutando consulta real a Google Gemini...")
    config = get_config()
    if not config.gemini_api_key:
        print("  [ERROR] Omitido: No se detectó GEMINI_API_KEY en .env")
        return False
        
    router = AIRouter(config)
    router.set_provider("gemini")
    
    test_prompt = "Responde en español en un solo párrafo corto: ¿Qué es un reto CTF de ciberseguridad?"
    try:
        response = router.ask(
            prompt=test_prompt,
            system_prompt="Eres un experto en CTFs y ciberseguridad.",
        )
        print("  [OK] Respuesta recibida exitosamente de Gemini:")
        print("  ------------------------------------------------------------")
        print(f"  {response.encode('ascii', errors='replace').decode('ascii')}")
        print("  ------------------------------------------------------------")
        assert len(response) > 20, "La respuesta fue demasiado corta o vacía"
        return True
    except Exception as e:
        print(f"  [ERROR] Fallo en consulta a Gemini: {type(e).__name__}: {str(e)}")
        return False


def main():
    print("=" * 60)
    print("  INICIANDO SUITE DE PRUEBAS DE CTF-AI SOLVER")
    print("=" * 60)
    
    test_offline_tools()
    test_config_security()
    test_ai_router_initialization()
    success = test_live_gemini_query()
    
    print("=" * 60)
    if success:
        print("  [OK] TODAS LAS PRUEBAS PASARON EXITOSAMENTE.")
    else:
        print("  [ERROR] ALGUNAS PRUEBAS FALLARON.")
    print("=" * 60)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
