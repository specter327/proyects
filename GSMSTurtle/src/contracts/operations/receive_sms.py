# Library import
from ..operations import OperationInterface, OperationParametersInterface, OperationResultsInterface
from ..data_classes.phone_number import PhoneNumber
from ..data_classes.message import Message
from typing import Dict, List
from ..data_classes.primitive_data import PrimitiveData

# Classes definition
class ReceiveSMS(OperationInterface):
    NAME: str = "Receive SMS"
    IDENTIFICATION: str = "RECEIVE_SMS"
    DESCRIPTION: str = "This operation allows to receive all the current pending SMS messages on the device"
    VERSION: str = "1"

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        return self.NAME
    
    @property
    def version(self) -> str:
        return self.VERSION
    
    @property
    def description(self) -> str:
        return self.DESCRIPTION
    
    @property
    def identification(self) -> str:
        return self.IDENTIFICATION

class ReceiveSMSOperationParameters(OperationParametersInterface):
    def __init__(self) -> None:
        pass

    def validate(self) -> bool: return True

class ReceiveSMSOperationResults(OperationResultsInterface):
    # Class properties definition
    STATUS_CODE: Dict[int, str] = {
        0:"SUCCESS",
        1:"UNKNOWN_ERROR"
    }

    def __init__(self,
        messages: List[Message],
        status_code: int
    ) -> None:
        # Instance properties assignment
        self.messages = messages
        self.status_code = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=(self.STATUS_CODE.keys()),
            content=status_code
        )
    
    def to_dict(self) -> dict:
        return {
            "MESSAGES":self.messages,
            "STATUS_CODE":self.status_code.content
        }