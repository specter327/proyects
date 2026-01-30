# Library import
from . import DeviceEventInterface
from typing import Any

# Classes definition
class SIMRemovedEvent(DeviceEventInterface):
    # Class properties definition
    NAME: str = "SIM_REMOVED"

    # Public methods
    @property
    def name(self) -> str: return self.NAME
    
    def identify(self, content: Any) -> bool: raise NotImplementedError
    def prepare(self) -> bool: raise NotImplementedError