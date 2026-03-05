# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .. import LayerInterface, LayerContainer, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
from ....utils.logger import logger
from ....utils.debug import smart_debug
from abc import ABC, abstractmethod
from configurations import Configurations, Setting
from . import modules
from datapackage import Datapackage
from typing import Optional, Dict, List
import uuid
import queue
import threading

# Classes definition
class SessionLayer:
    # Class properties definition
    LAYER_NAME: str = "SESSION_LAYER"

    def __init__(self,
        layers_container: object,
        connection_identifier: int,
        local_role: str
    ) -> None:
        # Instance properties assignment
        self.layers_container = layers_container
        self.connection_identifier = connection_identifier
        self.transport_layer = self.layers_container.query_layer("TRANSPORT")
        self.local_role = local_role

        # Instance properties definition
        self.datapackages_handler: Optional[Datapackage] = None

        self.virtual_layers_container: LayerContainer = LayerContainer()
        self._protection_layer_class = self.layers_container.query_layer("PROTECTION")
        self._security_layer_class = self.layers_container.query_layer("SECURITY")
        self.protection_layer: Optional[LayerInterface] = None
        self.security_layer: Optional[LayerInterface] = None
        self.logger = logger("SESSION_LAYER")

        # Inject the structural layers
        self._inject_structural_layers()

    # Private methods
    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def _set_datapackage_handler(self) -> bool:
        self.logger.debug(f"Setting datapackages handler")
        self.datapackages_handler = Datapackage(
            write_function=self.send,
            read_function=self.receive,

        )
        self.logger.debug(f"Datapackage handler set successfully")
        return True

    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def _inject_structural_layers(self) -> bool:
        self.logger.debug(f"Injecting structural layers")
        self.virtual_layers_container.layers_table["TRANSPORT"] = self.transport_layer
        self.logger.debug(f"Structural layers injected successfully")

        return True

    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def _inject_session_layers(self, layer_instance: LayerInterface) -> bool:
        self.logger.debug(f"Injecting session layers")
        self.virtual_layers_container.layers_table[layer_instance.LAYER_NAME] = layer_instance
        self.logger.debug(f"Session layers injected successfully")

        return True

    # Public methods
    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def send(self, data: bytes) -> bool:
        # Resend the data throught the layers stack
        self.logger.debug(f"Sending data: {data}, with length: {len(data)}")
        self.protection_layer.send(self.connection_identifier, data)
        self.logger.debug(f"Data sended successfully")

        return True

    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def receive(self, limit: Optional[int] = None, timeout: Optional[int] = None) -> bytes:
        self.logger.debug(f"Receiving data from session with limit: {limit}, and timeout: {timeout}")
        # Receive data throught the layers stack
        return self.protection_layer.receive(self.connection_identifier, limit, timeout)

    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def receive_datapackage(self, timeout: Optional[int] = None) -> dict:
        return self.datapackages_handler.receive_datapackage(timeout=timeout)

    def start(self) -> bool:
        self.logger.info("Starting session layer")
        # Create a protection layer instance
        self.logger.info("Instanciating Protection Layer")
        self.protection_layer = self._protection_layer_class(self.virtual_layers_container)

        # Configure the current protection layer
        self.logger.info("Configurating Protection Layer")
        self.protection_layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = self.connection_identifier
        self.logger.info("Starting Protection Layer")
        self.protection_layer.start()

        # Negotiate the protection layer
        self.logger.info("Negotiating Protection Layer")
        self.protection_layer.negotiate(
            role=self.local_role,
            connection_identifier=self.connection_identifier
        )

        # Inject protection layer
        self.logger.info("Injecting Protection Layer")
        self._inject_session_layers(self.protection_layer)

        # Create a security layer instance
        self.logger.info("Instanciating Security Layer")
        self.security_layer = self._security_layer_class(self.virtual_layers_container)

        # Configure the current security layer
        self.logger.info("Configurating Session Layer")
        self.security_layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = self.connection_identifier
        
        self.logger.info("Starting Security Layer")
        self.security_layer.start()

        # Negotiate the security layer
        #self.security_layer.negotiate(
        #    role=self.local_role,
        #    connection_identifier=self.connection_identifier
        #)

        # Inject protection layer
        self.logger.info("Injecting Security Layer")
        self._inject_session_layers(self.security_layer)

        # Start the datapackage handler
        self._set_datapackage_handler()

        # Return results
        self.logger.info("Session started successfully")
        return True

    @smart_debug(element_name=LAYER_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Stopping session")
        pass

        self.logger.info("Session stopped successfully")
        return True

class CommunicationLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "COMMUNICATION"
    LAYER_TYPE = LAYER_TYPE_STRUCTURAL

    def __init__(self, layers_container: object) -> None:
        super().__init__(layers_container)
        self._module_container = ModuleContainer()
        self.sessions_table: Dict[str, SessionLayer] = {}
        self.datapackages_table: Dict[str, Dict[str, queue.Queue]] = {}
        self.loaded_modules: Dict[str, ModuleInterface] = {}
        self.configurations: Optional[object] = None
        self._lock = threading.Lock()
        self.logger = logger("COMMUNICATION_LAYER")
        print("Communication layer instantiated successfully")
    
    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    # Private methods
    @smart_debug(element_name="COMMUNICATION_LAYER")
    def _session_dispatcher(self, session_identifier: str) -> None:
        """Rutina concurrente por sesión para demultiplexación de paquetes."""
        self.logger.info(f"Dispatcher started for session: {session_identifier}")

        with self._lock:
            session = self.sessions_table.get(session_identifier)
        
        while session and session_identifier in self.sessions_table:
            try:
                package = session.receive_datapackage(timeout=10.0)
                
                if not package:
                    continue

                print(f"Datapackage received:")
                print(package)
                
                module_id = package.get("__MODULE_IDENTIFIER__")
                if not module_id:
                    print(f"Package without module identifier in session: {session_identifier}")
                    self.logger.warning(f"Package without module identifier in session: {session_identifier}")
                    continue

                with self._lock:
                    if session_identifier not in self.datapackages_table:
                        print(f"Session datapackages table created for session: {session_identifier}")
                        self.datapackages_table[session_identifier] = {}
                    
                    if module_id not in self.datapackages_table[session_identifier]:
                        print(f"Module datapackages queue created for module: {module_id}, from session: {session_identifier}")
                        self.datapackages_table[session_identifier][module_id] = queue.Queue(maxsize=500)
                    
                    self.datapackages_table[session_identifier][module_id].put(package)
                    print(f"Datapackage append to the queue for session: {session_identifier}, for module: {module_id}")

            except Exception as e:
                # Usamos continue en lugar de break para no matar el hilo ante un paquete corrupto
                if session_identifier in self.sessions_table:
                    self.logger.error(f"Error in dispatcher {session_identifier}: {str(e)}")
                continue

        self.logger.info(f"Stopping dispatcher for session: {session_identifier}")
        return None

    # Public methods
    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def create_session(self, connection_identifier: int, local_role: str) -> str | bool:
        self.logger.info(f"Creating session for connection: {connection_identifier} with role: {local_role}")
        
        try:
            session = SessionLayer(
                self.layers_container,
                connection_identifier,
                local_role
            )
            session.start()

            session_identifier = str(uuid.uuid4())
            self.sessions_table[session_identifier] = session
            
            # Inicializar la tabla de paquetes para esta sesión
            with self._lock:
                self.datapackages_table[session_identifier] = {}
            
            # Lanzar el despachador de forma asíncrona
            threading.Thread(
                target=self._session_dispatcher, 
                args=(session_identifier,), 
                daemon=True
            ).start()
            
            self.logger.info(f"Session created successfully: {session_identifier}")
            return session_identifier
            
        except Exception as e:
            self.logger.error(f"Failed to create session for connection {connection_identifier}: {str(e)}")
            return False

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def stop_session(self, session_identifier: str) -> bool:
        if session_identifier not in self.sessions_table:
            self.logger.error(f"Session {session_identifier} not found")
            return False
            
        session = self.sessions_table.get(session_identifier)
        if session:
            session.stop()
            del self.sessions_table[session_identifier]
            
            # Limpieza de memoria (Garbage Collection de las colas)
            with self._lock:
                self.datapackages_table.pop(session_identifier, None)
                
            self.logger.info(f"Session {session_identifier} stopped and removed")
        return True

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def send_datapackage(self, datapackage: dict, module_name: str, session_identifier: str) -> bool:
        self.logger.debug(f"Sending datapackage: {datapackage}, to module: {module_name}, to the session: {session_identifier}")
        session = self.sessions_table.get(session_identifier)
        if not session:
            self.logger.error(f"The specified session not exists")
            return False

        datapackage["__MODULE_IDENTIFIER__"] = module_name
        
        # Try to unpackage datapackage
        #try:
        #    datapackage_bytes = json.dumps(datapackage).encode("UTF-8")
        #except Exception as Error:
        #    self.logger.debug(f"Error unpacking datapackage: {datapackage} ({Error})")
        #    return False

        try:
            self.logger.debug(f"Sending datapackage through the session")
            return session.datapackages_handler.send_datapackage(datapackage)
        except Exception as e:
            self.logger.error(f"Failed to send package: {datapackage}, from {module_name}: {e}, to the session: {session_identifier}")
            return False

    @smart_debug(element_name="COMMUNICATION_LAYER")
    def receive_datapackage(self, session_identifier: str, module_name: str, timeout: float = 0.1) -> Optional[dict]:
        self.logger.debug(f"Receiving datapackage from session: {session_identifier}, from module: {module_name}, with timeout: {timeout}")
        with self._lock:
            q = self.datapackages_table.get(session_identifier, {}).get(module_name)
        
        if not q:
            self.logger.warning(f"Any datapackage received")
            #print("Any datapackage received")
            return None
            
        try:
            self.logger.debug("One datapackage received")
            #print("One datapackage received")
            return q.get(timeout=timeout)
        except queue.Empty:
            self.logger.warning("Any datapackage received")
            #print("Any datapackage received")
            return None

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def load_module(self, module_name: str, configurations: object = None) -> bool:
        self.logger.info(f"Loading communication module: {module_name}")
        module_class = self.query_module(module_name)
        if not module_class:
            self.logger.error(f"Module {module_name} not found in container")
            return False
            
        try:
            module_instance = module_class(self)
            if configurations:
                module_instance.configure(configurations)
            module_instance.start()
            
            self.loaded_modules[module_name] = module_instance
            self.logger.info(f"Module {module_name} loaded and started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error loading module {module_name}: {str(e)}")
            return False

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.logger.info("Communication layer configurated")
        return True

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def start(self) -> bool:
        self.logger.info("Starting Communication layer")
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info(f"Modules discovered: {self.query_modules()}")

        for module_name in self.query_modules():
            module_instance = self.query_module(module_name)
            module_configurations = module_instance.CONFIGURATIONS.copy()
            self.load_module(module_name, module_configurations)
            self.logger.info(f"Module: {module_name}, loaded successfully")

        self.logger.info("Communication layer loaded successfully")
        print("Communication layer started successfully")

        return True

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Stopping Communication layer")
        
        for mod_name, mod_instance in self.loaded_modules.items():
            self.logger.debug(f"Stopping module: {mod_name}")
            mod_instance.stop()
            
        self.loaded_modules.clear()
        
        for session_id in list(self.sessions_table.keys()):
            self.stop_session(session_id)
            
        self.logger.info("Communication layer stopped")
        return True

class CommunicationModule(ModuleInterface, ABC):
    # Class properties definition
    CONFIGURATIONS: Optional[Configurations] = Configurations()

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)
