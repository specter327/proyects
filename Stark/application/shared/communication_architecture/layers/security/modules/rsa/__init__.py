# Library import
from ... import SecurityModuleInterface
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from ......utils.debug import smart_debug
from ......utils.logger import logger
from typing import Optional
from configurations import Configurations, Setting
import threading
import traceback
import time

# Classes definition
class SecurityModule(SecurityModuleInterface):
    MODULE_NAME = "SECURITY_RSA"
    # Corrección de Scope: Acceso directo a la constante de la clase padre
    CRYPTOGRAPHIC_MODEL = SecurityModuleInterface.ASYMMETRIC_MODEL

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)

        # Instance properties definition
        self._raw_buffer = bytearray()
        self._clean_buffer = bytearray()
        self._lock = threading.Lock()
        self._protection_layer = None
        self._connection_identifier = None
        self._read_unsecure_process: Optional[threading.Thread] = None
        self.layer = layer
        self.logger = logger(self.MODULE_NAME)

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def start(self) -> bool:
        # Set status active
        self._set_status(active=True)
        # Acceso corregido a la capa de protección a través del contenedor
        self._protection_layer = self.layer.layers_container.query_layer("PROTECTION")
        self._active = True
        # Create the receiver routine
        self._read_unsecure_process = threading.Thread(
            target=self._read_unsecure_routine,
            daemon=True
        )

        # Launch the receiver routine
        self._read_unsecure_process.start()

        # Return results
        self.logger.info(f"{self.MODULE_NAME} Initializated")

        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def stop(self) -> bool:
        # Set status inactive
        self._set_status(active=False)
        self.logger.info(f"{self.MODULE_NAME} finished")
        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self._set_configurated(configurated=True)
        return True
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def secure(self, data: bytes) -> bytes:
        remote_public_key_bytes = self.configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value

        # Verify the remote public key value
        if not remote_public_key_bytes:
            raise ValueError(f"Remote public key is missing for encryption")
        
        remote_public_key = serialization.load_pem_public_key(
            remote_public_key_bytes,
            backend=default_backend()
        )

        self.logger.debug(f"Securing data: {data}, with length: {len(data)}, with public key: {remote_public_key}")

        # Encryption with OAEP + SHA256
        encrypted_data = remote_public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.logger.debug(f"Secured data: {encrypted_data}")

        # Return results
        return encrypted_data
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def unsecure(self, data: bytes) -> bytes:
        # Get the private key
        private_key_bytes = self.configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value

        # Verify the private key
        if not private_key_bytes:
            raise ValueError(f"Private key is missing for decryption")
    
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )

        self.logger.debug(f"Decrypting data: {data}, with length: {len(data)}, with private key: {private_key}")

        # Decrypt the data
        decrypted_data = private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.logger.debug(f"Decrypted data: {decrypted_data}")

        # Return results
        return decrypted_data
    
    @classmethod
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def generate_configurations(cls) -> Configurations:
        # Generate a new private key
        new_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate a new public key
        new_public_key = new_private_key.public_key()

        # Serializate private and public keys (PEM)
        private_key_bytes = new_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key_bytes = new_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Generate configurations
        generated_configurations = cls.CONFIGURATIONS.copy()

        # Value assignment
        generated_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").value.value = private_key_bytes
        generated_configurations.query_setting("PRIVATE_ENCRYPTION_KEY").private = True

        generated_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value = public_key_bytes
        generated_configurations.query_setting("PUBLIC_ENCRYPTION_KEY").private = False

        # Return results
        #cls.logger.debug(f"Private key generated: {private_key_bytes}")
        #cls.logger.debug(f"Public key generated: {public_key_bytes}")
        
        return generated_configurations

    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def write(self, data: bytes) -> bool:
        self.logger.debug(f"Sending data: {data}, with length: {len(data)}")
        try:
            # RSA encryption
            secured_data = self.secure(data)
            print("[SecurityLayer RSA] Sending secured data. Original size:", len(data), "Secured size:", len(secured_data))

            # Re-send data to the protection layer
            return self._protection_layer.send(device_identifier=None, data=secured_data)
        except:
            traceback.print_exc()
            return False
    
    @smart_debug(element_name=MODULE_NAME, include_args=True, include_result=True)
    def read(self, limit: int = None, timeout: int = None) -> bytes:
        # Método síncrono para que la capa superior consuma datos limpios
        start_time = time.time()
        while True:
            with self._lock:
                if self._clean_buffer:
                    # Si hay datos, los entregamos
                    end = limit if limit is not None else len(self._clean_buffer)
                    data = bytes(self._clean_buffer[:end])
                    del self._clean_buffer[:end]

                    self.logger.debug(f"Received data: {data}, with length: {len(data)}")
                    return data
            
            # Gestión de Timeout si no hay datos
            if timeout is not None and (time.time() - start_time) > timeout:
                return b""
            
            time.sleep(0.01)
    
    def _read_unsecure_routine(self) -> None:
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        while self._active:
            # Pide a protección todo lo que tenga disponible, sin límite estricto de 256
            data = self._protection_layer.receive(device_identifier, limit=4096, timeout=1) 
            if data:
                self._raw_buffer.extend(data)
                
            # Mientras el buffer tenga suficiente para al menos un bloque RSA
            while len(self._raw_buffer) >= 256:
                block = bytes(self._raw_buffer[:256])
                del self._raw_buffer[:256] # Consumimos el bloque
                try:
                    decrypted = self.unsecure(block)
                    with self._lock:
                        self._clean_buffer.extend(decrypted)
                except:
                    print("Bloque corrupto o desalineado")