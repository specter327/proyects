# Library import
from abc import ABC, abstractmethod
from typing import Any

# Classes definition
class PropertyInterface(ABC):
    "This class represents a property interface (contract) defined on the standard."
    
    def __init__(self,
        imei: str,
        status_code: int
    ) -> None:
        pass

    @property
    def name(self) -> str: return self.NAME

    def read(self) -> Any: raise NotImplementedError

    def to_dict(self) -> dict: raise NotImplementedError