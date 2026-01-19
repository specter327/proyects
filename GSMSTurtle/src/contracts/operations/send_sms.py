# Library import
from ..operations import OperationInterface, OperationParametersInterface, OperationResultsInterface
from ..data_classes.phone_number import PhoneNumber
from ..data_classes.message import Message
from typing import Dict
from ..data_classes.primitive_data import PrimitiveData

# Classes definition
class SendSMS(OperationInterface):
    # Class properties definition
    NAME: str = "Send SMS"
    IDENTIFICATION: str = "SEND_SMS"
    DESCRIPTION: str = "This operation allows to send a SMS message to a specified phone number destinatary"
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
    

class SendSMSOperationParameters(OperationParametersInterface):
    def __init__(self,
        phone_number: str,
        message: str
    ) -> None:
        # Instance property definition
        self.destinatary_phone_number: PhoneNumber = PhoneNumber(phone_number)
        self.message: Message = Message(message)
    
    # Public methods
    def validate(self) -> bool:
        return True

class SendSMSOperationResults(OperationResultsInterface):
    # Class properties definition
    STATUS_CODE: Dict[int, str] = {
        0:"SUCCESS",
        1:"UNKNOWN_ERROR",
        2:"TIMEOUT_ERROR",
        3:"SEND_ERROR"
    }

    def __init__(self,
        send_result: bool,
        status_code: int
    ) -> None:
        # Instance properties assignment
        self.send_result = PrimitiveData(
            data_type=bool,
            minimum_length=None,
            maximum_length=None,
            possible_values=(True, False),
            content=send_result
        )

        self.status_code = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=(self.STATUS_CODE.keys()),
            content=status_code
        )