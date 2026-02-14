# Library import
from abc import ABC, abstractmethod
from typing import Any
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import handlers
from handlers import FileHandlerInterface
from handlers import *

# Classes definition
class SecureFileHandler(FileHandlerInterface):
    # Class properties definition
    MAGIC: bytes = b"SFILEv1"
    SALT_SIZE: int = 16
    NONCE_SIZE: int = 12
    ITERATIONS: int = 200_000

    def __init__(self,
        file_handler: FileHandlerInterface,
        password: str
    ) -> None:
        # Instance properties assignment
        self._file_handler = file_handler
        self._password = password.encode("UTF-8")
    
    @property
    def is_opened(self) -> bool:
        return self._file_handler.is_opened

    # Private methods
    def _derive_key(self, salt: bytes) -> bytes:
        KDF = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=self.ITERATIONS,
            backend=default_backend()
        )

        return KDF.derive(self._password)

    # Public methods
    def open(self):
        self._file_handler.open()
    
    def close(self):
        self._file_handler.close()
        
    def write(self, data: bytes):
        if not self.is_opened:
            raise RuntimeError("File not opened")

        encrypted = self.encrypt(data)
        self._file_handler.write(encrypted)

    def append_write(self, data: bytes):
        if not self.is_opened:
            raise RuntimeError("File not opened")

        try:
            decrypted = self.read()
        except:
            decrypted = b""

        new_encrypted_data = self.encrypt(decrypted + data)
        self._file_handler.write(new_encrypted_data)

    def read(self) -> bytes:
        if not self.is_opened:
            raise RuntimeError("File not opened")

        encrypted = self._file_handler.read()
        return self.decrypt(encrypted)

    def encrypt(self, data: bytes) -> bytes:
        salt = os.urandom(self.SALT_SIZE)
        key = self._derive_key(salt)

        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)

        ciphertext = aesgcm.encrypt(nonce, data, self.MAGIC)

        return self.MAGIC + salt + nonce + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        if not data.startswith(self.MAGIC):
            raise ValueError("Invalid or corrupted file format")

        min_size = len(self.MAGIC) + self.SALT_SIZE + self.NONCE_SIZE + 16  # tag mínimo
        if len(data) < min_size:
            raise ValueError("File too small or corrupted")

        offset = len(self.MAGIC)

        salt = data[offset:offset + self.SALT_SIZE]
        offset += self.SALT_SIZE

        nonce = data[offset:offset + self.NONCE_SIZE]
        offset += self.NONCE_SIZE

        ciphertext = data[offset:]

        key = self._derive_key(salt)
        aesgcm = AESGCM(key)

        return aesgcm.decrypt(nonce, ciphertext, self.MAGIC)