# Library import
from . import DeviceEventInterface
from datavalue import PrimitiveData
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

    def __init__(self, *args,**kwargs) -> None:
        # Class hereditance
        super().__init__(*args, **kwargs)

        # Instance properties assignment
        self.message_type = PrimitiveData(
            data_type=str,
            value=None,
            maximum_length=None, minimum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=self.MESSAGE_TYPES,
            regular_expression=None,
            data_class=True
        )

        self.sim_index = PrimitiveData(
            data_type=int,
            value=None,
            maximum_length=None, minimum_length=None,
            maximum_size=None, minimum_size=None,
            possible_values=None,
            regular_expression=None,
            data_class=True
        )

    # Public methods
    @property
    def name(self) -> str: return self.NAME

    def identify(self, content: Any) -> bool: raise NotImplementedError
    def prepare(self) -> bool: raise NotImplementedError