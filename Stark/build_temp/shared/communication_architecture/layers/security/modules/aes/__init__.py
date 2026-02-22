# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["ALL"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True

# Library import
from ... import SecurityModuleInterface
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Optional
from configurations import Configurations, Setting
from datavalue import PrimitiveData
from ......utils.debug import smart_debug
from ......utils.logger import logger
import threading
import traceback
import time
import os

# Classes definition
class SecurityModule(SecurityModuleInterface):
    MODULE_NAME = "SECURITY_AES"
    CRYPTOGRAPHIC_MODEL = SecurityModuleInterface.SIMMETRIC_MODEL

    # Definición de configuración específica para simétrico
    SymmetricKeySetting = Setting(
        value=PrimitiveData(
            data_type=bytes,
            value=None,
            data_class=True
        ),
        system_name="SYMMETRIC_KEY",
        symbolic_name="Symmetric key",
        description="Shared secret key for AES-256 encryption",
        optional=False,
        private=True
    )

    def __init__(self, layer: object) -> None:
        super().__init__(layer)
        
        # Sobrescribir configuraciones para usar la clave simétrica
        self.configurations = Configurations()
        self.configurations.add_setting(self.SymmetricKeySetting)
        
        self._raw_buffer = bytearray()
        self._clean_buffer = bytearray()
        self._lock = threading.Lock()
        self._protection_layer = None
        self._read_unsecure_process: Optional[threading.Thread] = None
        self._active = False
        self.logger = logger(self.MODULE_NAME)

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        self._protection_layer = self.layer.layers_container.query_layer("PROTECTION")
        self._active = True
        
        # Lanzar rutina de escucha concurrente
        self._read_unsecure_process = threading.Thread(
            target=self._read_unsecure_routine,
            daemon=True
        )
        self._read_unsecure_process.start()

        self.logger.info(f"{self.MODULE_NAME} Initializated")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        self._active = False

        self.logger.info(f"{self.MODULE_NAME} Finished")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations

        self.logger.info(f"Module configurated")
        return True

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def secure(self, data: bytes) -> bytes:
        """Cifra usando AES-GCM (Nonce + Ciphertext + Tag)."""
        key = self.configurations.query_setting("SYMMETRIC_KEY").value.value
        if not key: raise ValueError("Missing SYMMETRIC_KEY")

        self.logger.debug(f"Securing data: {data}, with length: {len(data)}")
        aesgcm = AESGCM(key)
        # Generamos un Nonce único de 96 bits (12 bytes) por paquete
        nonce = os.urandom(12)
        
        # El resultado de GCM incluye el ciphertext y el tag de autenticación (16 bytes)
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        
        self.logger.debug(f"Nonce: {nonce}, secured data: {encrypted_data}, with length: {encrypted_data}")
        # Retornamos Nonce + Datos Cifrados (que incluyen el Tag al final)
        return nonce + encrypted_data

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def unsecure(self, data: bytes) -> bytes:
        """Descifra y verifica integridad (AEAD)."""
        key = self.configurations.query_setting("SYMMETRIC_KEY").value.value
        if len(data) < 28: # 12 (nonce) + 16 (tag mínimo)
            return b""

        self.logger.debug(f"Decrypting data: {data}, with length: {len(data)}")
        aesgcm = AESGCM(key)
        nonce = data[:12]
        ciphertext = data[12:]
        
        # Si los datos fueron manipulados, decrypt lanzará una excepción (Integrity check)
        decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
        self.logger.debug(f"Decrypted data: {decrypted_data}, with length: {len(decrypted_data)}")

        return decrypted_data 

    @classmethod
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def generate_configurations(cls) -> Configurations:
        """Genera una clave aleatoria de 256 bits."""
        key = AESGCM.generate_key(bit_length=256)

        #cls.logger.debug(f"Generated key: {key}")

        generated_configurations = Configurations()
        setting = cls.SymmetricKeySetting.copy()
        setting.value.value = key
        generated_configurations.add_setting(setting)

        #cls.logger.info("Configurations generated")
        return generated_configurations

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def write(self, data: bytes) -> bool:
        self.logger.debug(f"Sending data: {data}, with length: {len(data)}")
        try:
            secured_data = self.secure(data)
            return self._protection_layer.send(device_identifier=None, data=secured_data)
        except:
            traceback.print_exc()
            return False

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def read(self, limit: int = None, timeout: int = None) -> bytes:
        start_time = time.time()
        while True:
            with self._lock:
                if self._clean_buffer:
                    end = limit if limit is not None else len(self._clean_buffer)
                    data = bytes(self._clean_buffer[:end])
                    del self._clean_buffer[:end]

                    self.logger.debug(f"Received data: {data}, length: {len(data)}")
                    return data
            
            if timeout is not None and (time.time() - start_time) > timeout:
                return b""
            time.sleep(0.01)

    def _read_unsecure_routine(self) -> None:
        device_id = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        while self._active:
            try:
                # AES-GCM no tiene tamaño de bloque fijo como RSA, pero el paquete 
                # suele ser pequeño en C2. Leemos un buffer razonable.
                data = self._protection_layer.receive(device_id, limit=4096, timeout=1)
                if data:
                    try:
                        decrypted = self.unsecure(data)
                        if decrypted:
                            with self._lock:
                                self._clean_buffer.extend(decrypted)
                    except Exception:
                        # Si la autenticación falla, descartamos el paquete (intento de inyección)
                        pass
            except:
                time.sleep(1)