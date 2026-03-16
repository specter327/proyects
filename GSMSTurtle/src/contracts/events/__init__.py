# Library import
from abc import ABC, abstractmethod
from datavalue import PrimitiveData
from typing import Any
import time

# Classes definition
class EventInterface(ABC):
    NAME: str = None
    
    def __init__(self, **kwargs) -> None:
        # Instance properties definition
        self.timestamp = time.time()
        self.status_seen: bool = False
        
    @property
    @abstractmethod
    def name(self) -> str: raise NotImplementedError

    def mark_seen(self) -> bool: self.status_seen = True; return True

class DeviceEventInterface(EventInterface):
    def __init__(self,
        device_identifier: str,
        event: object,
        **kwargs
    ) -> None:
        # Constructor hereditance
        super().__init__(**kwargs)
        
        # Instance properties assignment
        self.device_identifier = PrimitiveData(
            data_type=str,
            value=device_identifier,
            minimum_length=None, maximum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=None,
            regular_expression=None,
            data_class=False
        )

        self.event = event

    @abstractmethod
    def prepare(self) -> bool: raise NotImplementedError

    @abstractmethod
    def identify(self, content: Any) -> bool: raise NotImplementedError