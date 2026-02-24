# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__SELECTABLE__ = True
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__CONFIGURABLE__ = True
__STATIC_CONFIGURATIONS__ = {
    "SERVER_PROFILES": {
        "SYSTEM_NAME": "SERVER_PROFILES",
        "SYMBOLIC_NAME": "Server profiles",
        "DESCRIPTION": "It includes a list of ServerProfile instances, with information to search it to establish a connection",
        "VALUE": {
            "DATA_TYPE": "dict",
            "VALUE": None,
            "MAXIMUM_LENGTH": None,
            "MINIMUM_LENGTH": None,
            "POSSIBLE_VALUES": [
                [
                    "TRANSPORT",
                    "ADDRESSES"
                ],
                [
                    "INTERNET",
                    "BLUETOOTH",
                    "SERIAL",
                    {
                        "__type__": "ComplexData",
                        "content": {
                            "DATA_TYPE": "list",
                            "VALUE": None,
                            "MAXIMUM_LENGTH": None,
                            "MINIMUM_LENGTH": 1,
                            "POSSIBLE_VALUES": [
                                {
                                    "__type__": "ComplexData",
                                    "content": {
                                        "DATA_TYPE": "dict",
                                        "VALUE": None,
                                        "MAXIMUM_LENGTH": None,
                                        "MINIMUM_LENGTH": 1,
                                        "POSSIBLE_VALUES": [
                                            [
                                                "ADDRESS",
                                                "PORT"
                                            ],
                                            [
                                                {
                                                    "__type__": "PrimitiveData",
                                                    "content": {
                                                        "DATA_TYPE": "str",
                                                        "VALUE": None,
                                                        "MAXIMUM_LENGTH": None,
                                                        "MINIMUM_LENGTH": None,
                                                        "MAXIMUM_SIZE": 15,
                                                        "MINIMUM_SIZE": 7,
                                                        "POSSIBLE_VALUES": None,
                                                        "REGULAR_EXPRESSION": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                                                        "DATA_CLASS": True,
                                                        "__type__": "PrimitiveData"
                                                    }
                                                },
                                                {
                                                    "__type__": "PrimitiveData",
                                                    "content": {
                                                        "DATA_TYPE": "str",
                                                        "VALUE": None,
                                                        "MAXIMUM_LENGTH": None,
                                                        "MINIMUM_LENGTH": None,
                                                        "MAXIMUM_SIZE": 39,
                                                        "MINIMUM_SIZE": 2,
                                                        "POSSIBLE_VALUES": None,
                                                        "REGULAR_EXPRESSION": "^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",
                                                        "DATA_CLASS": True,
                                                        "__type__": "PrimitiveData"
                                                    }
                                                },
                                                {
                                                    "__type__": "PrimitiveData",
                                                    "content": {
                                                        "DATA_TYPE": "str",
                                                        "VALUE": None,
                                                        "MAXIMUM_LENGTH": None,
                                                        "MINIMUM_LENGTH": None,
                                                        "MAXIMUM_SIZE": 17,
                                                        "MINIMUM_SIZE": 17,
                                                        "POSSIBLE_VALUES": None,
                                                        "REGULAR_EXPRESSION": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
                                                        "DATA_CLASS": True,
                                                        "__type__": "PrimitiveData"
                                                    }
                                                },
                                                {
                                                    "__type__": "PrimitiveData",
                                                    "content": {
                                                        "DATA_TYPE": "str",
                                                        "VALUE": None,
                                                        "MAXIMUM_LENGTH": None,
                                                        "MINIMUM_LENGTH": None,
                                                        "MAXIMUM_SIZE": None,
                                                        "MINIMUM_SIZE": None,
                                                        "POSSIBLE_VALUES": None,
                                                        "REGULAR_EXPRESSION": "^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}$",
                                                        "DATA_CLASS": True,
                                                        "__type__": "PrimitiveData"
                                                    }
                                                },
                                                {
                                                    "__type__": "PrimitiveData",
                                                    "content": {
                                                        "DATA_TYPE": "int",
                                                        "VALUE": None,
                                                        "MAXIMUM_LENGTH": 65535,
                                                        "MINIMUM_LENGTH": 1,
                                                        "MAXIMUM_SIZE": None,
                                                        "MINIMUM_SIZE": None,
                                                        "POSSIBLE_VALUES": None,
                                                        "REGULAR_EXPRESSION": None,
                                                        "DATA_CLASS": True,
                                                        "__type__": "PrimitiveData"
                                                    }
                                                }
                                            ]
                                        ],
                                        "DATA_CLASS": True,
                                        "__type__": "ComplexData"
                                    }
                                }
                            ],
                            "DATA_CLASS": True,
                            "__type__": "ComplexData"
                        }
                    }
                ]
            ],
            "DATA_CLASS": True,
            "__type__": "ComplexData"
        },
        "OPTIONAL": False,
        "PRIVATE": False
    }
}

# Constants definition
ADDRESS_PROFILE = {
    "ADDRESS":str,
    "PORT":int
}

SERVER_PROFILE = {
    "TRANSPORT":str,
    "ADDRESSES":[]
}

# Library import
from .... import ModuleInterface
from ......utils.logger import logger
from ......utils.debug import smart_debug
from configurations import Configurations, Setting
from datavalue import PrimitiveData, ComplexData
from system.configurations import ConfigurationsManager
from typing import Optional
import threading
import time

# Constants definition
PrimitiveData()
IPv4AddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=None, 
    minimum_length=None,
    maximum_size=15, 
    minimum_size=7,
    possible_values=None,
    # Valida 4 grupos de 0-255 separados por puntos
    regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    data_class=True
)

IPv6AddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=None, 
    minimum_length=None,
    maximum_size=39, 
    minimum_size=2, # Corresponde a '::'
    possible_values=None,
    # Soporta direcciones completas y abreviadas (RFC 4291)
    regular_expression=r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",
    data_class=True
)

MACAddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=None, 
    minimum_length=None,
    maximum_size=17, 
    minimum_size=17,
    possible_values=None,
    # Valida formato XX:XX:XX:XX:XX:XX o XX-XX-XX-XX-XX-XX
    regular_expression=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
    data_class=True
)

DomainNameSchema = PrimitiveData(
    data_type=str,
    value=None,
    regular_expression=r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$",
    data_class=True
)

InternetPortSchema = PrimitiveData(
    data_type=int,
    value=None,
    maximum_length=65535, minimum_length=1,
    maximum_size=None, minimum_size=None,
    possible_values=None,
    data_class=True
)

AddressSchema = ComplexData(
    data_type=dict,
    value=None,
    maximum_length=None, minimum_length=1,
    possible_values=(("ADDRESS", "PORT"), (IPv4AddressSchema, IPv6AddressSchema, MACAddressSchema, DomainNameSchema, InternetPortSchema)),
    data_class=True
)
AddressesSchema = ComplexData(
    data_type=list,
    value=None,
    maximum_length=None, minimum_length=1,
    possible_values=(AddressSchema, ),
    data_class=True
)

ServerProfileSchema = ComplexData(
    data_type=dict,
    value=None,
    maximum_length=None, minimum_length=None,
    possible_values=(("TRANSPORT", "ADDRESSES"), ("INTERNET", "BLUETOOTH", "SERIAL", AddressesSchema)),
    data_class=True
)

ServerProfilesSchema = ComplexData(
    data_type=list,
    value=None,
    minimum_length=1,
    possible_values=(ServerProfileSchema, ),
    data_class=True
)

ModuleConfigurations = Configurations()
ServerProfilesSetting = Setting(
    value=ServerProfilesSchema,
    system_name="SERVER_PROFILES",
    symbolic_name="Server profiles",
    description="It includes a list of ServerProfile instances, with information to search it to establish a connection",
    optional=False
)

ModuleConfigurations.add_setting(ServerProfilesSetting)

print(ModuleConfigurations.to_json())

# Classes definition
class CommunicationClient(ModuleInterface):
    MODULE_NAME = "COMMUNICATION_CLIENT"
    
    def __init__(self, layer) -> None:
        super().__init__(layer)
        self.logger = logger(self.MODULE_NAME)
        self._transport_layer = layer.layers_container.query_layer("TRANSPORT")
        self._config_manager = ConfigurationsManager()
        
        self._active = False
        self._worker_thread: Optional[threading.Thread] = None
        self._established_connections = []

    def start(self) -> bool:
        if self._active:
            return True
        
        self._active = True
        self._worker_thread = threading.Thread(target=self._connection_orchestrator, daemon=True)
        self._worker_thread.start()
        self.logger.info("CommunicationClient background routine started")
        return True

    def _connection_orchestrator(self) -> None:
        """Rutina proactiva de búsqueda y establecimiento de conexiones."""
        while self._active:
            # 1. Obtener la configuración global de perfiles
            config_data = self._config_manager.query_configuration("SERVER_PROFILES")
            if not config_data or "VALUE" not in config_data:
                self.logger.error("SERVER_PROFILES configuration not found or invalid")
                time.sleep(10)
                continue

            # Extraemos la lista de perfiles (ServerProfileSchema)
            # Nota: Dependiendo de tu implementación de Setting, accedemos al valor real
            profiles = config_data["VALUE"].get("VALUE", [])
            if not isinstance(profiles, list): profiles = [profiles]

            for profile in profiles:
                transport_target = profile.get("TRANSPORT")
                addresses = profile.get("ADDRESSES", [])

                # 2. Localizar un módulo de transporte compatible
                available_module_names = self._transport_layer.query_modules()
                target_module = None

                for mod_name in available_module_names:
                    mod_class = self._transport_layer.query_module(mod_name)
                    if getattr(mod_class, "TRANSPORT_TYPE", None) == transport_target:
                        target_module = mod_class
                        break

                if not target_module:
                    self.logger.warning(f"No module found for transport: {transport_target}")
                    continue

                # 3. Intentar conexión a cada dirección definida en el perfil
                for endpoint in addresses:
                    addr = endpoint.get("ADDRESS")
                    port = endpoint.get("PORT")

                    # Evitamos reconexiones redundantes si ya existe (Lógica simplificada)
                    if self._is_already_connected(addr, port):
                        continue

                    self.logger.info(f"Attempting connection to {addr}:{port} via {transport_target}")
                    
                    # Clonamos la configuración del módulo para inyectar parámetros
                    conn_configs = target_module.CONFIGURATIONS.copy()
                    conn_configs.query_setting("REMOTE_ADDRESS").value.value = addr
                    conn_configs.query_setting("REMOTE_PORT").value.value = port

                    # Ejecutamos la conexión a través de la capa de transporte
                    connection_id = self._transport_layer.connect(target_module, conn_configs)

                    if connection_id:
                        self.logger.info(f"Success! ID: {connection_id} -> {addr}:{port}")
                        self._established_connections.append({
                            "id": connection_id, 
                            "address": addr, 
                            "port": port
                        })
            
            time.sleep(30) # Intervalo de re-escaneo de perfiles

    def _is_already_connected(self, address, port) -> bool:
        return any(c['address'] == address and c['port'] == port for c in self._established_connections)

    def stop(self) -> bool:
        self._active = False
        return True