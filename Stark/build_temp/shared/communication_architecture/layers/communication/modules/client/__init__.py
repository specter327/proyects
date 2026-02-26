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
            "DATA_TYPE": "list",
            "NAME": "Server Collection",
            "DESCRIPTION": None,
            "VALUE": None,
            "MAXIMUM_LENGTH": None,
            "MINIMUM_LENGTH": 1,
            "POSSIBLE_VALUES": [
                {
                    "__type__": "ComplexData",
                    "content": {
                        "DATA_TYPE": "dict",
                        "NAME": "INTERNET Profile",
                        "DESCRIPTION": None,
                        "VALUE": None,
                        "MAXIMUM_LENGTH": None,
                        "MINIMUM_LENGTH": None,
                        "POSSIBLE_VALUES": {
                            "TRANSPORT": [
                                "INTERNET"
                            ],
                            "ADDRESSES": {
                                "__type__": "ComplexData",
                                "content": {
                                    "DATA_TYPE": "list",
                                    "NAME": "IP List",
                                    "DESCRIPTION": None,
                                    "VALUE": None,
                                    "MAXIMUM_LENGTH": None,
                                    "MINIMUM_LENGTH": 1,
                                    "POSSIBLE_VALUES": [
                                        {
                                            "__type__": "ComplexData",
                                            "content": {
                                                "DATA_TYPE": "dict",
                                                "NAME": "IP Endpoint",
                                                "DESCRIPTION": None,
                                                "VALUE": None,
                                                "MAXIMUM_LENGTH": None,
                                                "MINIMUM_LENGTH": None,
                                                "POSSIBLE_VALUES": {
                                                    "ADDRESS": [
                                                        {
                                                            "__type__": "PrimitiveData",
                                                            "content": {
                                                                "DATA_TYPE": "str",
                                                                "VALUE": None,
                                                                "NAME": "IPv4 address",
                                                                "DESCRIPTION": "IPv4 address",
                                                                "MAXIMUM_LENGTH": 15,
                                                                "MINIMUM_LENGTH": 7,
                                                                "MAXIMUM_SIZE": None,
                                                                "MINIMUM_SIZE": None,
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
                                                                "NAME": "IPv6 address",
                                                                "DESCRIPTION": "IPv6 address",
                                                                "MAXIMUM_LENGTH": 39,
                                                                "MINIMUM_LENGTH": 2,
                                                                "MAXIMUM_SIZE": None,
                                                                "MINIMUM_SIZE": None,
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
                                                                "NAME": "Domain name",
                                                                "DESCRIPTION": "Domain name",
                                                                "MAXIMUM_LENGTH": None,
                                                                "MINIMUM_LENGTH": None,
                                                                "MAXIMUM_SIZE": None,
                                                                "MINIMUM_SIZE": None,
                                                                "POSSIBLE_VALUES": None,
                                                                "REGULAR_EXPRESSION": "^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}$",
                                                                "DATA_CLASS": True,
                                                                "__type__": "PrimitiveData"
                                                            }
                                                        }
                                                    ],
                                                    "PORT": [
                                                        {
                                                            "__type__": "PrimitiveData",
                                                            "content": {
                                                                "DATA_TYPE": "int",
                                                                "VALUE": None,
                                                                "NAME": "Internet port",
                                                                "DESCRIPTION": "Internet port on the range from: 1, to: 65,535",
                                                                "MAXIMUM_LENGTH": None,
                                                                "MINIMUM_LENGTH": None,
                                                                "MAXIMUM_SIZE": 65535,
                                                                "MINIMUM_SIZE": 1,
                                                                "POSSIBLE_VALUES": None,
                                                                "REGULAR_EXPRESSION": None,
                                                                "DATA_CLASS": True,
                                                                "__type__": "PrimitiveData"
                                                            }
                                                        }
                                                    ]
                                                },
                                                "DATA_CLASS": True,
                                                "__type__": "ComplexData"
                                            }
                                        }
                                    ],
                                    "DATA_CLASS": True,
                                    "__type__": "ComplexData"
                                }
                            }
                        },
                        "DATA_CLASS": True,
                        "__type__": "ComplexData"
                    }
                },
                {
                    "__type__": "ComplexData",
                    "content": {
                        "DATA_TYPE": "dict",
                        "NAME": "BLUETOOTH Profile",
                        "DESCRIPTION": None,
                        "VALUE": None,
                        "MAXIMUM_LENGTH": None,
                        "MINIMUM_LENGTH": None,
                        "POSSIBLE_VALUES": {
                            "TRANSPORT": [
                                "BLUETOOTH"
                            ],
                            "ADDRESSES": {
                                "__type__": "ComplexData",
                                "content": {
                                    "DATA_TYPE": "list",
                                    "NAME": "BT List",
                                    "DESCRIPTION": None,
                                    "VALUE": None,
                                    "MAXIMUM_LENGTH": None,
                                    "MINIMUM_LENGTH": 1,
                                    "POSSIBLE_VALUES": [
                                        {
                                            "__type__": "ComplexData",
                                            "content": {
                                                "DATA_TYPE": "dict",
                                                "NAME": "BT Endpoint",
                                                "DESCRIPTION": None,
                                                "VALUE": None,
                                                "MAXIMUM_LENGTH": None,
                                                "MINIMUM_LENGTH": None,
                                                "POSSIBLE_VALUES": {
                                                    "ADDRESS": [
                                                        {
                                                            "__type__": "PrimitiveData",
                                                            "content": {
                                                                "DATA_TYPE": "str",
                                                                "VALUE": None,
                                                                "NAME": "MAC address",
                                                                "DESCRIPTION": "MAC address",
                                                                "MAXIMUM_LENGTH": None,
                                                                "MINIMUM_LENGTH": None,
                                                                "MAXIMUM_SIZE": 17,
                                                                "MINIMUM_SIZE": 17,
                                                                "POSSIBLE_VALUES": None,
                                                                "REGULAR_EXPRESSION": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
                                                                "DATA_CLASS": True,
                                                                "__type__": "PrimitiveData"
                                                            }
                                                        }
                                                    ],
                                                    "PORT": [
                                                        {
                                                            "__type__": "PrimitiveData",
                                                            "content": {
                                                                "DATA_TYPE": "int",
                                                                "VALUE": None,
                                                                "NAME": "Internet port",
                                                                "DESCRIPTION": "Internet port on the range from: 1, to: 65,535",
                                                                "MAXIMUM_LENGTH": None,
                                                                "MINIMUM_LENGTH": None,
                                                                "MAXIMUM_SIZE": 65535,
                                                                "MINIMUM_SIZE": 1,
                                                                "POSSIBLE_VALUES": None,
                                                                "REGULAR_EXPRESSION": None,
                                                                "DATA_CLASS": True,
                                                                "__type__": "PrimitiveData"
                                                            }
                                                        }
                                                    ]
                                                },
                                                "DATA_CLASS": True,
                                                "__type__": "ComplexData"
                                            }
                                        }
                                    ],
                                    "DATA_CLASS": True,
                                    "__type__": "ComplexData"
                                }
                            }
                        },
                        "DATA_CLASS": True,
                        "__type__": "ComplexData"
                    }
                }
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
IPv4AddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    name="IPv4 address",
    description="IPv4 address",
    maximum_length=15, 
    minimum_length=7,
    maximum_size=None, 
    minimum_size=None,
    possible_values=None,
    # Valida 4 grupos de 0-255 separados por puntos
    regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
    data_class=True
)

IPv6AddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    name="IPv6 address",
    description="IPv6 address",
    maximum_length=39, 
    minimum_length=2,
    maximum_size=None, 
    minimum_size=None, # Corresponde a '::'
    possible_values=None,
    # Soporta direcciones completas y abreviadas (RFC 4291)
    regular_expression=r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",
    data_class=True
)

MACAddressSchema = PrimitiveData(
    data_type=str,
    value=None,
    name="MAC address",
    description="MAC address",
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
    name="Domain name",
    description="Domain name",
    regular_expression=r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$",
    data_class=True
)

InternetPortSchema = PrimitiveData(
    data_type=int,
    value=None,
    name="Internet port",
    description="Internet port on the range from: 1, to: 65,535",
    maximum_length=None, minimum_length=None,
    maximum_size=65535, minimum_size=1,
    possible_values=None,
    regular_expression=None,
    data_class=True
)

InternetAddrSchema = ComplexData(
    data_type=dict, 
    value=None,
    name="IP Endpoint", 
    possible_values={
        "ADDRESS": [IPv4AddressSchema, IPv6AddressSchema, DomainNameSchema], 
        "PORT": [InternetPortSchema]
    },
    data_class=True
)

BluetoothAddrSchema = ComplexData(
    data_type=dict,
    value=None,
    name="BT Endpoint", 
    possible_values={
        "ADDRESS": [MACAddressSchema], 
        "PORT": [InternetPortSchema] # O un esquema específico para canales BT
    },
    data_class=True
)

# --- Perfiles con Auto-Inferencia de TRANSPORT ---
InternetProfile = ComplexData(
    data_type=dict, 
    value=None,
    name="INTERNET Profile",
    possible_values={
        "TRANSPORT": ["INTERNET"],  # Al ser lista de 1, cli_capture lo auto-asigna
        "ADDRESSES": ComplexData(
            data_type=list, 
            value=None,
            name="IP List", 
            maximum_length=None, minimum_length=1,
            possible_values=(InternetAddrSchema,),
            data_class=True
        )
    },
    data_class=True
)

BluetoothProfile = ComplexData(
    data_type=dict, 
    value=None,
    name="BLUETOOTH Profile", 
    possible_values={
        "TRANSPORT": ["BLUETOOTH"],
        "ADDRESSES": ComplexData(
            data_type=list, 
            value=None,
            name="BT List", 
            maximum_length=None, minimum_length=1,
            possible_values=(BluetoothAddrSchema,),
            data_class=True
        )
    },
    data_class=True
)

# --- Esquema de Alto Nivel ---
ServerProfilesSchema = ComplexData(
    data_type=list,
    value=None,
    name="Server Collection", 
    maximum_length=None, minimum_length=1,
    possible_values=(InternetProfile, BluetoothProfile), # Aquí se elije el tipo de perfil
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
    CONFIGURATIONS: Configurations = ModuleConfigurations

    def __init__(self, layer) -> None:
        super().__init__(layer)
        self.logger = logger(self.MODULE_NAME)
        # self.layer referencia a CommunicationLayer
        self._transport_layer = self.layer.layers_container.query_layer("TRANSPORT")
        self._config_manager = ConfigurationsManager()
        
        self._active: bool = False
        self._orchestrator_thread: Optional[threading.Thread] = None
        
        # Mapeo: { connection_id: session_uuid }
        self._active_sessions: Dict[int, str] = {}
        self._lock = threading.Lock()

    # Private methods
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def _connection_orchestrator(self) -> None:
        """Rutina de alto nivel: Conectar -> Negociar Sesión -> Mantener."""
        self.logger.info("Starting connection orchestrator")

        while self._active:
            # 1. Limpieza de sesiones huérfanas
            self._maintain_sessions()

            # 2. Obtener configuración inyectada por LinkBuilder
            # Usamos el FQN para precisar el recurso en la tabla
            resource_id = "shared.communication_architecture.layers.communication.modules.client"
            config_data = self._config_manager.query_configuration(resource_id)
            self.logger.debug(f"Configurations query result: {config_data}")
            profiles = config_data.get("SERVER_PROFILES", {}).get("VALUE", [])

            for profile in profiles:
                self.logger.debug(f"Server profile: {profile}")
                transport_type = profile.get("TRANSPORT")
                endpoints = profile.get("ADDRESSES", [])

                for endpoint in endpoints:
                    self.logger.debug(f"Endpoint: {endpoint}")
                    if not self._active: break
                    
                    addr, port = endpoint.get("ADDRESS"), endpoint.get("PORT")

                    # Evitar duplicidad si ya existe una sesión para este endpoint
                    if self._session_exists_for_endpoint(addr, port):
                        continue

                    # 3. Intento de conexión en Capa de Transporte
                    self.logger.debug(f"Requesting connection with address: {addr}, and port: {port}")
                    conn_id = self._establish_transport_connection(transport_type, addr, port)
                    self.logger.debug(f"Connection result: {conn_id}")

                    if conn_id:
                        # 4. Elevación a Capa de Comunicación (Creación de Sesión)
                        # El local_role se define como 'CLIENT' para este módulo
                        session_id = self.layer.create_session(conn_id, local_role="CLIENT")
                        self.logger.debug(f"Session identifier: {session_id}")

                        if session_id:
                            with self._lock:
                                self._active_sessions[conn_id] = session_id
                            self.logger.info(f"Established Session {session_id} for Connection {conn_id}")
                        else:
                            # Si la sesión falla, cerramos el transporte para evitar leaks
                            self._transport_layer.disconnect(conn_id)

            time.sleep(20)

        self.logger.info("Stopping connection orchestrator")


    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def _establish_transport_connection(self, transport_type: str, addr: str, port: int) -> Optional[int]:
        """Interactúa con TransportLayer para obtener un connection_id."""
        # Buscar módulo de transporte compatible (TCP_IP, etc)
        self.logger.debug(f"Establishing a transport connection")
        available = self._transport_layer.query_modules()
        target_mod_name = None
        
        for name in available:
            mod_class = self._transport_layer.query_module(name)
            if getattr(mod_class, "TRANSPORT_TYPE", None) == transport_type:
                target_mod_name = name
                break
        
        if not target_mod_name:
            return None

        # Preparar configuración efímera para el transporte
        # Se obtiene el blueprint y se inyectan los valores del endpoint
        transport_class = self._transport_layer.query_module(target_mod_name)
        conn_configs = transport_class.CONFIGURATIONS.copy()
        
        # Inyección dinámica de parámetros
        conn_configs.query_setting("REMOTE_ADDRESS").value.value = addr
        conn_configs.query_setting("REMOTE_PORT").value.value = port

        # Solicitar conexión a la capa de transporte
        return self._transport_layer.connect(target_mod_name, conn_configs)

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def _maintain_sessions(self) -> None:
        """Verifica si las conexiones de transporte siguen vivas."""
        with self._lock:
            to_remove = []
            for conn_id, session_id in self._active_sessions.items():
                # Consultar a la TransportLayer si el ID sigue activo
                if conn_id not in self._transport_layer.connections_table:
                    self.logger.warning(f"Connection {conn_id} lost. Invalidating session {session_id}.")
                    self.layer.stop_session(session_id)
                    to_remove.append(conn_id)
            
            for cid in to_remove:
                del self._active_sessions[cid]

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def _session_exists_for_endpoint(self, addr: str, port: int) -> bool:
        """Verifica si el endpoint ya tiene una sesión activa mapeada."""
        with self._lock:
            for conn_id in self._active_sessions.keys():
                conn_mod = self._transport_layer.connections_table.get(conn_id)
                if conn_mod:
                    # Acceso a los settings del módulo de transporte activo
                    c_addr = conn_mod.configurations.query_setting("REMOTE_ADDRESS").value.value
                    c_port = conn_mod.configurations.query_setting("REMOTE_PORT").value.value
                    if c_addr == addr and c_port == port:
                        return True
        return False

    # Public methods
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        self.logger.info("Starting module")
        self._set_active(active=True)

        self._connection_orchestrator = threading.Thread(
            target=self._connection_orchestrator,
            daemon=False
        )
        self._connection_orchestrator.start()

        self.logger.info("Module successfully started")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        self.logger.info("Stopping module")
        self._set_active(active=False)

        self.logger.info("Module stopped successfully")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.logger.info("Configurating module")
        self.configurations = configurations
        self._set_configurated(configurated=True)

        self.logger.info("Module configurated successfully")
        return True