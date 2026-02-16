# Library import
from .. import LayerInterface, ModuleInterface, ModuleContainer, LAYER_TYPE_STRUCTURAL
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from . import modules # Importamos el paquete para obtener su __package__ name

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

    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        return True

    def stop(self) -> bool:
        return True

    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    def load_module(self, module: ModuleInterface) -> bool:
        # Verify the module status
        #if not module.configurated: raise RuntimeError(f"The module: {module.MODULE_NAME}, is not configurated. We can`t load it")
        #self.loaded_module = module
        return True

    def connect(self, module: ModuleInterface, configurations: object) -> str | bool:
        # Configure the module with the specified static configurations
        module_instance = module(self)
        module_instance.configure(configurations)

        # Try to start the module
        module_instance.start()

        # Try to connect the module
        connection_result = module_instance.connect()

        # Validate results
        print("Connection result:", connection_result)
        if not connection_result: return False

        # Generate a unique identification
        new_identifier = len(self.connections_table.keys()) + 1

        # Regist the new connection
        self.connections_table[new_identifier] = module_instance

        # Return results
        return new_identifier

    def receive_connection(self, module: ModuleInterface, configurations: object) -> str | bool:
        # Create a module instance
        module_instance = module(self)

        # Configure the module instance with the provided configurations
        module_instance.configure(configurations)

        # Start the module
        module_instance.start()

        # Try to receive a connection
        module_instance.receive_connection()

        # Create new identifier
        new_identifier = len(self.connections_table.keys()) + 1

        # Insert the new connection
        self.connections_table[new_identifier] = module_instance

        # Return results
        return new_identifier


    def disconnect(self, connection_identifier: str) -> bool:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connections table")

        # Get the connection controller
        connection_controller = self.connections_table.get(connection_identifier)

        # Execute the close standard operation
        return connection_controller.disconnect()

    def send(self, connection_identifier: str, data: bytes) -> bool:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connections table")

        # Get the connection controller
        connection_controller = self.connections_table.get(connection_identifier)

        # Execute the standard write operation
        return connection_controller.write(data)

    def receive(self, connection_identifier: str, limit: int = None, timeout: int = None) -> bytes:
        if not connection_identifier in self.connections_table: raise KeyError(f"The specified device: {connection_identifier}, not exists in the connection table")

        # Get the connection controller
        connection_controller = self.connections_table.get(connection_identifier)

        # Execute the standard read operation
        return connection_controller.read(limit=limit, timeout=timeout)

    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        return True
    

class TransportModuleInterface(ModuleInterface, ABC):
    # Class properties definition
    CONNECTION_STATUS_ESTABLISHED: str = "ESTABLISHED"
    CONNECTION_STATUS_LISTENING: str = "LISTENING"
    CONNECTION_STATUS_CLOSED: str = "CLOSED"
    CONNECTION_STATUS_LOST: str = "LOST"

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