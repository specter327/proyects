# Library import
from typing import Optional
from io import BytesIO
from . import FileHandlerInterface

class VirtualFileHandler(FileHandlerInterface):
    def __init__(self) -> None:
        self._buffer: Optional[BytesIO] = None

    # Properties
    @property
    def is_opened(self) -> bool:
        return self._buffer is not None

    # Public methods
    def open(self):
        if not self.is_opened:
            self._buffer = BytesIO()

    def close(self):
        if self._buffer is not None:
            self._buffer.close()
            self._buffer = None

    def write(self, data: bytes):
        if not self.is_opened:
            raise RuntimeError("File not opened")

        # Sobrescritura completa
        self._buffer.seek(0)
        self._buffer.truncate(0)
        self._buffer.write(data)

    def read(self) -> bytes:
        if not self.is_opened:
            raise RuntimeError("File not opened")

        self._buffer.seek(0)
        return self._buffer.read()