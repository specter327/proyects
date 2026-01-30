# Library import
from abc import ABC, abstractmethod
from ..data_classes.primitive_data import PrimitiveData
from typing import Any
import time

# Classes definition
class EventInterface(ABC):
    NAME: str = None
    
    def __init__(self) -> None:
        # Instance properties definition
        self.timestamp = time.time()
        self.status_seen: bool = False
        
    @property
    @abstractmethod
    def name(self) -> str: raise NotImplementedError

    @abstractmethod
    def identify(self, content: Any) -> bool: raise NotImplementedError

    def mark_seen(self) -> bool: self.status_seen = True; return True

class DeviceEventInterface(EventInterface):
    def __init__(self,
        device_identifier: str,
        event: object
    ) -> None:
        # Constructor hereditance
        super().__init__()
        
        # Instance properties assignment
        self.device_identifier = PrimitiveData(
            data_type=str,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=device_identifier
        )

        self.event = event

    @abstractmethod
    def prepare(self) -> bool: raise NotImplementedError