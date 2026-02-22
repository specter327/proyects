# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .. import LayerContainer, LayerInterface, ModuleInterface, ModuleContainer, LAYER_TYPE_SESSION
from ....utils.logger import logger
from ....utils.debug import smart_debug
from . import modules
from abc import ABC, abstractmethod
from configurations import Configurations, Setting
from datavalue import PrimitiveData
from typing import List, Optional
from datapackage import Datapackage
import threading
import time
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
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def query_modules(self) -> List[str]:
        return self._module_container.query_modules()
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def query_module(self, module_name: str) -> ModuleInterface | None:
        return self._module_container.query_module(module_name)

    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def start(self) -> bool:
        self._module_container.load_modules(package=modules.__package__)
        self.logger.info("Security layer initializated")
        return True
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Security layer stopped")
        return True
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.logger.info("Security layer configurated")
        return True
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def load_module(self, module: ModuleInterface, configurations: object) -> bool:
        self.loaded_module = module(self)
        self.loaded_module.configure(configurations)
        self.logger.info(f"Security module loaded: {module}, with configurations: {configurations}")
        self.loaded_module.start()

        return True

    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def send(self, device_identifier: int, data: bytes) -> bool:
        print("Enviando datos por la capa de proteccion....")
        self.logger.info(f"Sending data: {len(data)}, to the connection: {device_identifier}")

        if not self.loaded_module: 
            raise RuntimeError("Theres no loaded module to use")
        
        #secured_data = self.loaded_module.secure(data)

        return self.loaded_module.write(data)
    
    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def receive(self, device_identifier: int, limit: int, timeout: int) -> bytes:
        #print("Recibiendo datos por la capa de proteccion...")
        if not self.loaded_module:
            self.logger.warning(f"Theres no module loaded for the connection: {device_identifier}") 
            return b""
            raise RuntimeError("Theres no loaded module to use")
        
        # Extraemos los datos ya "limpios" del buffer del módulo
        self.logger.info(f"Requesting data to the connection: {device_identifier}, with limit: {limit}, and timeout: {timeout}")

        data_readed = self.loaded_module.read(limit=limit, timeout=timeout)
        self.logger.info(f"Data received: {data_readed}, with length: {len(data_readed)}, from the connection: {device_identifier}")
        #print("[SecurityLayer] Returned data:")
        #print(data_readed)
        return data_readed

    @smart_debug(element_name="SECURITY_LAYER", include_args=True, include_result=True)
    def negotiate(self, role: str, connection_identifier: int) -> bool:
        protection_layer = self.layers_container.query_layer("PROTECTION")

        # 1. Handler inicial (Fase 1)
        handler = Datapackage(
            write_function=lambda data, **kwargs: protection_layer.send(connection_identifier, data, **kwargs),
            read_function=lambda **kwargs: protection_layer.receive(**kwargs),
            read_keyword_arguments={"device_identifier": connection_identifier, "limit": 1, "timeout": 30}
        )

        try:
            # --- FASE 1: NEGOCIACIÓN ASIMÉTRICA ---
            self.logger.info("Iniciando Fase 1: Asimétrica")
            asymmetric_modules = [m for m in self.query_modules() if self.query_module(m).CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.ASYMMETRIC_MODEL]
            
            if role == self.LAYER_ROLE_PASSIVE:
                handler.send_datapackage({"AVAILABLE_ASYMMETRIC": asymmetric_modules})
                pkg = handler.receive_datapackage(timeout=30)
                if not pkg: raise ConnectionError("Timeout Fase 1 (List)")
                choice = pkg.get("SELECTED_MODULE")
            else:
                pkg = handler.receive_datapackage(timeout=30)
                if not pkg: raise ConnectionError("Timeout Fase 1 (Choice)")
                remote_asym = pkg.get("AVAILABLE_ASYMMETRIC")
                choice = remote_asym[0] 
                handler.send_datapackage({"SELECTED_MODULE": choice})

            asym_module_instance = self.query_module(choice)
            asym_configs = asym_module_instance.generate_configurations()
            
            handler.send_datapackage({"MODULE_CONFIGURATIONS": asym_configs.to_dict()})
            pkg_configs = handler.receive_datapackage(timeout=30)
            if not pkg_configs: raise ConnectionError("Timeout Fase 1 (Configs)")
            remote_asym_configs = Configurations.from_dict(pkg_configs.get("MODULE_CONFIGURATIONS"))
            
            # --- CRÍTICO: LIMPIEZA Y CARGA ---
            handler.stop() 
            time.sleep(0.5) # Tiempo para que el SO procese el cierre del hilo de lectura anterior
            self.logger.debug(f"Datos remanentes en el manejador de paquetes (DataPackage): {handler._reception_buffer}")

            local_asym_cfg = asym_configs.copy()
            local_asym_cfg.query_setting("PRIVATE_ENCRYPTION_KEY").value.value = asym_configs.query_setting("PRIVATE_ENCRYPTION_KEY").value.value
            local_asym_cfg.query_setting("PUBLIC_ENCRYPTION_KEY").value.value = remote_asym_configs.query_setting("PUBLIC_ENCRYPTION_KEY").value.value
            
            self.load_module(asym_module_instance, local_asym_cfg)
            self.logger.info(f"Módulo RSA cargado. Limpiando buffers...")

            # --- FASE 2: HANDSHAKE DE ALINEACIÓN (DENTRO DE RSA) ---
            # Este es el punto que estaba fallando. Creamos un nuevo handler cifrado.
            secure_handler = Datapackage(
                write_function=lambda data, **kwargs: self.send(connection_identifier, data),
                read_function=lambda **kwargs: self.receive(**kwargs),
                read_keyword_arguments={"device_identifier": connection_identifier, "limit": 4096, "timeout": 30}
            )

            # Sincronización explícita: "READY"
            if role == self.LAYER_ROLE_PASSIVE:
                secure_handler.send_datapackage({"SIGNAL": "READY_FOR_SIMMETRIC"})
                pkg_sig = secure_handler.receive_datapackage(timeout=45)
                if not pkg_sig or pkg_sig.get("SIGNAL") != "READY_FOR_SIMMETRIC":
                    raise ConnectionError("Falla de sincronización en canal cifrado")
            else:
                pkg_sig = secure_handler.receive_datapackage(timeout=45)
                if not pkg_sig or pkg_sig.get("SIGNAL") != "READY_FOR_SIMMETRIC":
                    raise ConnectionError("Falla de sincronización en canal cifrado")
                secure_handler.send_datapackage({"SIGNAL": "READY_FOR_SIMMETRIC"})

            # --- FASE 3: NEGOCIACIÓN SIMÉTRICA ---
            self.logger.info("Iniciando negociación de llave simétrica...")
            symmetric_modules = [m for m in self.query_modules() if self.query_module(m).CRYPTOGRAPHIC_MODEL == SecurityModuleInterface.SIMMETRIC_MODEL]

            if role == self.LAYER_ROLE_PASSIVE:
                secure_handler.send_datapackage({"AVAILABLE_SYMMETRIC": symmetric_modules})
                pkg = secure_handler.receive_datapackage(timeout=45)
                sym_choice = pkg.get("SELECTED_MODULE")
                pkg_sym_configs = secure_handler.receive_datapackage(timeout=45)
                sym_configs = Configurations.from_dict(pkg_sym_configs.get("MODULE_CONFIGURATIONS"))
            else:
                pkg = secure_handler.receive_datapackage(timeout=45)
                remote_sym = pkg.get("AVAILABLE_SYMMETRIC")
                sym_choice = remote_sym[0]
                secure_handler.send_datapackage({"SELECTED_MODULE": sym_choice})
                sym_module_instance = self.query_module(sym_choice)
                sym_configs = sym_module_instance.generate_configurations()
                secure_handler.send_datapackage({"MODULE_CONFIGURATIONS": sym_configs.to_dict()})

            # --- FASE 4: PROMOCIÓN ATÓMICA ---
            secure_handler.stop()
            time.sleep(0.5)
            self.logger.debug(f"Datos remanentes en el manejador de paquetes (DataPackage): {secure_handler._reception_buffer}")
            if self.loaded_module: self.loaded_module.stop()
            
            time.sleep(0.2) # Estabilización final
            sym_module_class = self.query_module(sym_choice)
            self.load_module(sym_module_class, sym_configs)
            
            self.logger.info("Promoción exitosa a canal simétrico.")
            return True

        except Exception as e:
            self.logger.error(f"Error crítico: {e}")
            if 'handler' in locals(): handler.stop()
            if 'secure_handler' in locals(): secure_handler.stop()
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