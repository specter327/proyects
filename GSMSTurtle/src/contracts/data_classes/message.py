# Library import
from .primitive_data import PrimitiveData
from datetime import datetime
import hashlib
from dataclasses import dataclass
from typing import ClassVar, Optional


# Classes definition
@dataclass
class MessageMetadata:
    SIM_STATUS: ClassVar[tuple] = (
        "REC UNREAD",
        "REC READ",
        "STO UNSENT",
        "STO SENT",

        None
    )

    sim_index: int
    sim_status: str
    network_timestamp: str
    raw_header: str

class Message:
    "This class represents a SMS message."

    # Class properties
    TYPE_SENT: str = "SENT"
    TYPE_RECEIVED: str = "RECEIVED"


    def __init__(self,
        message: str,
        metadata: MessageMetadata,
        timestamp: int = None,
        type: str = None,
        sender: str = None,
    ) -> None:
        # Instance properties assignment
        self.content = PrimitiveData(
            data_type=str,
            minimum_length=1,
            maximum_length=600,
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

        self.sender = PrimitiveData(
            data_type=None,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=sender
        )

        self.metadata = metadata
    
    # Public methods
    def generate_uid(self) -> str:
        signature = f"{self.sender.content}|{self.metadata.network_timestamp}|{self.content.content}"
        return hashlib.sha256(signature.encode('UTF-8')).hexdigest()