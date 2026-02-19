# Library import
from .. import LayerInterface, ModuleInterface, ModuleContainer, LAYER_TYPE_SESSION
from ....utils.logger import logger
from ....utils.debug import smart_debug
from abc import ABC, abstractmethod
from . import modules
import threading
from typing import List, Optional
from configurations import Configurations, Setting
from datavalue import PrimitiveData
from datapackage import Datapackage
import time

# Constants
LAYER_CONFIGURATIONS: Configurations = Configurations()

# Configure layer configurations
DeviceIdentifierSetting = Setting(
    value=PrimitiveData(
        data_type=int,
        value=None,
        maximum_length=None, minimum_length=1,
        maximum_size=None, minimum_size=None,
        possible_values=None,
        regular_expression=None,
        data_class=True
    ),
    system_name="DEVICE_IDENTIFIER",
    symbolic_name="Device identifier",
    description="Specifiy the device communications to protect",
    optional=False
)

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

LAYER_CONFIGURATIONS.add_setting(DeviceIdentifierSetting)
LAYER_CONFIGURATIONS.add_setting(SupportedModulesSetting)

# Classes definition
class ProtectionLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "PROTECTION"
    LAYER_TYPE = LAYER_TYPE_SESSION

    def __init__(self, layers_container: object) -> None:
        # Constructor hereditance
        super().__init__(layers_container)

        # Instance properties definition
        self._module_container = ModuleContainer()
        self.loaded_module: Optional[ModuleInterface] = None
        self.layer_settings = LAYER_CONFIGURATIONS
        self.logger = logger("PROTECTION_LAYER")

    @property
    def NAME(self) -> str:
        return self.LAYER_NAME

    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info("Protection layer initializated")
        return True
    
    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Protection layer finished")
        return True
    
    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.logger.info("Protection layer configurated")
        return True
    
    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def load_module(self, module: ModuleInterface, configurations: object) -> bool:
        self.loaded_module = module(self)
        self.loaded_module.configure(configurations)
        self.loaded_module.start()
        self.logger.info(f"Module loaded: {module}, with configurations: {configurations}, and started")

        return True
    
    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def send(self, device_identifier: int, data: bytes) -> bool:
        print("Enviando datos por la capa de proteccion....")
        self.logger.info(f"Sendind data: {len(data)}, to the connection: {device_identifier}")
        if not self.loaded_module: 
            self.logger.error("Theres no loaded module to use")
            raise RuntimeError("Theres no loaded module to use")

        # 1. Aplicamos la transformación (HTTP, Cifrado, etc.)
        #protected_data = self.loaded_module.protect(data)
        
        # 2. Enviamos el paquete resultante mediante el módulo (que ya conoce el transporte)
        return self.loaded_module.write(data)

    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def receive(self, device_identifier: int, limit: int, timeout: int) -> bytes:
        #print("Recibiendo datos por la capa de proteccion...")
        self.logger.info(f"Receiving data from the connection: {device_identifier}, with limit: {limit}, and timeout: {timeout}")
        if not self.loaded_module: 
            return b""
            raise RuntimeError("Theres no loaded module to use")
        
        #print("[ProtectionLayer] Reading data from the loaded module...")

        # Extraemos los datos ya "limpios" del buffer del módulo
        data_readed = self.loaded_module.read(limit=limit, timeout=timeout)
        if len(data_readed) != 0:
            self.logger.info(f"Data readed: {data_readed}, with length: {len(data_readed)}")
        
        return data_readed

    @smart_debug(element_name="PROTECTION_LAYER", include_args=True, include_result=True)
    def negotiate(self, role: str, connection_identifier: int) -> Configurations | bool:
        # Get the transport layer
        transport_layer = self.layers_container.query_layer("TRANSPORT")

        # Verify if the connection exists (in the transport layer)
        if connection_identifier not in transport_layer.connections_table:
            self.logger.error(f"Error negotiating protection layer: the specified connection identifier: {connection_identifier}, not exists in the transport layer connections: {list(transport_layer.connections_table.keys())}")
            raise KeyError(f"The specified connection identifier: {connection_identifier}, not exists in the transport layer connections: {list(transport_layer.connections_table.keys())}")

        datapackages_handler = Datapackage(
            write_function=lambda data, **kwargs: transport_layer.send(connection_identifier, data, **kwargs),
            read_function=transport_layer.receive,
            read_arguments=(connection_identifier, 1)
        ) 

        self.logger.info(f"Starting negotation with role: {role}, with the connection: {connection_identifier}")

        try:
            if role == self.LAYER_ROLE_PASSIVE:
                available_modules = {"AVAILABLE_MODULES": self.query_modules()}
                datapackages_handler.send_datapackage(available_modules)

                # Receive the module selection
                selected_module = datapackages_handler.receive_datapackage(timeout=180)
                choice_module = selected_module.get("SELECTED_MODULE")

                self.logger.info(f"Available modules: {self.query_modules()}")
                self.logger.info(f"Selected module: {selected_module}")

                print("[Link] Selected module:", choice_module)

                # Get the selected module configurations
                choice_module_configurations = self.query_module(choice_module).CONFIGURATIONS.to_dict()

                # Send the selected module configurations
                selected_module_configurations = {"MODULE_CONFIGURATIONS":choice_module_configurations}
                datapackages_handler.send_datapackage(selected_module_configurations)

                # Receive the personalized settings
                personalized_settings = datapackages_handler.receive_datapackage()
                personalized_settings = Configurations.from_dict(personalized_settings.get("MODULE_CONFIGURATIONS"))

                print("[Link] Personalized settings:")
                print(personalized_settings)

                self.logger.info("Personalized settings received")

                # Set the local module configurations
                self.load_module(
                    module=self.query_module(choice_module),
                    configurations=personalized_settings
                )

                self.logger.info("Module loaded")

                print("[Link] Selected module loaded successfully")

                return True

            elif role == self.LAYER_ROLE_ACTIVE:
                # Esperamos el paquete de negociación
                available_modules = datapackages_handler.receive_datapackage(timeout=10)

                print("[Nexus] Available modules:", available_modules.get("AVAILABLE_MODULES"))
                self.logger.info(f"Available modules: {available_modules.get('AVAILABLE_MODULES')}")

                # Select a module
                module_choice = available_modules["AVAILABLE_MODULES"][1]
                self.logger.info(f"Selected module: {module_choice}")

                # Send the selected module data package
                selected_module = {"SELECTED_MODULE":module_choice}
                datapackages_handler.send_datapackage(selected_module)

                # Get the module configurations
                selected_module_configurations = datapackages_handler.receive_datapackage()
                personalized_settings = Configurations.from_dict(selected_module_configurations.get("MODULE_CONFIGURATIONS"))

                print("[Nexus] Selected module configurations:")
                print(selected_module_configurations)

                # Personalize all the required settings
                for setting in personalized_settings.query_settings():
                    print("Setting:")
                    print(setting)
                
                # Send the personalized settings
                datapackages_handler.send_datapackage({"MODULE_CONFIGURATIONS":personalized_settings.to_dict()})

                self.logger.info("Personalized configurations sended")

                # Set the local module configurations
                self.load_module(
                    module=self.query_module(module_choice),
                    configurations=personalized_settings
                )

                self.logger.info("Selected module loaded")

                print("[Nexus] Selected module loaded successfully")

                return True
        finally:
            datapackages_handler.stop()    
            time.sleep(0.500)        

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