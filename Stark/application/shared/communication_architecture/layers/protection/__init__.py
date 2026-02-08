# Library import
from .. import LayerInterface, ModuleInterface, ModuleContainer
from abc import ABC, abstractmethod
from . import modules
import threading
from typing import List, Optional
from configurations import Configurations, Setting
from datavalue import PrimitiveData
from datapackage import Datapackage

# Constants
LAYER_CONFIGURATIONS: Configurations = Configurations()

# Configure layer configurations
SupportedModulesSetting = Setting(
    value=PrimitiveData(
        data_type=int,
        value=None,
        maximum_length=None, minimum_length=None,
        maximum_size=None, minimum_size=None,
        possible_values=None,
        regular_expression=None,
        data_class=True
    ),
    system_name="SUPPORTED_MODULES",
    symbolic_name="Supported modules",
    description="Specify a limit of supported modules",
    optional=False
)

LAYER_CONFIGURATIONS.add_setting(SupportedModulesSetting)

# Classes definition
class ProtectionLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "PROTECTION"

    def __init__(self, layers_container: object) -> None:
        # Constructor hereditance
        super().__init__(layers_container)

        # Instance properties definition
        self._module_container = ModuleContainer()
        self.loaded_module: Optional[ModuleInterface] = None
        self.layer_settings = LAYER_CONFIGURATIONS

    @property
    def NAME(self) -> str:
        return self.LAYER_NAME

    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        return True
    
    def stop(self) -> bool:
        return True
    
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        return True
    
    def load_module(self, module: ModuleInterface, configurations: object) -> bool:
        self.loaded_module = module(self)
        self.loaded_module.configure(configurations)
        self.loaded_module.start()

        return True
    
    def send(self, device_identifier: int, data: bytes) -> bool:
        print("Enviando datos por la capa de proteccion....")
        if not self.loaded_module: 
            raise RuntimeError("Theres no loaded module to use")

        # 1. Aplicamos la transformación (HTTP, Cifrado, etc.)
        protected_data = self.loaded_module.protect(data)
        
        # 2. Enviamos el paquete resultante mediante el módulo (que ya conoce el transporte)
        return self.loaded_module.write(protected_data)

    def receive(self, device_identifier: int, limit: int, timeout: int) -> bytes:
        print("Recibiendo datos por la capa de proteccion...")
        if not self.loaded_module: 
            raise RuntimeError("Theres no loaded module to use")

        # Extraemos los datos ya "limpios" del buffer del módulo
        return self.loaded_module.read(limit=limit)

    def negotiate(self, role: str, connection_identifier: int) -> Configurations | bool:
        # Get the transport layer
        transport_layer = self.layers_container.query_layer("TRANSPORT")

        # Verify if the connection exists (in the transport layer)
        if connection_identifier not in transport_layer.connections_table:
            raise KeyError(f"The specified connection identifier: {connection_identifier}, not exists in the transport layer connections: {list(transport_layer.connections_table.keys())}")

        datapackages_handler = Datapackage(
            write_function=lambda data, **kwargs: transport_layer.send(connection_identifier, data, **kwargs),
            read_function=transport_layer.receive,
            # CONFIGURACIÓN QUIRÚRGICA: limit=1
            read_arguments=(connection_identifier, 1)
        ) 

        try:
            if role == self.LAYER_ROLE_PASSIVE:
                available_modules = {"AVAILABLE_MODULES": self.query_modules()}
                datapackages_handler.send_datapackage(available_modules)
                residual_data = datapackages_handler._reception_buffer
                print("[ProtectionLayer] Residual data:")
                print(residual_data)
                
                return True

            elif role == self.LAYER_ROLE_ACTIVE:
                # Esperamos el paquete de negociación
                available_modules = datapackages_handler.receive_datapackage(timeout=10)
                residual_data = datapackages_handler._reception_buffer
                print("[ProtectionLayer] Residual data:")
                print(residual_data)
                
                print(f"Modules received: {available_modules}")
                return True
        finally:
            # CRÍTICO: Detener el hilo inmediatamente para liberar el socket
            datapackages_handler.stop()            

class ProtectionModuleInterface(ModuleInterface, ABC):
    # Class properties definition
    CONFIGURATIONS: Configurations = Configurations()
    DeviceIdentifierSetting = Setting(
        value=PrimitiveData(
            data_type=int,
            value=None,
            maximum_length=None, minimum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=None,
            regular_expression=None,
            data_class=True
        ),
        system_name="DEVICE_IDENTIFIER",
        symbolic_name="Device identifier",
        description="Specify which connection is going to be protected",
        optional=False
    )
    CONFIGURATIONS.add_setting(DeviceIdentifierSetting)

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)

        # Instance properties definition
        self._raw_buffer = bytearray()
        self._clean_buffer = bytearray()
        self._lock = threading.Lock()
        self._transport_layer = None
        self._connection_identifier = None
        self.layer = layer

        # Instance properties assignment
        self.configurations = self.CONFIGURATIONS.copy()

    # Public methods
    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

    @abstractmethod
    def configure(self, configurations: object) -> bool: raise NotImplementedError

    @abstractmethod
    def protect(self, data: bytes) -> bytes: raise NotImplementedError

    @abstractmethod
    def unprotect(self, data: bytes) -> bytes: raise NotImplementedError