# Library import
from . import DeviceEventInterface
from ..data_classes.primitive_data import PrimitiveData
from typing import Any

# Classes definition
class MessageReceivedEvent(DeviceEventInterface):
    # Class properties definition
    NAME: str = "MESSAGE_RECEIVED"
    MESSAGE_TYPES: tuple = (
        "SMS",
        "MMS",
        "RCS"
    )
    MESSAGE_TYPE: str = ""
    SIM_INDEX: int = -1

    # Public methods
    @property
    def name(self) -> str: return self.NAME

    def identify(self, content: Any) -> bool: raise NotImplementedError
    def prepare(self) -> bool: raise NotImplementedError