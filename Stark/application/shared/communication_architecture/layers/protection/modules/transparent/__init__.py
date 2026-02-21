# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True

# system/core/layers/session/protection/modules/transparent_protection.py

from ... import ProtectionModuleInterface
import threading
import time

class ProtectionModule(ProtectionModuleInterface):
    MODULE_NAME: str = "TRANSPARENT_PROTECTION"

    def __init__(self, layer: object) -> None:
        super().__init__(layer)
        self._active: bool = False
        self._lock = threading.Lock()
        self._clean_data_buffer = bytearray()
        self._transport_layer = layer.layers_container.query_layer("TRANSPORT")
        self._reader_thread: threading.Thread = None

    def start(self) -> bool:
        self._active = True
        self._reader_thread = threading.Thread(target=self._read_routine, daemon=True)
        self._reader_thread.start()
        return True

    def stop(self) -> bool:
        self._active = False
        return True

    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        return True

    def write(self, data: bytes) -> bool:
        # En modo transparente, no hay transformación (protect)
        device_id = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        return self._transport_layer.send(device_id, data)

    def read(self, limit: int = None, timeout: int = None) -> bytes:
        with self._lock:
            if not self._clean_data_buffer:
                return b""
            
            end = limit if limit is not None else len(self._clean_data_buffer)
            data = bytes(self._clean_data_buffer[:end])
            del self._clean_data_buffer[:end]
            return data

    def protect(self, data: bytes) -> bytes:
        return data

    def unprotect(self, data: bytes) -> bytes:
        return data

    def _read_routine(self) -> None:
        """Rutina de lectura simplificada sin parsing."""
        # Cacheamos el ID para optimizar el bucle
        device_id = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        
        while self._active:
            try:
                # Lectura directa del transporte
                raw_data = self._transport_layer.receive(device_id)
                
                if raw_data:
                    with self._lock:
                        self._clean_data_buffer.extend(raw_data)
                else:
                    # Evitar saturación de CPU si no hay datos
                    time.sleep(0.05)
            except Exception as e:
                # Loggear error si fuera necesario
                break