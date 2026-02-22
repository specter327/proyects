# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .. import LayerInterface, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
from ....utils.logger import logger
from ....utils.debug import smart_debug
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from . import modules # Importamos el paquete para obtener su __package__ name
import threading

# Classes definition
class TransportLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "TRANSPORT"
    LAYER_TYPE = LAYER_TYPE_STRUCTURAL

    def __init__(self, layers_container: object) -> None:
        # Constructor hereditance
        super().__init__(layers_container)
        
        # Instance properties definition
        self._module_container = ModuleContainer()
        self.loaded_module: Optional[ModuleInterface] = None
        self.configurations: Optional[object] = None

        self.connections_table: Dict[int, ModuleInterface] = {}
        self.work_lock: threading.Lock = threading.Lock()
        self.logger = logger("TRANSPORT_LAYER")

    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info("Transport layer initializated")

        return True

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Transport layer stopped")
        return True

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def load_module(self, module: ModuleInterface) -> bool:
        # Verify the module status
        #if not module.configurated: raise RuntimeError(f"The module: {module.MODULE_NAME}, is not configurated. We can`t load it")
        #self.loaded_module = module
        return True

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def connect(self, module: ModuleInterface, configurations: object) -> str | bool:
        self.logger.info(f"Transport layer connecting with module: {str(module)}, with configurations: {configurations}")

        # Configure the module with the specified static configurations
        module_instance = module(self)
        module_instance.configure(configurations)

        # Try to start the module
        module_instance.start()

        # Try to connect the module
        connection_result = module_instance.connect()

        # Validate results
        self.logger.info(f"Connection result: {connection_result}")

        if not connection_result:
            self.logger.error(f"Connection result: ERROR") 
            return False

        # Generate a unique identification
        with self.work_lock:
            new_identifier = len(self.connections_table.keys()) + 1

            # Regist the new connection
            self.connections_table[new_identifier] = module_instance
            self.logger.info(f"Connection (connect) registered with the identifier: {new_identifier}")

        # Return results
        return new_identifier

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def receive_connection(self, module: ModuleInterface, configurations: object) -> str | bool:
        self.logger.info(f"Transport layer receiving connection with module: {str(module)}, with configurations: {configurations}")

        # Create a module instance
        module_instance = module(self)

        # Configure the module instance with the provided configurations
        module_instance.configure(configurations)

        # Start the module
        module_instance.start()

        # Try to receive a connection
        module_instance.receive_connection()

        # Create new identifier
        with self.work_lock:
            new_identifier = len(self.connections_table.keys()) + 1

            # Insert the new connection
            self.connections_table[new_identifier] = module_instance

            self.logger.info(f"Connection (receive) registered with the identifier: {new_identifier}")

        # Return results
        return new_identifier

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def disconnect(self, connection_identifier: str) -> bool:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connections table")

        # Get the connection controller
        self.logger.info(f"Disconnecting from connection: {connection_identifier}")
        connection_controller = self.connections_table.get(connection_identifier)

        # Execute the close standard operation
        disconnection_result = connection_controller.disconnect()
        self.logger.info(f"Disconnection result: {disconnection_result}") 
        return disconnection_result

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def send(self, connection_identifier: str, data: bytes) -> bool:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connections table")

        # Get the connection controller
        connection_controller = self.connections_table.get(connection_identifier)

        #self.logger.info(f"Sending data to the connection: {connection_identifier}")

        # Execute the standard write operation
        send_result = connection_controller.write(data)
        #self.logger.info(f"Sending result: {send_result}, to the connection: {connection_identifier}")
        return send_result

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def receive(self, connection_identifier: str, limit: int = None, timeout: int = None) -> bytes:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connection table")

        # Get the connection controller
        connection_controller = self.connections_table.get(connection_identifier)
        #self.logger.info(f"Receiving data from the connection: {connection_identifier}")

        # Execute the standard read operation
        receive_result = connection_controller.read(limit=limit, timeout=timeout)
        self.logger.info(f"Data received: {receive_result}, with length: {len(receive_result)}, from the connection: {connection_identifier}")
        return receive_result 

    @smart_debug(element_name="TRANSPORT_LAYER", include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.logger.info("Transport layer configurated")

        return True
    

class TransportModuleInterface(ModuleInterface, ABC):
    # Class properties definition
    CONNECTION_STATUS_ESTABLISHED: str = "ESTABLISHED"
    CONNECTION_STATUS_LISTENING: str = "LISTENING"
    CONNECTION_STATUS_CLOSED: str = "CLOSED"
    CONNECTION_STATUS_LOST: str = "LOST"
    TRANSPORT_TYPE_INTERNET: str = "INTERNET"
    TRANSPORT_TYPE_BLUETOOTH: str = "BLUETOOTH"
    TRANSPORT_TYPE_SERIAL: str = "SERIAL"
    TRANSPORT_TYPE_UNDEFINED: str = "UNDEFINED"
    TRANSPORT_TYPE: str = TRANSPORT_TYPE_UNDEFINED

    # Status properties
    @property
    @abstractmethod
    def is_active(self) -> bool: raise NotImplementedError

    @property
    @abstractmethod
    def is_connected(self) -> bool: raise NotImplementedError

    @property
    @abstractmethod
    def connection_status(self) -> str: raise NotImplementedError

    @property
    @abstractmethod
    def reception_buffer(self) -> bytearray: raise NotImplementedError

    @property
    @abstractmethod
    def connection_controller(self) -> object: raise NotImplementedError

    # Public methods
    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

    @abstractmethod
    def connect(self) -> bool: raise NotImplementedError

    @abstractmethod
    def configure(self, configurations: object) -> bool: raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> bool: raise NotImplementedError

    @abstractmethod
    def receive_connection(self) -> bool: raise NotImplementedError

    @abstractmethod
    def write(self, data: bytes) -> bool: raise NotImplementedError

    @abstractmethod
    def read(self, limit: int = None, timeout: int = None) -> bytes: raise NotImplementedError