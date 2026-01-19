# Library import
from .primitive_data import PrimitiveData

# Classes definition
class Message:
    "This class represents a SMS message."

    # Class properties
    TYPE_SENT: str = "SENT"
    TYPE_RECEIVED: str = "RECEIVED"

    def __init__(self,
        message: str,
        timestamp: int = None,
        type: str = None
    ) -> None:
        # Instance properties assignment
        self.content = PrimitiveData(
            data_type=str,
            minimum_length=1,
            maximum_length=200,
            possible_values=None,
            content=message
        )
        self.timestamp = PrimitiveData(
            data_type=None,
            minimum_length=1,
            maximum_length=None,
            possible_values=None,
            content=timestamp
        )
        self.type = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=(self.TYPE_SENT, self.TYPE_RECEIVED, None),
            content=type
        )