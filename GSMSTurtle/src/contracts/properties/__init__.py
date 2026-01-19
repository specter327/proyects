# Library import
from abc import ABC, abstractmethod
from typing import Any

# Classes definition
class PropertyInterface(ABC):
    "This class represents a property interface (contract) defined on the standard."
    
    def __init__(self) -> None:
        pass
    
    def read(self) -> Any: raise NotImplementedError