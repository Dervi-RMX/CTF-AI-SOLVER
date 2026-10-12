"""
Agente autónomo de automatización en bucle cerrado para Cisco Packet Tracer.
Implementa el ciclo: PLANIFICAR -> EJECUTAR -> OBSERVAR -> VERIFICAR -> CORREGIR -> GUARDAR.
Soporta pausa, reanudación, cancelación y telemetría en tiempo real.
"""

import threading
import time
from typing import Any, Callable, Dict, List, Optional

from ctf_ai.packet_tracer.bridge import PTBridgeServer
from ctf_ai.packet_tracer.desktop import PacketTracerDesktop
from ctf_ai.packet_tracer.ios_generator import CiscoIOSGenerator
from ctf_ai.packet_tracer.models import AgentState, NetworkBlueprint, PingCheck
from ctf_ai.packet_tracer.validator import validate_blueprint


class PacketTracerAgent:
    """
    Agente que orquesta la ejecución visual y la autocuración de prácticas
    en Cisco Packet Tracer de forma autónoma.
    """

    def __init__(self, bridge: Optional[PTBridgeServer] = None, desktop: Optional[PacketTracerDesktop] = None):
        self.bridge = bridge or PTBridgeServer()
        self.desktop = desktop or PacketTracerDesktop()
        self.state = AgentState()

        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._on_update: Optional[Callable[[AgentState], None]] = None
        self.last_results: List[Dict[str, Any]] = []

    def execute_blueprint_async(
        self,
        blueprint: NetworkBlueprint,
        save_path: Optional[str] = None,
        on_update: Optional[Callable[[AgentState], None]] = None,
    ) -> None:
        """Inicia la ejecución del plano en un hilo en segundo plano."""
        self._stop_event.clear()
        self._pause_event.clear()
        self._on_update = on_update

        self._thread = threading.Thread(
            target=self._run_closed_loop,
            args=(blueprint, save_path),
            daemon=True,
            name="PTAgentWorkerThread",
        )
        self._thread.start()

    def execute_blueprint_sync(
        self,
        blueprint: NetworkBlueprint,
        save_path: Optional[str] = None,
        on_update: Optional[Callable[[AgentState], None]] = None,
    ) -> AgentState:
        """Ejecuta el plano de forma síncrona (bloqueante)."""
        self.execute_blueprint_async(blueprint, save_path, on_update)
        if self._thread:
            self._thread.join()
        return self.state

    def pause(self) -> None:
        """Pausa la ejecución tras completar la acción en curso."""
        self._pause_event.set()
        self.state.status = "paused"
        self._emit_update(f"⏸️ Automatización pausada por el usuario.")

    def resume(self) -> None:
        """Reanuda la ejecución pausada."""
        self._pause_event.clear()
        self.state.status = "running"
        self._emit_update(f"▶️ Automatización reanudada.")

    def stop(self) -> None:
        """Detiene y aborta la ejecución."""
        self._stop_event.set()
        self._pause_event.clear()
        self.state.status = "stopped"
        self._emit_update(f"⏹️ Automatización detenida.")

    def _check_pause_and_stop(self) -> bool:
        """Retorna True si se solicitó detener la ejecución."""
        while self._pause_event.is_set():
            if self._stop_event.is_set():
                return True
            time.sleep(0.2)
        return self._stop_event.is_set()

    def _emit_update(self, log_msg: str, current_step: Optional[str] = None) -> None:
        self.state.add_log(log_msg)
        if current_step:
            self.state.current_step = current_step
        if self.state.total_steps > 0:
            self.state.progress_percent = min(100.0, (self.state.completed_steps / self.state.total_steps) * 100.0)
        if self._on_update:
            try:
                self._on_update(self.state)
            except Exception:
                pass

    def _run_closed_loop(self, blueprint: NetworkBlueprint, save_path: Optional[str]) -> None:
        """Ciclo completo: Planificar -> Ejecutar -> Observar -> Verificar -> Corregir -> Guardar."""
        self.state.status = "running"
        self.state.error_message = None
        self.state.completed_steps = 0
        self.last_results = []

        # Cálculo de pasos totales
        total = (
            1  # Inicialización de PT y Puente
            + 1  # Limpieza de lienzo
            + len(blueprint.devices)  # Colocación de dispositivos
            + len(blueprint.links)  # Cableado
            + len(blueprint.configs)  # Configuraciones
            + len(blueprint.verifications)  # Verificaciones
            + (1 if save_path else 0)  # Guardar archivo
        )
        self.state.total_steps = max(total, 1)

        try:
            issues = validate_blueprint(blueprint)
            errors = [issue for issue in issues if issue.severity == "error"]
            for issue in issues:
                self._emit_update(f"[PLAN] {issue.severity.upper()}: {issue.message}", current_step="Validando plano")
            if errors:
                raise ValueError(
                    "El plano no es ejecutable: "
                    + "; ".join(issue.message for issue in errors[:5])
                )

            # 1. PLANIFICAR & APERTURA DE APLICACIÓN
            self._emit_update(f"[PT] Iniciando entorno de Cisco Packet Tracer...", current_step="Preparando entorno")
            self.bridge.start()
            ok, msg = self.desktop.launch(wait_seconds=2.0)
            if not ok and not self.bridge.simulated:
                self._emit_update(f"[PT Alerta] {msg}. Continuando con puente Socket.IO...")

            self.desktop.bring_to_foreground()

            # Esperar activamente la conexión real de Packet Tracer
            if not self.bridge.simulated and not self.bridge.is_connected:
                self._emit_update(f"[PT] Esperando conexión de la extensión en http://127.0.0.1:7531...", current_step="Esperando conexión PT")
                self.desktop.trigger_extensions_menu()

                connected = False
                for wait_i in range(25):
                    if self._check_pause_and_stop():
                        return
                    if self.bridge.is_connected:
                        connected = True
                        break
                    if wait_i == 4:
                        self.desktop.bring_to_foreground()
                        self.desktop.trigger_extensions_menu()
                        self._emit_update("[PT Tip] Abre en Packet Tracer: Menú 'Extensions' -> Haz clic en 'Packet Tracer API'.")
                    time.sleep(1.0)

                if not connected and not self.bridge.is_connected:
                    raise RuntimeError(
                        "No se detectó la conexión de la extensión de Cisco Packet Tracer en el puerto 7531. "
                        "Asegúrate de que Packet Tracer esté abierto y en el menú 'Extensions' hagas clic en 'Packet Tracer API'."
                    )

                self._emit_update(f"[PT] ✅ ¡Conexión con Cisco Packet Tracer establecida! Automatizando en vivo en la pantalla...")

            self.state.completed_steps += 1

            if self._check_pause_and_stop():
                return

            # 2. No borrar una topología existente sin una orden explícita.
            self._emit_update(
                "[PT] Conservando la topología existente; la extensión decidirá si puede reutilizarla.",
                current_step="Inspeccionando workspace",
            )
            network_result = self.bridge.get_network()
            if not network_result.get("success", False) and not self.bridge.simulated:
                raise RuntimeError(f"No se pudo inspeccionar el workspace de Packet Tracer: {network_result.get('error', 'respuesta inválida')}")
            self.state.completed_steps += 1
            time.sleep(0.2)

            # 3. EJECUTAR: COLOCAR DISPOSITIVOS EN EL ESPACIO VISUAL
            for dev in blueprint.devices:
                if self._check_pause_and_stop():
                    return
                self.state.active_device = dev.name
                self._emit_update(
                    f"[PT] Colocando {dev.device_type.upper()} '{dev.name}' (Modelo: {dev.model}) en ({dev.x}, {dev.y})...",
                    current_step=f"Colocando {dev.name}",
                )
                result = self.bridge.add_device(
                    dev_type=dev.device_type,
                    model=dev.model,
                    x=dev.x,
                    y=dev.y,
                    name=dev.name,
                )
                self._record_tool_result(f"addDevice:{dev.name}", result)
                self.state.completed_steps += 1
                time.sleep(0.3)

            # 4. EJECUTAR: CONECTAR CABLES
            for link in blueprint.links:
                if self._check_pause_and_stop():
                    return
                self._emit_update(
                    f"[PT] Conectando cable {link.cable_type}: {link.device1} [{link.port1}] <---> {link.device2} [{link.port2}]...",
                    current_step=f"Conectando {link.device1} - {link.device2}",
                )
                result = self.bridge.add_link(
                    dev1=link.device1,
                    port1=link.port1,
                    dev2=link.device2,
                    port2=link.port2,
                    cable_type=link.cable_type,
                )
                self._record_tool_result(f"addLink:{link.device1}:{link.port1}", result)
                self.state.completed_steps += 1
                time.sleep(0.3)

            # 5. EJECUTAR: APLICAR CONFIGURACIONES A DISPOSITIVOS
            for dev_name, cfg in blueprint.configs.items():
                if self._check_pause_and_stop():
                    return
                self.state.active_device = dev_name
                if cfg.is_pc and cfg.pc_ip and cfg.pc_mask:
                    self._emit_update(
                        f"[CLI] Configurando Host '{dev_name}' -> IP: {cfg.pc_ip}/{cfg.pc_mask}, Gateway: {cfg.pc_gateway or 'N/A'}...",
                        current_step=f"Configurando PC {dev_name}",
                    )
                    result = self.bridge.configure_pc_ip(
                        name=dev_name,
                        ip=cfg.pc_ip,
                        mask=cfg.pc_mask,
                        gateway=cfg.pc_gateway or "",
                        dns=cfg.pc_dns or "",
                    )
                    self._record_tool_result(f"configurePcIp:{dev_name}", result)
                else:
                    ios_cmds = CiscoIOSGenerator.generate_device_ios_script(cfg)
                    self._emit_update(
                        f"[CLI] Inyectando configuración Cisco IOS en '{dev_name}' ({len(ios_cmds)} líneas)...",
                        current_step=f"Configurando IOS en {dev_name}",
                    )
                    result = self.bridge.configure_ios_device(dev_name, ios_cmds)
                    self._record_tool_result(f"configureIosDevice:{dev_name}", result)

                self.state.completed_steps += 1
                time.sleep(0.4)

            # 6. OBSERVAR & VERIFICAR CONECTIVIDAD
            self.state.status = "verifying"
            failed_pings: List[PingCheck] = []

            for v in blueprint.verifications:
                if self._check_pause_and_stop():
                    return
                self._emit_update(
                    f"[VERIFY] Probando conectividad ICMP: {v.source} ➔ {v.target}...",
                    current_step=f"Verificando {v.source} -> {v.target}",
                )
                res = self.bridge.ping_devices(v.source, v.target)
                self._record_tool_result(f"ping:{v.source}:{v.target}", res)
                is_ok = res.get("ok", False) or res.get("lossPercent", 100.0) < 50.0

                if is_ok:
                    self._emit_update(f"  ✔ Ping Exitoso: {v.source} ➔ {v.target} (Tasa: {100.0 - res.get('lossPercent', 0)}%)")
                else:
                    self._emit_update(f"  ❌ Ping Fallido: {v.source} ➔ {v.target} - {res.get('status', 'no_reply')}")
                    failed_pings.append(v)

                self.state.completed_steps += 1
                time.sleep(0.3)

            # 7. CORREGIR (AUTO-CURACIÓN EN BUCLE CERRADO)
            if failed_pings:
                self.state.status = "correcting"
                self._emit_update(f"[CORRECT] Detectados {len(failed_pings)} fallos de conectividad. Aplicando auto-curación...")
                for fp in failed_pings:
                    source_cfg = blueprint.configs.get(fp.source)
                    if not source_cfg or source_cfg.is_pc:
                        self._emit_update(
                            f"[CORRECT] No hay una corrección IOS segura definida para {fp.source}; "
                            "se conserva el fallo como pendiente."
                        )
                        continue
                    interface_commands = []
                    for iface in source_cfg.interfaces:
                        interface_commands.extend(["interface " + iface.name, "no shutdown", "exit"])
                    if not interface_commands:
                        self._emit_update(
                            f"[CORRECT] No hay interfaces configuradas para {fp.source}; "
                            "se conserva el fallo como pendiente."
                        )
                        continue
                    self._emit_update(f"[CORRECT] Revalidando interfaces configuradas en {fp.source}...")
                    correction_result = self.bridge.configure_ios_device(
                        fp.source,
                        ["enable", "configure terminal", *interface_commands, "end"],
                    )
                    self._record_tool_result(f"correct:{fp.source}", correction_result)
                    # Re-intentar verificación
                    retry_res = self.bridge.ping_devices(fp.source, fp.target)
                    self._record_tool_result(f"retry-ping:{fp.source}:{fp.target}", retry_res)
                    if retry_res.get("ok", False) or retry_res.get("lossPercent", 100.0) < 50.0:
                        self._emit_update(f"  ✔ [CORRECTED] Conectividad restablecida exitosamente: {fp.source} ➔ {fp.target}")
                    else:
                        self._emit_update(f"  ✖ [PENDING] El fallo persiste: {fp.source} ➔ {fp.target}")

            # 8. GUARDAR .PKT
            if save_path:
                if self._check_pause_and_stop():
                    return
                self._emit_update(f"[GUARDAR] Exportando archivo de topología a '{save_path}'...", current_step="Guardando .pkt")
                result = self.bridge.export_workspace(filename=save_path)
                self._record_tool_result("exportWorkspace", result)
                self._record_tool_result("save", result)
                self.state.completed_steps += 1

            self.state.status = "completed"
            self.state.progress_percent = 100.0
            self._emit_update(f"🎉 Automatización de Cisco Packet Tracer completada con éxito.", current_step="Completado")

        except Exception as e:
            self.state.status = "error"
            self.state.error_message = str(e)
            self._emit_update(f"❌ Error durante la automatización: {e}", current_step="Error")

    def _record_tool_result(self, operation: str, result: Dict[str, Any]) -> None:
        """Registra y valida la respuesta real del adaptador."""
        entry = {"operation": operation, "result": result}
        self.last_results.append(entry)
        if not result.get("success", False):
            raise RuntimeError(
                f"La operación '{operation}' no fue confirmada por Packet Tracer: "
                f"{result.get('error', 'respuesta sin éxito')}"
            )
