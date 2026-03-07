# application/shared/communication_architecture/layers/control/modules/shell_passive/__init__.py

# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__SELECTABLE__ = True
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__CONFIGURABLE__ = False
__STATIC_CONFIGURATIONS__ = {}

# Library import
import threading
import time
import subprocess
import queue
import traceback
from typing import Optional, Dict

from ... import ControlModule
from ......utils.logger import logger
from ......utils.debug import smart_debug
from configurations import Configurations

# Constants
ModuleConfigurations = Configurations()

# Classes definition
class ShellPassive(ControlModule):
    MODULE_NAME: str = "SYSTEM_SHELL_PASSIVE"
    CONTROL_NAME: str = "SYSTEM_SHELL"
    REMOTE_MODULE: str = "SYSTEM_SHELL_ACTIVE"
    CONFIGURATIONS: Configurations = ModuleConfigurations

    #print(f"{MODULE_NAME} class loaded")
    print(f"[{CONTROL_NAME}-{MODULE_NAME}] Class created successfully")

    def __init__(self, layer) -> None:
        # Constructor inheritance
        super().__init__(layer)

        # Instance properties assignment
        self._communication_layer = layer.layers_container.query_layer("COMMUNICATION")

        # Instance properties definition
        self.logger = logger(f"CONTROL_{self.MODULE_NAME}")
        self._listener_thread: Optional[threading.Thread] = None
        self._active_tasks: Dict[str, threading.Thread] = {}
        self._lock: threading.Lock = threading.Lock()
        #print(f"{self.MODULE_NAME} instance created")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Instance created successfully")

    # Private methods
    @smart_debug(element_name="SYSTEM_SHELL_PASSIVE", include_args=True, include_result=True)
    def _execute_command(self, session_id: str, packet_id: str, command: str) -> None:
        self.logger.debug(f"Executing task {packet_id}: {command}")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Executing command: {command}, from packet ID: {packet_id}, from session: {session_id}...")
        try:
            # Redireccionamos stderr a stdout para capturar mensajes de error de bash/cmd
            result = subprocess.check_output(
                command, 
                shell=True, 
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                timeout=120
            )
            output = result.decode('utf-8', errors='replace')
        except subprocess.TimeoutExpired:
            output = f"[!] Excedido tiempo límite de ejecución (120s) para: {command}"
        except subprocess.CalledProcessError as e:
            output = e.output.decode('utf-8', errors='replace') if e.output else "Error en proceso sin salida."
        except Exception as e:
            output = f"[!] Excepción crítica durante ejecución: {str(e)}"

        # Enviar respuesta usando la capa de comunicaciones
        # Nota: Aquí usamos "SYSTEM_SHELL" como identificador de destino para compatibilidad con el controlador
        response_payload = {
            "PACKET_ID": packet_id,
            "RESULT": output
        }

        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Command execution result:")
        print("==========")
        print(response_payload)
        print("==========")
        
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Sending execution command result to remote module: {self.REMOTE_MODULE}, from session: {session_id}...")
        self.logger.debug(f"Sending execution result for task {packet_id}")
        send_result = self._communication_layer.send_datapackage(
            datapackage=response_payload,
            module_name=self.REMOTE_MODULE, #self.MODULE_NAME,
            session_identifier=session_id
        )
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Command execution result send result: {send_result}")

        # Envia el paquete de datos al modulo: SYSTEM_SHELL, de rol: ACTIVE

        # Limpieza de la tabla de tareas
        with self._lock:
            if packet_id in self._active_tasks:
                print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Removing completed task: {packet_id}")
                del self._active_tasks[packet_id]

    @smart_debug(element_name="SYSTEM_SHELL_PASSIVE", include_args=True, include_result=True)
    def _listener_loop(self) -> None:
        self.logger.info("Passive Shell listener started.")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Starting command listener loop...")
        while self.active:
            # Iteramos sobre todas las sesiones registradas
            active_sessions = list(self._communication_layer.sessions_table.keys())
            idle_cycle = True 

            for session_id in active_sessions:
                #print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Receiving command datapackages from session: {session_id}, to local module: {self.MODULE_NAME}...")

                try:
                    package = self._communication_layer.receive_datapackage(
                        session_identifier=session_id,
                        module_name=self.MODULE_NAME,#self.MODULE_NAME,
                        timeout=2
                    )

                    # Recibe paquetes de datos para el modulo: SYSTEM_SHELL, de rol: PASSIVE

                    #print(f"Package received for module: {self.MODULE_NAME}:")
                    #print(package)

                    if package:
                        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Datapackage received for module: {self.MODULE_NAME}:")
                        print("==========")
                        print(package)
                        print("==========")

                        idle_cycle = False
                        command = package.get("COMMAND")
                        packet_id = package.get("PACKET_ID", "UNKNOWN")

                        if command:
                            print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Executing command: {command}, of package ID: {packet_id}...")
                            self.logger.info(f"Received command '{command}' from session {session_id}")
                            
                            task_thread = threading.Thread(
                                target=self._execute_command,
                                args=(session_id, packet_id, command),
                                daemon=True
                            )
                            
                            with self._lock:
                                self._active_tasks[packet_id] = task_thread
                                
                            task_thread.start()

                except queue.Empty:
                    continue
                except Exception:
                    self.logger.error(f"Error in listener loop for session {session_id}: {traceback.format_exc()}")

            if idle_cycle:
                time.sleep(0.5)

        #print(f"Stopping command listener routine")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Command listener routine stopped")
        self.logger.info("Passive Shell listener stopped.")

    # Public Methods
    @smart_debug(element_name="SYSTEM_SHELL_PASSIVE", include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Configurating module...")
        self.configurations = configurations
        self._set_configurated(True)
        self.logger.info("Module configured successfully.")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Module configurated successfully")
        return True

    @smart_debug(element_name="SYSTEM_SHELL_PASSIVE", include_args=True, include_result=True)
    def start(self) -> bool:
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Start the module?")
        #start_query = input("[y/n]>>> ").lower().strip()
        #if start_query not in ("n", "not"):
        #    print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Start approved")
        #else:
        #    print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Skipping module")
        #    return False

        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Starting module...")
        self.logger.info("Starting SHELL_PASSIVE module...")
        self._set_status(active=True)

        self._listener_thread = threading.Thread(
            target=self._listener_loop,
            daemon=False
        )
        self._listener_thread.start()

        self.logger.info("Module started successfully.")
        #print(f"{self.MODULE_NAME} started successfully")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Module started successfully")
        return True

    @smart_debug(element_name="SYSTEM_SHELL_PASSIVE", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Stopping SHELL_PASSIVE module...")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Stopping module...")
        self._set_status(active=False)
        
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=2.0)
            
        self.logger.info("Module stopped.")
        print(f"{self.MODULE_NAME} stopped successfully")
        print(f"[{self.CONTROL_NAME}-{self.MODULE_NAME}] Module stopped successfully")
        return True