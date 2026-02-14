# Library import
from abc import ABC, abstractmethod

# Classes definition
class FileHandlerInterface(ABC):
    # Properties
    @property
    @abstractmethod
    def is_opened(self) -> bool: raise NotImplementedError
    
    # Public methods
    @abstractmethod
    def open(self) -> None: raise NotImplementedError
    
    @abstractmethod
    def close(self) -> None: raise NotImplementedError
    
    @abstractmethod
    def write(self, data: bytes) -> None: raise NotImplementedError
    
    @abstractmethod
    def read(self) -> bytes: raise NotImplementedError

from localfilehandler import *
from virtualfilehandler import *