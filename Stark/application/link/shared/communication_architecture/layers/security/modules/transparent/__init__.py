# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True

# Library import
from ... import SecurityModuleInterface
from ......utils.logger import logger
from ......utils.debug import smart_debug
from typing import Optional
from configurations import Configurations
import threading
import traceback
import time

class SecurityModule(SecurityModuleInterface):
    MODULE_NAME = "SECURITY_TRANSPARENT"
    # Definimos un modelo simétrico simple para evitar la negociación compleja de RSA
    CRYPTOGRAPHIC_MODEL = SecurityModuleInterface.SIMMETRIC_MODEL

    def __init__(self, layer: object) -> None:
        super().__init__(layer)
        self._clean_buffer = bytearray()
        self._lock = threading.Lock()
        self._protection_layer = None
        self._active = False
        self._read_process: Optional[threading.Thread] = None
        self.layer = layer
        self.logger = logger(self.MODULE_NAME)

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        self._protection_layer = self.layer.layers_container.query_layer("PROTECTION")
        self._active = True
        #self._read_process = threading.Thread(
        #    target=self._read_routine,
        #    daemon=True
        #)
        #self._read_process.start()

        self.logger.info("Module initializated")
        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        self._active = False
        self.logger.info("Module stopped")

        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self._set_configurated(configurated=True)
        self.logger.info("Module configurated")
        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def secure(self, data: bytes) -> bytes:
        # Pass-through: Sin cifrado
        return data
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def unsecure(self, data: bytes) -> bytes:
        # Pass-through: Sin descifrado
        return data
    
    @classmethod
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def generate_configurations(cls) -> Configurations:
        # Retorna configuraciones base vacías para cumplir el contrato
        return cls.CONFIGURATIONS.copy()

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def write(self, data: bytes) -> bool:
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value

        try:
            # Envia los datos directamente a la capa inferior
            return self._protection_layer.send(device_identifier=device_identifier, data=data)
        except:
            traceback.print_exc()
            return False
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def read(self, limit: int = None, timeout: int = None) -> bytes:
    # RASTREO 5: Verificar parámetros de entrada
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        self.logger.debug(f"Solicitando a Protection: ID={device_identifier}, limit={limit}, timeout={timeout}")
        
        # Llamada a la capa inferior
        data = self._protection_layer.receive(device_identifier, limit=limit, timeout=timeout)
        
        # RASTREO 6: Resultado de la capa de protección
        if len(data) > 0:
            self.logger.debug(f"¡DATOS OBTENIDOS!: {data}")
        else:
            # Esto te dirá si el problema es que la protección no devuelve nada
            self.logger.debug(f"Protección devolvió vacío (posible timeout)")
            
        return data
    
    
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        return self._protection_layer.receive(device_identifier, limit=limit, timeout=timeout)
    
        start_time = time.time()
        while True:
            with self._lock:
                if self._clean_buffer:
                    end = limit if limit is not None else len(self._clean_buffer)
                    data = bytes(self._clean_buffer[:end])
                    del self._clean_buffer[:end]
                    self.logger.debug(f"Returned data: {len(data)}")

                    return data
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return b""
            
            time.sleep(0.01)
    
    def _read_routine(self) -> None:
        """
        Punta de entrada concurrente: Mueve datos de PROTECTION a SECURITY
        sin procesar bloques fijos.
        """
        self.logger.info("Starting receive routine")
        while self._active:
            device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
            if not device_identifier:
                print("THERES ANY FUCKING device IDENTIFIER")
                time.sleep(0.100)
                continue

            try:
                # Leemos lo que esté disponible, sin forzar 256 bytes
                data = self._protection_layer.receive(device_identifier, limit=1, timeout=1) 
                if data:
                    with self._lock:
                        # En este módulo, unsecure() no hace nada
                        self.logger.debug(f"Extended data: {len(data)}")
                        self._clean_buffer.extend(self.unsecure(data))
                        print("[SecurityModule TRANSPARENT] Extended data:")
                        print(data)
            except Exception:
                traceback.print_exc()
        self.logger.info("Stopping receive routine")