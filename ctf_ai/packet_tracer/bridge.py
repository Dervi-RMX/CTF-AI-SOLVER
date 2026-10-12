"""
Bridge opcional para una extensión externa de Cisco Packet Tracer.
No es la API oficial de Packet Tracer: solo se considera operativo cuando la
extensión instalada se conecta y confirma cada operación.
"""

import asyncio
import logging
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

try:
    import aiohttp
    from aiohttp import web
    import socketio
    HAS_SOCKETIO = True
except ImportError:
    HAS_SOCKETIO = False


logger = logging.getLogger("ctf_ai.packet_tracer.bridge")


class PTBridgeServer:
    """
    Servidor Socket.IO para una extensión externa que escucha en 127.0.0.1:7531.
    El puerto no se interpreta como API oficial; la extensión debe devolver
    resultados explícitos para cada llamada.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 7531, simulated: bool = False):
        self.host = host
        self.port = port
        self.simulated = simulated

        self.sio: Optional[Any] = None
        self.app: Optional[Any] = None
        self.runner: Optional[Any] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        self._connected_sids: set[str] = set()
        self._pending_calls: Dict[str, asyncio.Future] = {}
        self._mock_topology: Dict[str, Any] = {"devices": {}, "links": []}
        self._is_running = False

    @property
    def transport_name(self) -> str:
        return "simulated" if self.simulated else "external_extension_socketio"

    @property
    def is_connected(self) -> bool:
        """Indica si hay al menos una instancia de Packet Tracer conectada al puente."""
        if self.simulated:
            return True
        return len(self._connected_sids) > 0

    def start(self) -> bool:
        """Inicia el servidor Socket.IO en un hilo daemon en segundo plano."""
        if not HAS_SOCKETIO:
            logger.warning("Bibliotecas socketio/aiohttp no disponibles. Operando en modo puente degradado.")
            return False

        if self._is_running:
            return True

        self._is_running = True
        self._thread = threading.Thread(target=self._run_server_thread, daemon=True, name="PTBridgeServerThread")
        self._thread.start()

        # Esperar brevemente a que el servidor inicialice
        time.sleep(0.5)
        return True

    def _run_server_thread(self) -> None:
        """Bucle de eventos asyncio en hilo secundario."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        # Servidor Socket.IO compatible con el cliente de la extensión
        self.sio = socketio.AsyncServer(
            async_mode="aiohttp",
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False,
        )
        self.app = web.Application()
        self.sio.attach(self.app)

        # Registro de eventos
        @self.sio.event
        async def connect(sid, environ):
            self._connected_sids.add(sid)
            logger.info(f"Cisco Packet Tracer conectado al puente (sid: {sid})")

        @self.sio.event
        async def disconnect(sid):
            self._connected_sids.discard(sid)
            logger.info(f"Cisco Packet Tracer desconectado (sid: {sid})")

        @self.sio.event
        async def tool_result(sid, data):
            call_id = data.get("tool_call_id")
            if call_id and call_id in self._pending_calls:
                future = self._pending_calls[call_id]
                if not future.done():
                    future.set_result(data.get("result", {}))

        async def start_web_app():
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, self.host, self.port)
            try:
                await site.start()
            except OSError as e:
                logger.warning(f"No se pudo enlazar el puerto {self.port}: {e}")

        self._loop.run_until_complete(start_web_app())
        try:
            self._loop.run_forever()
        finally:
            self._loop.close()

    def stop(self) -> None:
        """Detiene el servidor Socket.IO y limpia recursos."""
        self._is_running = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

    def wait_for_connection(self, timeout: float = 20.0, step_callback: Optional[Callable[[float], None]] = None) -> bool:
        """Espera activamente a que la extensión de Packet Tracer se conecte al puente."""
        if self.simulated:
            return True
        start_t = time.time()
        while time.time() - start_t < timeout:
            if self.is_connected:
                return True
            if step_callback:
                try:
                    step_callback(time.time() - start_t)
                except Exception:
                    pass
            time.sleep(0.3)
        return self.is_connected

    def call_tool(self, tool_name: str, tool_input: Optional[Dict[str, Any]] = None, timeout: float = 15.0) -> Dict[str, Any]:
        """
        Ejecuta una herramienta en Cisco Packet Tracer mediante la extensión Socket.IO.
        Bloquea de forma síncrona con timeout hasta recibir la respuesta.
        """
        tool_input = tool_input or {}

        if self.simulated:
            return self._execute_simulated(tool_name, tool_input)

        if not self.is_connected:
            return {
                "success": False,
                "error": "Cisco Packet Tracer no está conectado al puente en http://127.0.0.1:7531. Asegúrate de que la extensión 'Packet Tracer API' esté abierta.",
            }

        if not self._loop or not self.sio:
            return {"success": False, "error": "Servidor puente no inicializado."}

        call_id = str(uuid.uuid4())
        payload = {
            "tool_name": tool_name,
            "tool_call_id": call_id,
            "tool_input": tool_input,
        }

        future: asyncio.Future = self._loop.create_future()
        self._pending_calls[call_id] = future

        # Emitir llamada en el bucle del servidor
        async def emit_call():
            await self.sio.emit("tool_call", payload)

        asyncio.run_coroutine_threadsafe(emit_call(), self._loop)

        # Esperar respuesta
        start_t = time.time()
        while time.time() - start_t < timeout:
            if future.done():
                self._pending_calls.pop(call_id, None)
                return future.result()
            time.sleep(0.05)

        self._pending_calls.pop(call_id, None)
        return {"success": False, "error": f"Timeout esperando respuesta de Packet Tracer para '{tool_name}'"}

    def _execute_simulated(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Simulación local para tests y modo offline."""
        if tool_name == "addDevice":
            name = tool_input.get("deviceName") or tool_input.get("name", "Device")
            self._mock_topology["devices"][name] = tool_input
            return {"success": True, "deviceName": name, "status": "created"}

        elif tool_name == "addLink":
            self._mock_topology["links"].append(tool_input)
            return {"success": True, "status": "connected"}

        elif tool_name == "configurePcIp":
            name = tool_input.get("deviceName", "")
            if name in self._mock_topology["devices"]:
                self._mock_topology["devices"][name]["ip_config"] = tool_input
            return {"success": True, "status": "ip_assigned"}

        elif tool_name in ("configureIosDevice", "runDeviceCommands"):
            cmds = tool_input.get("commands", [])
            results = [{"command": c, "status": "ok", "output": ""} for c in cmds]
            return {"success": True, "results": results, "summary": "Comandos aplicados con éxito"}

        elif tool_name == "pingDevices":
            src = tool_input.get("sourceName", "")
            dst = tool_input.get("targetName", "")
            return {
                "success": True,
                "ok": True,
                "source": src,
                "target": dst,
                "sent": 4,
                "received": 4,
                "lossPercent": 0.0,
                "status": "ok",
                "output": "Success rate is 100 percent (4/4)",
            }

        elif tool_name == "clearWorkspace":
            self._mock_topology = {"devices": {}, "links": []}
            return {"success": True, "status": "cleared"}

        elif tool_name == "exportWorkspace":
            return {"success": True, "filename": tool_input.get("filename", "lab.pkt"), "status": "saved"}

        elif tool_name == "importWorkspace":
            return {"success": True, "filename": tool_input.get("filename", ""), "status": "opened"}

        elif tool_name == "getNetwork":
            return {"success": True, "network": self._mock_topology}

        return {"success": True, "simulated": True, "tool": tool_name}

    # Métodos convenientes de alto nivel:
    def add_device(self, dev_type: str, model: str, x: int, y: int, name: str) -> Dict[str, Any]:
        return self.call_tool("addDevice", {
            "type": dev_type,
            "model": model,
            "x": x,
            "y": y,
            "deviceName": name,
        })

    def add_link(self, dev1: str, port1: str, dev2: str, port2: str, cable_type: str = "copper_straight") -> Dict[str, Any]:
        return self.call_tool("addLink", {
            "device1": dev1,
            "port1": port1,
            "device2": dev2,
            "port2": port2,
            "cableType": cable_type,
        })

    def configure_pc_ip(self, name: str, ip: str, mask: str, gateway: str = "", dns: str = "") -> Dict[str, Any]:
        return self.call_tool("configurePcIp", {
            "deviceName": name,
            "ip": ip,
            "mask": mask,
            "gateway": gateway,
            "dns": dns,
        })

    def configure_ios_device(self, name: str, commands: List[str]) -> Dict[str, Any]:
        return self.call_tool("configureIosDevice", {
            "deviceName": name,
            "commands": commands,
        })

    def ping_devices(self, src: str, dst: str) -> Dict[str, Any]:
        return self.call_tool("pingDevices", {
            "sourceName": src,
            "targetName": dst,
        })

    def clear_workspace(self) -> Dict[str, Any]:
        return self.call_tool("clearWorkspace")

    def export_workspace(self, filename: str, target_dir: str = "") -> Dict[str, Any]:
        return self.call_tool("exportWorkspace", {
            "filename": filename,
            "targetDir": target_dir,
        })

    def import_workspace(self, filename: str, source_path: str = "") -> Dict[str, Any]:
        return self.call_tool("importWorkspace", {
            "filename": filename,
            "sourcePath": source_path,
        })

    def get_network(self) -> Dict[str, Any]:
        return self.call_tool("getNetwork")
