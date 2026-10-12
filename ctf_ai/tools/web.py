"""
Herramientas de Análisis Web Estructuradas para CTF-AI Solver Pro
Inspecciona cabeceras de seguridad, atributos de cookies, escaneo estático de código HTML/JS
en busca de endpoints y tokens expuestos, y control estricto de alcance (Scope Enforcer).
"""

from pathlib import Path
import re
import shutil
import urllib.parse
from typing import Any, Dict, List, Optional

from ctf_ai.tools.base import BaseTool, ToolResult, registry


SECRET_PATTERNS = [
    (r"(?:api[_-]?key|apikey|access_token|secret_key)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{16,})['\"]", "API Key / Secret Token"),
    (r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*", "JSON Web Token (JWT)"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
]

ENDPOINT_PATTERN = re.compile(r"['\"](\/(?:api|v[0-9]|admin|auth|user|login|flag|secret|dashboard)[a-zA-Z0-9_\-\/]*)['\"]", re.IGNORECASE)


class ScopeEnforcer:
    """Controlador que garantiza que sólo se interactúe con objetivos autorizados."""

    def __init__(self):
        # Por defecto siempre autorizados entornos locales y rangos típicos de laboratorios/CTF
        self.allowed_hosts = {"localhost", "127.0.0.1", "0.0.0.0"}

    def add_allowed_target(self, target: str) -> None:
        cleaned = target.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
        if cleaned:
            self.allowed_hosts.add(cleaned.lower())

    def is_in_scope(self, url_or_host: str) -> bool:
        host = url_or_host.strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].lower()
        if host in self.allowed_hosts:
            return True
        # Permitir redes locales RFC 1918 comúnmente usadas en CTF (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
        if host.startswith("10.") or host.startswith("192.168.") or host.startswith("172."):
            return True
        return False


global_scope_enforcer = ScopeEnforcer()


class WebSecurityHeadersTool(BaseTool):
    """Inspecciona cabeceras HTTP de respuesta y atributos de seguridad de cookies en URLs autorizadas."""

    name = "web_headers"
    description = "Analiza cabeceras HTTP de seguridad (CSP, HSTS, X-Frame) y cookies en objetivos autorizados"
    category = "web"
    arguments_schema = {
        "url": {"type": "str", "required": True, "help": "URL del reto"},
    }

    def execute(self, url: str) -> ToolResult:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        parsed = urllib.parse.urlparse(url)
        if not global_scope_enforcer.is_in_scope(parsed.hostname or ""):
            return ToolResult(
                success=False,
                error=f"Objetivo '{parsed.hostname}' fuera de alcance. Añádelo a la lista de objetivos autorizados.",
            )

        try:
            import requests
            resp = requests.get(url, timeout=10, headers={"User-Agent": "CTF-AI-Solver/2.0-Defensive"})

            headers = dict(resp.headers)
            security_headers_check = {
                "Strict-Transport-Security (HSTS)": "strict-transport-security" in headers,
                "Content-Security-Policy (CSP)": "content-security-policy" in headers,
                "X-Frame-Options (Clickjacking)": "x-frame-options" in headers,
                "X-Content-Type-Options": "x-content-type-options" in headers,
                "Referrer-Policy": "referrer-policy" in headers,
            }

            cookies_audit = []
            for c in resp.cookies:
                cookies_audit.append({
                    "name": c.name,
                    "httponly": c.has_nonstandard_attr("HttpOnly") or getattr(c, "httponly", False),
                    "secure": c.secure,
                })

            res = {
                "status_code": resp.status_code,
                "server": headers.get("Server", "Oculto/No especificado"),
                "security_headers": security_headers_check,
                "cookies_found": cookies_audit,
            }
            return ToolResult(
                success=True,
                output=res,
                raw_text=f"Status: {resp.status_code} | Server: {res['server']} | Headers evaluados: {security_headers_check}",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class WebStaticSecretScannerTool(BaseTool):
    """Escanea código fuente HTML, JS o texto buscando endpoints y credenciales/tokens expuestos."""

    name = "web_scan_secrets"
    description = "Busca secretos, API keys y endpoints ocultos en código fuente HTML/JS o respuestas"
    category = "web"
    arguments_schema = {
        "content_or_file": {"type": "str", "required": True, "help": "Texto a escanear o ruta de archivo local"},
    }

    def execute(self, content_or_file: str) -> ToolResult:
        p = Path(content_or_file.strip("\"'"))
        if p.exists() and p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
        else:
            text = content_or_file

        secrets_found = []
        for pat, desc in SECRET_PATTERNS:
            for match in re.finditer(pat, text):
                val = match.group(0)
                # Enmascarar ligeramente para no volcar claves enteras en logs
                masked = val[:8] + "..." + val[-4:] if len(val) > 16 else val
                secrets_found.append({"type": desc, "sample": masked})

        # Endpoints
        endpoints = list(set(ENDPOINT_PATTERN.findall(text)))

        # Comentarios HTML y JS
        comments = []
        html_comments = re.findall(r"<!--(.*?)-->", text, re.DOTALL)
        for c in html_comments[:10]:
            clean_c = c.strip()
            if clean_c:
                comments.append(clean_c)

        res = {
            "secrets_detected": secrets_found,
            "endpoints_found": endpoints[:30],
            "comments_sample": comments,
        }
        return ToolResult(
            success=True,
            output=res,
            raw_text=f"Secretos: {len(secrets_found)} | Endpoints descubiertos: {len(endpoints)} | Comentarios: {len(comments)}",
        )


class WebToolsDetectorTool(BaseTool):
    """Detecta la disponibilidad de herramientas de auditoría web en el sistema local."""

    name = "web_env"
    description = "Detecta utilidades web disponibles en PATH (curl, nmap, ffuf, gobuster, nikto)"
    category = "web"
    arguments_schema = {}

    def execute(self) -> ToolResult:
        tools = ["curl", "nmap", "ffuf", "gobuster", "nikto", "sqlmap"]
        detected = {t: shutil.which(t) is not None for t in tools}
        return ToolResult(
            success=True,
            output=detected,
            raw_text=f"Herramientas web detectadas: {[t for t, ok in detected.items() if ok]}",
        )


# Registrar herramientas web
registry.register(WebSecurityHeadersTool)
registry.register(WebStaticSecretScannerTool)
registry.register(WebToolsDetectorTool)
