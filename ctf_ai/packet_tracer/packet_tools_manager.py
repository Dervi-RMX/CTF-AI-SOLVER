"""
Gestor de la plataforma Packet Tools AI (ph0Void/packet-tools).
Administra el ciclo de vida del ecosistema de redes: detección del ejecutable oficial,
descarga del instalador de Windows, arranque del backend/frontend web, monitoreo de puertos
y apertura automática del navegador en http://localhost:3000.
"""

import os
import shutil
import socket
import subprocess
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


PACKET_TOOLS_SETUP_URL = "https://github.com/ph0Void/packet-tools/releases/download/v1.2.4/Packet.Tools.Setup.1.2.4.exe"
PACKET_TOOLS_WEB_URL = "http://localhost:3000"
DEFAULT_USER = "admin"
DEFAULT_PASS = "admin123"

CANDIDATE_PATHS = [
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Packet Tools\Packet Tools.exe")),
    Path(r"C:\Program Files\Packet Tools\Packet Tools.exe"),
    Path(r"C:\Program Files (x86)\Packet Tools\Packet Tools.exe"),
    Path(os.path.expanduser(r"~\AppData\Local\Programs\Packet Tools\Packet Tools.exe")),
]


class PacketToolsManager:
    """Gestiona el servicio y la interfaz web de Packet Tools AI."""

    def __init__(self):
        self._cached_exe: Optional[Path] = None

    def find_executable(self) -> Optional[Path]:
        """Busca el ejecutable instalado de Packet Tools en el sistema."""
        if self._cached_exe and self._cached_exe.exists():
            return self._cached_exe

        for p in CANDIDATE_PATHS:
            if p.exists():
                self._cached_exe = p
                return p

        # Buscar en el PATH de Windows
        which_exe = shutil.which("Packet Tools.exe") or shutil.which("packet-tools")
        if which_exe:
            p = Path(which_exe)
            self._cached_exe = p
            return p

        return None

    def is_installed(self) -> bool:
        """Comprueba si Packet Tools está instalado en la máquina."""
        return self.find_executable() is not None

    def is_port_open(self, host: str, port: int, timeout: float = 0.5) -> bool:
        """Comprueba si un puerto TCP local está escuchando activamente."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    def is_web_online(self, timeout: float = 1.0) -> bool:
        """Verifica si el servidor web (Next.js en el puerto 3000) responde."""
        return self.is_port_open("127.0.0.1", 3000, timeout=timeout)

    def is_api_online(self, timeout: float = 1.0) -> bool:
        """Verifica el backend de Packet Tools; no clasifica 7531 como API oficial de PT."""
        return (
            self.is_port_open("127.0.0.1", 3001, timeout=timeout)
        )

    def is_packet_tracer_ipc_online(self, timeout: float = 1.0) -> bool:
        """Comprueba el listener PTMP/IPC oficial documentado por Cisco (39000 por defecto)."""
        return self.is_port_open("127.0.0.1", 39000, timeout=timeout)

    def start_service(self) -> Tuple[bool, str]:
        """Inicia Packet Tools. Si ya está corriendo, retorna éxito de inmediato."""
        if self.is_web_online():
            return True, "El servicio de Packet Tools ya se encuentra activo en http://localhost:3000"

        exe = self.find_executable()
        if not exe:
            return False, "Packet Tools no está instalado en este equipo."

        try:
            # Iniciar el proceso de forma desacoplada
            subprocess.Popen([str(exe)], shell=False)

            # Esperar hasta 15 segundos a que el puerto web abra
            for _ in range(30):
                time.sleep(0.5)
                if self.is_web_online():
                    return True, "Servicio de Packet Tools iniciado con éxito en http://localhost:3000"

            return True, "Packet Tools se está iniciando. Abriendo navegador..."
        except Exception as e:
            return False, f"Error al iniciar Packet Tools: {e}"

    def stop_service(self) -> Tuple[bool, str]:
        """Detiene los procesos en ejecución de Packet Tools."""
        killed = False
        for proc_name in ["Packet Tools.exe", "PacketTools.exe"]:
            try:
                cmd = f'taskkill /F /IM "{proc_name}"'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0:
                    killed = True
            except Exception:
                pass

        if killed or not self.is_web_online():
            return True, "Servicios de Packet Tools detenidos correctamente."
        return False, "No se detectaron procesos activos de Packet Tools para detener."

    def open_web_browser(self, url: str = PACKET_TOOLS_WEB_URL) -> bool:
        """Abre el navegador web predeterminado en la URL del Dashboard."""
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    def download_and_install_setup(
        self, progress_cb: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """Descarga el instalador oficial de Windows (v1.2.4) y lo ejecuta."""
        target_dir = Path(os.path.expanduser(r"~\Downloads"))
        target_dir.mkdir(parents=True, exist_ok=True)
        setup_exe = target_dir / "Packet.Tools.Setup.1.2.4.exe"

        try:
            if not setup_exe.exists():
                if progress_cb:
                    progress_cb("Descargando Packet Tools Setup v1.2.4 desde GitHub (335 MB)...")

                req = urllib.request.Request(
                    PACKET_TOOLS_SETUP_URL,
                    headers={"User-Agent": "CTF-AI-Solver-Pro/2.0"},
                )
                with urllib.request.urlopen(req, timeout=60) as resp, open(setup_exe, "wb") as f:
                    shutil.copyfileobj(resp, f)

                if progress_cb:
                    progress_cb(f"Descarga completada en: {setup_exe}")
            else:
                if progress_cb:
                    progress_cb(f"Instalador existente detectado en: {setup_exe}")

            if progress_cb:
                progress_cb("Lanzando asistente de instalación de Packet Tools...")

            # Iniciar el instalador de forma interactiva
            os.startfile(str(setup_exe))
            return True, f"Instalador lanzado con éxito desde {setup_exe}. Completa la instalación y luego ejecuta 'pt'."
        except Exception as e:
            return False, f"Error al descargar o ejecutar el instalador: {e}"

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el diagnóstico completo del estado de Packet Tools."""
        exe = self.find_executable()
        web_ok = self.is_web_online()
        api_ok = self.is_api_online()

        return {
            "installed": exe is not None,
            "executable_path": str(exe) if exe else None,
            "web_online": web_ok,
            "api_online": api_ok,
            "web_url": PACKET_TOOLS_WEB_URL,
            "default_user": DEFAULT_USER,
            "default_pass": DEFAULT_PASS,
        }
