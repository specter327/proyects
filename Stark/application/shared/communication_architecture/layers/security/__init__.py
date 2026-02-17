# Library import
from .. import LayerContainer, LayerInterface, ModuleInterface, ModuleContainer, LAYER_TYPE_SESSION
from ....utils.logger import logger
from . import modules
from abc import ABC, abstractmethod
from configurations import Configurations, Setting
from datavalue import PrimitiveData
from typing import List, Optional
from datapackage import Datapackage
import threading
import traceback

# Constants
LAYER_CONFIGURATIONS: Configurations = Configurations()

# Configure layer settings
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
class SecurityLayer(LayerInterface):
    # Class properties definition
    LAYER_NAME: str = "SECURITY"
    LAYER_TYPE = LAYER_TYPE_SESSION

    def __init__(self, layers_container: object) -> None:
        # Constructor hereditance
        super().__init__(layers_container)

        # Instance properties definition
        self._module_container = ModuleContainer()
        self.loaded_module: Optional[ModuleInterface] = None
        self.layer_settings = LAYER_CONFIGURATIONS
        self.logger = logger("SECURITY_LAYER")

    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info("Security layer initializated")
        return True
    
    def stop(self) -> bool:
        self.logger.info("Security layer stopped")
        return True
    
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.logger.info("Security layer configurated")
        return True
    
    def load_module(self, module: ModuleInterface, configurations: object) -> bool:
        self.loaded_module = module(self)
        self.loaded_module.configure(configurations)
        self.logger.info(f"Security module loaded: {module}, with configurations: {configurations}")
        #self.loaded_module.start()

        return True

    def send(self, device_identifier: int, data: bytes) -> bool:
        print("Enviando datos por la capa de proteccion....")
        self.logger.info(f"Sending data: {len(data)}, to the connection: {device_identifier}")

        if not self.loaded_module: 
            raise RuntimeError("Theres no loaded module to use")
        
        #secured_data = self.loaded_module.secure(data)

        return self.loaded_module.write(data)
    
    def receive(self, device_identifier: int, limit: int, timeout: int) -> bytes:
        #print("Recibiendo datos por la capa de proteccion...")
        if not self.loaded_module: 
            return b""
            raise RuntimeError("Theres no loaded module to use")
        
        # Extraemos los datos ya "limpios" del buffer del módulo
        data_readed = self.loaded_module.read(limit=limit)
        self.logger.info(f"Data received: {data_readed}, with length: {len(data_readed)}, from the connection: {device_identifier}")
        #print("[SecurityLayer] Returned data:")
        #print(data_readed)
        return data_readed 

    def negotiate(self, role: str, connection_identifier: int) -> Configurations | bool:
        # Get the protection layer
        protection_layer = self.layers_container.query_layer("PROTECTION")

        # Create a datapackage handler
        datapackages_handler = Datapackage(
            write_function=lambda data, **kwargs: protection_layer.send(connection_identifier, data, **kwargs),
            read_function=lambda **kwargs: protection_layer.receive(**kwargs),
            read_keyword_arguments={
                "device_identifier":connection_identifier,
                "limit":1,
                "timeout":30
            }
        )

        self.logger.info(f"Negotiating security layer with role: {role}, with the connection: {connection_identifier}")

        try:
            if role == self.LAYER_ROLE_PASSIVE:
                # Send the current local available modules
                datapackages_handler.send_datapackage({"AVAILABLE_MODULES":self.query_modules()})

                # Receive the module selection
                selected_module = datapackages_handler.receive_datapackage(timeout=180)
                choice_module = selected_module.get("SELECTED_MODULE")
                module_instance = self.query_module(choice_module)

                self.logger.info(f"Available modules: {self.query_modules()}")
                self.logger.info(f"Selected module: {choice_module}")

                print("[Link] Selected module:", choice_module)

                # Generate the module configurations
                module_configurations = module_instance.generate_configurations()

                print("Generated configurations:")
                print(module_configurations.to_json())
                self.logger.info("Local configurations generated")
                self.logger.info(f"Negotiating algorithm model: {module_instance.CRYPTOGRAPHIC_MODEL}"
                                 )
                # Configuration exchange
                # Determine the type of negotiation according to the cryptographic model
                if module_instance.CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.ASYMMETRIC_MODEL:
                    print("[Link] Intercambiando claves asimetricas...")

                    # Send the local configurations (protecting the private key)
                    datapackages_handler.send_datapackage({"MODULE_CONFIGURATIONS":module_configurations.to_dict()})
                    self.logger.info("Local asymmetric keys sended")

                    # Receive the remote configurations
                    remote_configurations = Configurations.from_dict(datapackages_handler.receive_datapackage().get("MODULE_CONFIGURATIONS"))
                    self.logger.info("Remote asymmetric keys received")

                    # Set the local module
                    local_configurations = module_configurations.copy()
                    local_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value = module_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value
                    local_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value = remote_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value

                    self.load_module(module_instance, local_configurations)
                    self.logger.info("Module loaded")

                elif module_instance.CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.SIMMETRIC_MODEL:
                    print("[SecurityLayer] Negociando modelo simétrico/transparente...")
                    # Intercambio simple de configuraciones
                    datapackages_handler.send_datapackage({"MODULE_CONFIGURATIONS": module_configurations.to_dict()})
                    self.logger.info("Local symmetric keys sended")
                    remote_pkg = datapackages_handler.receive_datapackage()
                    remote_configurations = Configurations.from_dict(remote_pkg.get("MODULE_CONFIGURATIONS"))
                    self.logger.info("Remote symmetric keys received")

                    # En modelos simétricos, las configuraciones suelen ser espejadas o compartidas
                    self.load_module(module_instance, remote_configurations)
                    self.logger.info("Module loaded")
            
            elif role == self.LAYER_ROLE_ACTIVE:
                # Receive the available modules datapackage
                available_modules = datapackages_handler.receive_datapackage(timeout=10)

                print("[Nexus] Available modules:", available_modules.get("AVAILABLE_MODULES"))
                self.logger.info(f"Available modules: {available_modules.get('AVAILABLE_MODULES')}")

                # Select a module
                module_choice = available_modules["AVAILABLE_MODULES"][0]
                self.logger.info(f"Selected module: {module_choice}")

                # Send the selected module data package
                datapackages_handler.send_datapackage({"SELECTED_MODULE":module_choice})

                # Generate the module configurations
                module_instance = self.query_module(module_choice)
                module_configurations = module_instance.generate_configurations()

                print("Generated configurations:")
                print(module_configurations.to_json())
                self.logger.info(f"Negotating algorithm model: {module_instance.CRYPTOGRAPHIC_MODEL}")

                # Configuration exchange
                # Determine the type of negotiation according to the cryptographic model
                if module_instance.CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.ASYMMETRIC_MODEL:
                    print("[Link] Intercambiando claves asimetricas...")

                    # Send the local configurations (protecting the private key)
                    datapackages_handler.send_datapackage({"MODULE_CONFIGURATIONS":module_configurations.to_dict()})
                    self.logger.info("Local asymmetric keys sended")

                    remote_configurations = Configurations.from_dict(datapackages_handler.receive_datapackage().get("MODULE_CONFIGURATIONS"))
                    self.logger.info("Remote asymmetric keys received")

                    # Set the local module
                    local_configurations = module_configurations.copy()
                    local_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value = module_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value
                    local_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value = remote_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value

                    self.load_module(module_instance, local_configurations)
                    self.logger.info("Module loaded")

                elif module_instance.CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.SIMMETRIC_MODEL:
                    print("[SecurityLayer] Negociando modelo simétrico/transparente...")
                    datapackages_handler.send_datapackage({"MODULE_CONFIGURATIONS": module_configurations.to_dict()})
                    self.logger.info("Local symmetric keys sended")

                    remote_pkg = datapackages_handler.receive_datapackage()
                    remote_configurations = Configurations.from_dict(remote_pkg.get("MODULE_CONFIGURATIONS"))
                    self.logger.info("Remote symmetric keys received")

                    self.load_module(module_instance, remote_configurations)
                    self.logger.info("Module loaded")

            if self.loaded_module:
                self.loaded_module.start()
                self.logger.info("Module started")

        except:
            traceback.print_exc()
            return False

class SecurityModuleInterface(ModuleInterface, ABC):
    # Class properties definition
    CONFIGURATIONS: Configurations = Configurations()
    PrivateEncryptionKeySetting = Setting(
        value=PrimitiveData(
            data_type=bytes,
            value=None,
            maximum_length=None, minimum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=None,
            regular_expression=None,
            data_class=True
        ),
        system_name="PRIVATE_ENCRYPTION_KEY",
        symbolic_name="Private encryption key",
        description="This setting specify the private key to decrypt the received data",
        optional=False,
        private=True
    )

    PublicEncryptionKeySetting = Setting(
        value=PrimitiveData(
            data_type=bytes,
            value=None,
            maximum_length=None, minimum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=None,
            regular_expression=None,
            data_class=True
        ),
        system_name="PUBLIC_ENCRYPTION_KEY",
        symbolic_name="Public encryption key",
        description="This setting specify the public key to encrypt the sended data",
        optional=False
    )

    CONFIGURATIONS.add_setting(PrivateEncryptionKeySetting)
    CONFIGURATIONS.add_setting(PublicEncryptionKeySetting)

    CRYPTOGRAPHIC_MODEL: str = "UNDEFINED"
    ASYMMETRIC_MODEL: str = "ASYMMETRIC"
    SIMMETRIC_MODEL: str = "SIMMETRIC"

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)

        # Instance properties definition
        self._raw_buffer = bytearray()
        self._clean_buffer = bytearray()
        self._lock = threading.Lock()
        self._protection_layer = None
        self._connection_identifier = None
        self._active: bool = False
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
    def secure(self, data: bytes) -> bytes: raise NotImplementedError

    @abstractmethod
    def unsecure(self, data: bytes) -> bytes: raise NotImplementedError

    @abstractmethod
    def generate_configurations(self) -> Configurations: raise NotImplementedError