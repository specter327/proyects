# Library import
from ... import ProtectionModuleInterface
from datavalue import PrimitiveData, ComplexData
from configurations import Configurations
from typing import Tuple
import threading
import time

# Constants definition
ModuleConfigurations = Configurations()
#USER_AGENTS: Tuple[str] = (
#    "",
#    ""
#)

# Classes definition
class ProtectionModule(ProtectionModuleInterface):
    # Class definition properties
    MODULE_NAME: str = "HTTP_PROTECTION"

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)

        # Instance properties assignment
        self.configurations = self.CONFIGURATIONS

        # Instance properties definition
        self._received_data_buffer = bytearray()
        self._clean_data_buffer = bytearray()
        self._active: bool = False
        self.configurated: bool = False
        self._transport_layer = layer.layers_container.query_layer("TRANSPORT")

        # Support routines
        self._read_raw_data_routine_process: threading.Thread = None
    
    # Public methods
    def start(self) -> bool:
        # Set the status active
        self._active = True

        # Launch the read routine
        self._read_raw_data_routine_process = threading.Thread(
            target=self._read_raw_data_routine,
            daemon=True
        )
        self._read_raw_data_routine_process.start()

        return True

    def stop(self) -> bool:
        # Set the status inactive
        self._active = False

        return True

    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.configurated = True
        return True
    
    def write(self, data: bytes) -> bool:
        print("Writed data through the connection:")
        print(data)
        device_identifier = self.configurations.query_setting("DEVICE_IDENTIFIER").value.value
        return self._transport_layer.send(device_identifier, data)

    def read(self, limit: int = None, timeout: int = None) -> bytes:
        with self._lock:
            if not self._clean_data_buffer:
                return b""
            
            end = limit if limit is not None else len(self._clean_data_buffer)
            data = bytes(self._clean_data_buffer[:end])
            del self._clean_data_buffer[:end]
            print("Readed data through the connection:")
            print(data)
            return data
    
    def protect(self, data: bytes) -> bytes:
        header = (
            f"POST /api/v1/sync HTTP/1.1\r\n"
            f"Host: google.com\r\n"
            f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(data)}\r\n"
            f"Connection: keep-alive\r\n"
            f"\r\n"
        ).encode("UTF-8")

        print("Protected data:")
        print(header+data)
        return header + data
    
    def unprotect(self, data: bytes) -> bytes:
        try:
            # Buscamos el delimitador estándar de HTTP \r\n\r\n
            delimiter = b"\r\n\r\n"
            if delimiter in data:
                _, payload = data.split(delimiter, 1)
                return payload
            return data
        except Exception:
            # En caso de datos corruptos o no-HTTP
            return b""
        
    def _read_raw_data_routine(self) -> None:
        transport_layer = self.layer.layers_container.query_layer("TRANSPORT")
        connection_identifier = self.configurations.query_setting("DEVICE_IDENTIFIER").value.value

        while self._active:
            all_raw_data = transport_layer.receive(connection_identifier)

            if all_raw_data:
                # 1. Procesar el HTTP para extraer el payload
                clean_payload = self.unprotect(all_raw_data)
                
                # 2. Almacenar en el buffer de salida
                with self._lock:
                    self._clean_data_buffer.extend(clean_payload)
            else:
                time.sleep(0.1)