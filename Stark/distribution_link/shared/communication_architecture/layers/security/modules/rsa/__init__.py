# Library import
from ... import SecurityModuleInterface
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
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
        return True
    
    def stop(self) -> bool:
        # Set status inactive
        self._set_status(active=False)
        return True
    
    def configure(self, configurations: object) -> bool:
        self.configurations = configurations
        self._set_configurated(configurated=True)
        return True
    
    def secure(self, data: bytes) -> bytes:
        remote_public_key_bytes = self.configurations.query_setting("PUBLIC_ENCRYPTION_KEY").value.value

        # Verify the remote public key value
        if not remote_public_key_bytes:
            raise ValueError(f"Remote public key is missing for encryption")
        
        remote_public_key = serialization.load_pem_public_key(
            remote_public_key_bytes,
            backend=default_backend()
        )

        # Encryption with OAEP + SHA256
        encrypted_data = remote_public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Return results
        return encrypted_data
    
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

        # Decrypt the data
        decrypted_data = private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Return results
        return decrypted_data
    
    @classmethod
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
        return generated_configurations

    def write(self, data: bytes) -> bool:
        try:
            # RSA encryption
            secured_data = self.secure(data)
            print("[SecurityLayer RSA] Sending secured data. Original size:", len(data), "Secured size:", len(secured_data))

            # Re-send data to the protection layer
            return self._protection_layer.send(device_identifier=None, data=secured_data)
        except:
            traceback.print_exc()
            return False
    
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
                    return data
            
            # Gestión de Timeout si no hay datos
            if timeout is not None and (time.time() - start_time) > timeout:
                return b""
            
            time.sleep(0.01)
    
    def _read_unsecure_routine(self) -> None:
        device_identifier = self.layer.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value
        print("[SecurityModule RSA] Lanzando proceso de lectura concurrente")
        while self._active:
            try:
                # Pide a protección (que ya limpió el HTTP)
                #print("[SecureModule RSA] Device identifier:", device_identifier)
                data = self._protection_layer.receive(device_identifier, limit=256, timeout=1) 
                if data:
                    print(f"[SecureModule RSA] Received data from the ProtectionLayer (length: {len(data)}):")
                    print(data)

                if len(data) == 256: # Bloque RSA completo
                    try:
                        decrypted = self.unsecure(data)
                        with self._lock:
                            self._clean_buffer.extend(decrypted)
                    except:
                        print("Error de descifrado: Llave incorrecta o bloque corrupto")
            except:
                print("[SecurityModule RSA] Error en la rutina de lectura")
                traceback.print_exc()

        print("[SecurityModule RSA] Deteniendo proceso de lectura concurrente")
