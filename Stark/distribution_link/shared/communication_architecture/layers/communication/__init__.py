# Library import
from .. import LayerInterface, LayerContainer, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
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
        self.sessions_table: Dict[int, SessionLayer] = {}
    
    # Public methods
    def create_session(self, connection_identifier: int, local_role: str) -> int | bool:
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

        return session_identifier
    
    def query_modules(self) -> List[str]:
        pass

    def query_module(self, module_name: str) -> ModuleInterface:
        pass

    def configure(self, configurations: object) -> bool:
        pass

    def start(self) -> bool:
        pass

    def stop(self) -> bool:
        pass