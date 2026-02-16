# system/core/modules/communication_service/__init__.py

# Library import
from system import ModuleInterface
from shared.communication_architecture import layers
import subprocess
import threading
import time
import os
import random
from typing import Optional

# Classes definition
class CommunicationService(ModuleInterface):
    # Class properties definition
    MODULE_NAME = "CORE_COMMUNICATION_SERVICE"
    PORT_FILE = ".stark_port"

    def __init__(self,
        container,
        system
    ) -> None:
        # Constructor inheritance
        super().__init__(container, system)

        # Instance properties definition
        self.layers_container = layers.LayerContainer()
        self.running: bool = False
        self.worker_thread: Optional[threading.Thread] = None
    
    # Private methods
    def _command_loop(self, session) -> None:
        """
        Bucle de control en modo SERVIDOR. 
        Envía comandos y procesa resultados del agente conectado.
        """
        print(f"[{self.MODULE_NAME}] Command loop started as ACTIVE server.")
        
        # Ejemplo de comando inicial automático (lógica de Nexus)
        session.datapackages_handler.send_datapackage({"COMMAND": "whoami"})
        
        while self.running:
            try:
                # Recepción de resultados del cliente
                datapackage = session.datapackages_handler.receive_datapackage(timeout=10)
                
                if datapackage and "RESULT" in datapackage:
                    result = datapackage.get("RESULT")
                    print(f"[{self.MODULE_NAME}] Result received:\n{result}")
                    
                    # Aquí podrías implementar una cola de comandos (Queue)
                    # Por ahora, enviamos un keep-alive o esperamos instrucciones
                    time.sleep(5)
                    
            except Exception as e:
                print(f"[{self.MODULE_NAME}] Session error or client disconnected: {e}")
                break
        
        self.running = False

    def start(self) -> bool:
        print(f"[{self.MODULE_NAME}] Initializing Passive Server infrastructure...")
        
        try:
            # 1. Levantar infraestructura de capas
            self.layers_container.start()
            transport = self.layers_container.query_layer("TRANSPORT")
            comm_layer = self.layers_container.query_layer("COMMUNICATION")
            transport.start()
            comm_layer.start()

            # 2. Configuración de transporte (TCP/IP Listener)
            tcp_module = transport.query_module("TRANSPORT_TCP_IP")
            cfg = tcp_module.CONFIGURATIONS.copy()
            
            cfg.query_setting("LOCAL_ADDRESS").value.value = "127.0.0.1"
            
            # Asignación de puerto dinámico (rango efímero/privado)
            dynamic_port = random.randint(24391, 55490)
            cfg.query_setting("LOCAL_PORT").value.value = dynamic_port

            # 3. Iniciar escucha de conexiones
            print(f"[{self.MODULE_NAME}] Attempting to bind to port {dynamic_port}...")
            server_id = transport.receive_connection(tcp_module, cfg)
            
            if not server_id:
                print(f"[{self.MODULE_NAME}] Failed to bind/receive connections.")
                return False

            # Registro del puerto para componentes externos
            with open(self.PORT_FILE, "w") as f:
                f.write(str(dynamic_port))

            # 4. Creación de sesión en rol ACTIVO (Controlador)
            session_uuid = comm_layer.create_session(
                connection_identifier=server_id, 
                local_role="ACTIVE"
            )
            session = comm_layer.sessions_table.get(session_uuid)

            if session:
                self.running = True
                self.worker_thread = threading.Thread(
                    target=self._command_loop, 
                    args=(session,)
                )
                #sself.worker_thread.daemon = True
                self.worker_thread.start()
                return True

        except Exception as e:
            print(f"[{self.MODULE_NAME}] Critical failure during startup: {e}")
            if os.path.exists(self.PORT_FILE):
                os.remove(self.PORT_FILE)
            return False

        return False

    def stop(self) -> bool:
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        
        if os.path.exists(self.PORT_FILE):
            os.remove(self.PORT_FILE)
            
        self.layers_container.stop()
        print(f"[{self.MODULE_NAME}] Server stopped.")
        return True

    def configure(self, configurations) -> bool:
        """
        Implementación obligatoria del contrato de ModuleInterface.
        Evita que la clase sea marcada como abstracta.
        """
        self.configurations = configurations
        self._set_configurated(True)
        return True