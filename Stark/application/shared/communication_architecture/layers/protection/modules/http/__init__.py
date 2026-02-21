# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True

# Library import
from ... import ProtectionModuleInterface
from ......utils.logger import logger
from ......utils.debug import smart_debug
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
        self.logger = logger(self.MODULE_NAME)

        # Support routines
        self._read_raw_data_routine_process: threading.Thread = None
    
    # Public methods
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        # Set the status active
        self._active = True

        # Launch the read routine
        self._read_raw_data_routine_process = threading.Thread(
            target=self._read_raw_data_routine,
            daemon=True
        )
        self._read_raw_data_routine_process.start()
        self.logger.info("Module initializated")

        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        # Set the status inactive
        self._active = False
        self.logger.info("Module stopped")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self.configurated = True
        self.logger.info("Module configurated")
        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def write(self, data: bytes) -> bool:
        print("[ProtectionModule] Writed data through the connection:")
        print(data)
        protected_data = self.protect(data)
        
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        #self.logger.info(f"Sending pure data: {len(data)}/protected data: {len(protected_data)}, to the connection: {device_identifier}")

        return self._transport_layer.send(device_identifier, protected_data)

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def read(self, limit: int = None, timeout: int = None) -> bytes:
        # 1. Bloqueo para verificar y extraer
        with self._lock:
            if not self._clean_data_buffer:
                # Si no hay datos, salimos del lock para permitir que el hilo receptor escriba
                pass 
            else:
                end = limit if limit is not None else len(self._clean_data_buffer)
                data = bytes(self._clean_data_buffer[:end])
                del self._clean_data_buffer[:end]
                
                print("==========")
                print("[ProtectionLayer] Returned data:")
                print(data)
                return data

        # 2. Si llegamos aquí, es porque el buffer estaba vacío
        # Esperamos fuera del lock para no causar un deadlock
        time.sleep(0.100)
        return b""

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
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
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
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
        
        self.logger.info("Starting read data routine")

        while self._active:
            connection_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
            if not connection_identifier:
                time.sleep(0.1)
                continue

            raw_burst = transport_layer.receive(connection_identifier, limit=4096, timeout=30)
            if raw_burst:
                print("[ProtectionModule HTTP] Readed data from the TransportLayer:")
                print(raw_burst)
                self.logger.info(f"Readed data from tne transport layer: {len(raw_burst)}")
            else:
                time.sleep(0.01)

            if raw_burst:
                with self._lock:
                    # 1. Acumulamos TODO lo que viene del socket en un buffer crudo
                    self._received_data_buffer.extend(raw_burst)
                
                # 2. Intentamos extraer paquetes completos del buffer acumulado
                self._process_buffer()
            else:
                time.sleep(0.01)

    def _process_buffer(self) -> None:
        """
        Procesa el buffer crudo de forma secuencial y atómica.
        Extrae únicamente payloads completos basándose en el protocolo HTTP.
        """
        DELIMITER = b"\r\n\r\n"
        
        with self._lock:
            while True:
                # 1. Buscamos el final de las cabeceras
                idx = self._received_data_buffer.find(DELIMITER)
                if idx == -1:
                    # No hay cabecera completa todavía, esperamos más datos
                    break 

                # 2. Extraemos y parseamos las cabeceras para buscar el Content-Length
                try:
                    header_segment = self._received_data_buffer[:idx].decode("utf-8", errors="ignore")
                    content_length = -1
                    
                    for line in header_segment.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            content_length = int(line.split(":")[1].strip())
                            break
                    
                    if content_length == -1:
                        # ERROR DE PROTOCOLO: No hay Content-Length. 
                        # Purgamos hasta después del delimitador para intentar resincronizar.
                        del self._received_data_buffer[:idx + len(DELIMITER)]
                        continue

                except Exception as e:
                    # Si la cabecera está corrupta, purgamos un poco y reintentamos
                    del self._received_data_buffer[:idx + 1]
                    continue

                # 3. Verificamos si el cuerpo (body) ya llegó completo
                total_packet_size = idx + len(DELIMITER) + content_length
                
                if len(self._received_data_buffer) >= total_packet_size:
                    # EXTRAER PAYLOAD: Cortamos exactamente lo que dice el Content-Length
                    start_payload = idx + len(DELIMITER)
                    payload = self._received_data_buffer[start_payload : total_packet_size]
                    
                    # 4. Extensión Segura: Agregamos el payload binario INTACTO.
                    # JAMÁS usar .strip() sobre datos que provienen o van hacia una capa criptográfica.
                    self._clean_data_buffer.extend(payload)
                    
                    # 5. PURGA ATÓMICA: Eliminamos del buffer crudo SOLO el paquete procesado
                    del self._received_data_buffer[:total_packet_size]
                    
                    self.logger.info(f"Paquete extraído exitosamente: {len(payload)} bytes")                
                else:
                    # El cuerpo está incompleto. Salimos del bucle y esperamos a la
                    # siguiente ráfaga (burst) del transporte.
                    break