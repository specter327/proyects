# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .. import LayerInterface, LayerContainer, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
from ....utils.logger import logger
from ....utils.debug import smart_debug
from . import modules
from datapackage import Datapackage
from typing import Optional, Dict, List
import uuid

# Classes definition
class SessionLayer:
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

        # Inject the structural layers
        self._inject_structural_layers()

    # Private methods
    def _set_datapackage_handler(self) -> bool:
        self.datapackages_handler = Datapackage(
            write_function=self.send,
            read_function=self.receive,

        )
        return True

    def _inject_structural_layers(self) -> bool:
        self.virtual_layers_container.layers_table["TRANSPORT"] = self.transport_layer

        return True

    def _inject_session_layers(self, layer_instance: LayerInterface) -> bool:
        self.virtual_layers_container.layers_table[layer_instance.LAYER_NAME] = layer_instance
        
        return True

    # Public methods
    def send(self, data: bytes) -> bool:
        # Resend the data throught the layers stack
        self.protection_layer.send(self.connection_identifier, data)
        return True

    def receive(self, limit: Optional[int] = None, timeout: Optional[int] = None) -> bytes:
        # Receive data throught the layers stack
        return self.protection_layer.receive(self.connection_identifier, limit, timeout)

    def start(self) -> bool:
        # Create a protection layer instance
        self.protection_layer = self._protection_layer_class(self.virtual_layers_container)

        # Configure the current protection layer
        self.protection_layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = self.connection_identifier
        self.protection_layer.start()

        # Negotiate the protection layer
        self.protection_layer.negotiate(
            role=self.local_role,
            connection_identifier=self.connection_identifier
        )

        # Inject protection layer
        self._inject_session_layers(self.protection_layer)

        # Create a security layer instance
        self.security_layer = self._security_layer_class(self.virtual_layers_container)

        # Configure the current security layer
        self.security_layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = self.connection_identifier
        self.security_layer.start()

        # Negotiate the security layer
        #self.security_layer.negotiate(
        #    role=self.local_role,
        #    connection_identifier=self.connection_identifier
        #)

        # Inject protection layer
        self._inject_session_layers(self.security_layer)

        # Start the datapackage handler
        self._set_datapackage_handler()

        # Return results
        return True

    def stop(self) -> bool:
        pass

class CommunicationLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "COMMUNICATION"
    LAYER_TYPE = LAYER_TYPE_STRUCTURAL

    def __init__(self, layers_container: object) -> None:
        # Constructor hereditance
        super().__init__(layers_container)

        # Instance properties definition
        self._module_container = ModuleContainer()
        self.sessions_table: Dict[str, SessionLayer] = {}
        self.loaded_modules: Dict[str, ModuleInterface] = {}
        self.configurations: Optional[object] = None
        self.logger = logger("COMMUNICATION_LAYER")
    
    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    # Public methods
    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def create_session(self, connection_identifier: int, local_role: str) -> str | bool:
        self.logger.info(f"Creating session for connection: {connection_identifier} with role: {local_role}")
        
        try:
            # Try to create the session based on the connection identifier
            session = SessionLayer(
                self.layers_container,
                connection_identifier,
                local_role
            )

            # Start the session
            session.start()

            # Insert the new session to the sessions table
            session_identifier = str(uuid.uuid4())
            self.sessions_table[session_identifier] = session
            
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
            self.logger.info(f"Session {session_identifier} stopped and removed")
        return True

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
            # Instanciamos pasándole la capa actual (self)
            module_instance = module_class(self)
            
            if configurations:
                module_instance.configure(configurations)
                
            # Iniciamos el módulo (ej. el bucle del CommunicationClient)
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
        # Load all available dynamic modules from the package
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info(f"Modules discovered: {self.query_modules()}")

        # Load every module
        for module_name in self.query_modules():
            # Get the module instance
            module_instance = self.query_module(module_name)
            module_configurations = module_instance.CONFIGURATIONS.copy()

            # Load the module
            self.load_module(module_instance, module_configurations)

            self.logger.info(f"Module: {module_name}, loaded successfully")

        self.logger.info("Communication layer loaded successfully")
        return True

    @smart_debug(element_name="COMMUNICATION_LAYER", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Stopping Communication layer")
        
        # Stop all loaded modules (e.g., stopping the CommunicationClient threads)
        for mod_name, mod_instance in self.loaded_modules.items():
            self.logger.debug(f"Stopping module: {mod_name}")
            mod_instance.stop()
            
        self.loaded_modules.clear()
        
        # Stop all active sessions
        for session_id in list(self.sessions_table.keys()):
            self.stop_session(session_id)
            
        self.logger.info("Communication layer stopped")
        return True