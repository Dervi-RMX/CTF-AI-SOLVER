"""
Instalador y verificador de la extensión nativa de Cisco Packet Tracer.
Permite instalar con un click el plugin Socket.IO (Plugin-PacketToolsAPI) en los
directorios de extensiones de Cisco Packet Tracer (v9.0 y v8.2).
"""

import os
import shutil
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PLUGIN_PTS_URL = "https://raw.githubusercontent.com/ph0Void/packet-tools/main/extension-packetracer/Plugin-PacketToolsAPIv1.2.3.pts"

DEFAULT_EXTENSION_DIRS = [
    Path(os.path.expanduser(r"~\Cisco Packet Tracer 9.0.0\extensions")),
    Path(os.path.expanduser(r"~\Cisco Packet Tracer 8.2.2\extensions")),
    Path(os.path.expanduser(r"~\Cisco Packet Tracer 8.2.0\extensions")),
    Path(r"C:\Program Files\Cisco Packet Tracer 9.0.0\extensions"),
    Path(r"C:\Program Files\Cisco Packet Tracer 8.2.2\extensions"),
]


class PTPluginInstaller:
    """Gestiona la presencia e instalación de la extensión de automatización en Packet Tracer."""

    @staticmethod
    def get_detected_extension_dirs() -> List[Path]:
        """Retorna las carpetas de extensiones que existen físicamente en la máquina."""
        found = []
        for p in DEFAULT_EXTENSION_DIRS:
            try:
                if p.exists():
                    found.append(p)
                elif p.parent.exists():  # La carpeta base de PT existe
                    p.mkdir(parents=True, exist_ok=True)
                    found.append(p)
            except (PermissionError, OSError):
                # Si no se tiene permiso de administrador para crear la subcarpeta en Program Files
                continue
        return found

    @staticmethod
    def is_plugin_installed() -> Tuple[bool, Optional[Path]]:
        """Comprueba si el archivo .pts o la carpeta de la extensión existe en alguna ruta."""
        for ext_dir in PTPluginInstaller.get_detected_extension_dirs():
            pts_file = ext_dir / "Plugin-PacketToolsAPIv1.2.3.pts"
            alt_pts = ext_dir / "Plugin-PacketToolsAPIv1.1.0.pts"
            unpacked_dir = ext_dir / "PacketToolsAPI"
            if pts_file.exists():
                return True, pts_file
            if alt_pts.exists():
                return True, alt_pts
            if unpacked_dir.exists() and (unpacked_dir / "main.js").exists():
                return True, unpacked_dir
        return False, None

    @staticmethod
    def install_plugin(progress_callback: Optional[callable] = None) -> Tuple[bool, str]:
        """
        Descarga e instala el plugin en los directorios de extensiones de Packet Tracer detectados.
        """
        target_dirs = PTPluginInstaller.get_detected_extension_dirs()
        if not target_dirs:
            return False, "No se detectaron carpetas de instalación de Cisco Packet Tracer."

        primary_target = target_dirs[0]
        pts_target = primary_target / "Plugin-PacketToolsAPIv1.2.3.pts"

        try:
            if progress_callback:
                progress_callback(f"Descargando Plugin-PacketToolsAPI desde repositorio oficial...")

            req = urllib.request.Request(
                PLUGIN_PTS_URL,
                headers={"User-Agent": "CTF-AI-Solver-Pro/2.0"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()

            # Guardar archivo .pts
            with open(pts_target, "wb") as f:
                f.write(data)

            # Replicar en otras carpetas si existen
            for alt_dir in target_dirs[1:]:
                try:
                    shutil.copy2(pts_target, alt_dir / "Plugin-PacketToolsAPIv1.2.3.pts")
                except Exception:
                    pass

            return True, f"Plugin instalado con éxito en: {pts_target}"
        except Exception as e:
            return False, f"Error descargando o instalando el plugin: {e}"
