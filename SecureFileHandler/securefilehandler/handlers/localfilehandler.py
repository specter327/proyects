# Library import
from typing import Optional, BinaryIO
from . import FileHandlerInterface

# Classes definition
class LocalFileHandler(FileHandlerInterface):
    def __init__(self,
        filepath: str,
        mode: str
    ) -> None:
        # Instance properties assignment
        self._filepath = filepath
        self._mode = mode
        self._file_handler: Optional[BinaryIO] = None
    
    # Properties
    @property
    def is_opened(self) -> bool:
        return self._file_handler is not None and not self._file_handler.closed
    
    # Public methods
    def open(self):
        self._file_handler = open(self._filepath, self._mode)
    
    def close(self):
        if self._file_handler and not self._file_handler.closed:
            self._file_handler.close()
    
    def write(self, data: bytes):
        self._file_handler.seek(0)
        self._file_handler.truncate(0)

        self._file_handler.write(data)
        self._file_handler.flush()
    
    def read(self):
        self._file_handler.seek(0)
        data = self._file_handler.read()
        return data