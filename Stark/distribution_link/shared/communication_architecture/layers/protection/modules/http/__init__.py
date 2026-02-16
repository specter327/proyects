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
    CONFIGURATIONS: Configurations = Configurations()

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
        print("[ProtectionModule] Writed data through the connection:")
        print(data)
        protected_data = self.protect(data)
        
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        return self._transport_layer.send(device_identifier, protected_data)

    def read(self, limit: int = None, timeout: int = None) -> bytes:
        with self._lock:
            if not self._clean_data_buffer:
                return b""
            
            end = limit if limit is not None else len(self._clean_data_buffer)
            data = bytes(self._clean_data_buffer[:end])
            del self._clean_data_buffer[:end]
            #print("[ProtectionModule] Readed data through the connection:")
            #print(data)
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

        print("[ProtectionModule] Protected data:")
        print(header+data)
        return header + data
    
    def unprotect(self, data: bytes) -> bytes:
        try:
            # Buscamos el delimitador estándar de HTTP \r\n\r\n
            delimiter = b"\r\n\r\n"
            if delimiter in data:
                _, payload = data.split(delimiter, 1)
                print("[ProtectionModule] Unprotected data:")
                print(payload)
                return payload
        
            return data
        except Exception:
            # En caso de datos corruptos o no-HTTP
            return b""
        
    def _read_raw_data_routine(self) -> None:
        transport_layer = self.layer.layers_container.query_layer("TRANSPORT")
        
        while self._active:
            connection_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
            if not connection_identifier:
                time.sleep(0.1)
                continue

            raw_burst = transport_layer.receive(connection_identifier)
            if raw_burst:
                print("[ProtectionModule HTTP] Readed data from the TransportLayer:")
                print(raw_burst)

            if raw_burst:
                with self._lock:
                    # 1. Acumulamos TODO lo que viene del socket en un buffer crudo
                    self._received_data_buffer.extend(raw_burst)
                
                # 2. Intentamos extraer paquetes completos del buffer acumulado
                self._process_buffer()
            else:
                time.sleep(0.01)

    def _process_buffer(self) -> None:
        """Extrae el payload HTTP asegurando que esté completo antes de pasarlo arriba."""
        DELIMITER = b"\r\n\r\n"
        
        with self._lock:
            # Mientras haya posibilidad de encontrar una cabecera
            while DELIMITER in self._received_data_buffer:
                idx = self._received_data_buffer.find(DELIMITER)
                
                # Parsear Content-Length para saber cuánto esperar
                header_part = self._received_data_buffer[:idx].decode("utf-8", errors="ignore")
                content_length = 0
                for line in header_part.split("\r\n"):
                    if "Content-Length:" in line:
                        try:
                            content_length = int(line.split(":")[1].strip())
                        except: content_length = 0
                        break
                
                total_packet_size = idx + len(DELIMITER) + content_length
                
                # ¿Está el cuerpo completo en el acumulador?
                if len(self._received_data_buffer) >= total_packet_size:
                    # Extraer el payload RSA puro (256 bytes)
                    payload = self._received_data_buffer[idx + len(DELIMITER) : total_packet_size]
                    
                    # Lo movemos al buffer de datos limpios
                    self._clean_data_buffer.extend(payload)
                    
                    # Eliminamos el paquete procesado del buffer de red
                    del self._received_data_buffer[:total_packet_size]
                    
                    print(f"[ProtectionModule] Payload HTTP reconstruido: {len(payload)} bytes")
                else:
                    # Faltan datos por llegar del transporte, esperamos
                    break