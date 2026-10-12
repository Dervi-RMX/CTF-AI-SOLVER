"""
Controlador de escritorio para Cisco Packet Tracer en Windows.
Detección de ejecutables, apertura de la aplicación y enfoque visual de la ventana.
"""

import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


COMMON_PT_INSTALL_PATHS = [
    Path(r"C:\Program Files\Cisco Packet Tracer 9.0.0\bin\PacketTracer.exe"),
    Path(r"C:\Program Files\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe"),
    Path(r"C:\Program Files\Cisco Packet Tracer 8.2.0\bin\PacketTracer.exe"),
    Path(r"C:\Program Files\Cisco Packet Tracer 8.0.0\bin\PacketTracer.exe"),
    Path(r"C:\Program Files (x86)\Cisco Packet Tracer 8.2.2\bin\PacketTracer.exe"),
    Path(r"C:\Program Files (x86)\Cisco Packet Tracer 8.2.0\bin\PacketTracer.exe"),
    Path(r"C:\Program Files (x86)\Cisco Packet Tracer 7.3.1\bin\PacketTracer.exe"),
]


class PacketTracerDesktop:
    """Gestiona el ciclo de vida y foco de la aplicación Cisco Packet Tracer en Windows."""

    def __init__(self, custom_path: Optional[str] = None):
        self.custom_path = Path(custom_path) if custom_path else None
        self._cached_exe_path: Optional[Path] = None

    def find_packet_tracer_exe(self) -> Optional[Path]:
        """Localiza el ejecutable de PacketTracer.exe en el sistema."""
        if self._cached_exe_path and self._cached_exe_path.exists():
            return self._cached_exe_path

        if self.custom_path and self.custom_path.exists():
            self._cached_exe_path = self.custom_path
            return self._cached_exe_path

        # 1. Comprobar rutas habituales
        for p in COMMON_PT_INSTALL_PATHS:
            if p.exists():
                self._cached_exe_path = p
                return p

        # 2. Comprobar en PATH
        which_path = shutil.which("PacketTracer.exe") or shutil.which("PacketTracer")
        if which_path:
            p = Path(which_path)
            if p.exists():
                self._cached_exe_path = p
                return p

        # 3. Comprobar rutas en AppData / Program Files genérico
        prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        pt_dir = Path(prog_files)
        for sub in pt_dir.glob("Cisco Packet Tracer*"):
            exe = sub / "bin" / "PacketTracer.exe"
            if exe.exists():
                self._cached_exe_path = exe
                return exe

        return None

    def is_running(self) -> bool:
        """Comprueba si el proceso PacketTracer.exe está activo en Windows."""
        try:
            cmd = 'tasklist /FI "IMAGENAME eq PacketTracer.exe" /NH'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            return "PacketTracer.exe" in res.stdout
        except Exception:
            return False

    def launch(self, file_path: Optional[str] = None, wait_seconds: float = 3.0) -> Tuple[bool, str]:
        """
        Inicia Cisco Packet Tracer si no está abierto. Opcionalmente abre un archivo .pkt específico.
        """
        exe = self.find_packet_tracer_exe()
        if not exe:
            return False, "No se encontró el ejecutable de Cisco Packet Tracer en las rutas estándar."

        already_running = self.is_running()
        cmd_args = [str(exe)]
        if file_path and Path(file_path).exists():
            cmd_args.append(str(Path(file_path).resolve()))

        try:
            if not already_running:
                subprocess.Popen(cmd_args, shell=False)
                # Esperar a que la ventana y los servicios internos de PT inicien
                time.sleep(wait_seconds)
            else:
                # Si ya está abierto y se especificó un archivo
                if file_path and Path(file_path).exists():
                    subprocess.Popen(cmd_args, shell=False)
                    time.sleep(1.5)

            # Intentar traer al frente
            self.bring_to_foreground()
            return True, f"Cisco Packet Tracer activo ({exe.name})"
        except Exception as e:
            return False, f"Error al ejecutar Cisco Packet Tracer: {e}"

    def bring_to_foreground(self) -> bool:
        """
        Enfoca la ventana principal de Cisco Packet Tracer en primer plano usando Windows API.
        """
        if sys.platform != "win32":
            return False

        try:
            user32 = ctypes.windll.user32
            found_hwnds = []

            # Callback para enumerar ventanas
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

            def enum_windows_callback(hwnd, extra):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value
                        if "packet tracer" in title.lower():
                            found_hwnds.append(hwnd)
                return True

            cb = WNDENUMPROC(enum_windows_callback)
            user32.EnumWindows(cb, 0)

            if found_hwnds:
                main_hwnd = found_hwnds[0]
                SW_RESTORE = 9
                user32.ShowWindow(main_hwnd, SW_RESTORE)
                user32.SetForegroundWindow(main_hwnd)
                return True
            return False
        except Exception:
            return False

    def trigger_extensions_menu(self) -> bool:
        """
        Envía la secuencia de teclado Alt+X y Enter para abrir el menú Extensions en Packet Tracer.
        """
        if sys.platform != "win32":
            return False
        try:
            self.bring_to_foreground()
            time.sleep(0.3)
            user32 = ctypes.windll.user32
            VK_MENU = 0x12  # Alt
            VK_X = 0x58     # X
            VK_DOWN = 0x28  # Flecha abajo
            VK_RETURN = 0x0D # Enter
            KEYEVENTF_KEYUP = 0x0002

            # Alt + X
            user32.keybd_event(VK_MENU, 0, 0, 0)
            user32.keybd_event(VK_X, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_X, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)

            # Enter para seleccionar la primera opción ("Packet Tracer API")
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            return True
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el diagnóstico del ejecutable y proceso de Packet Tracer."""
        exe = self.find_packet_tracer_exe()
        running = self.is_running()
        return {
            "installed": exe is not None,
            "executable_path": str(exe) if exe else None,
            "is_running": running,
            "version_hint": exe.parent.parent.name if exe else None,
        }
