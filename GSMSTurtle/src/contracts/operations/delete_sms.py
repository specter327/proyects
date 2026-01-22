# Library import
from ..operations import OperationInterface, OperationParametersInterface, OperationResultsInterface
from ..data_classes.primitive_data import PrimitiveData
from typing import Dict

# Classes definition
class DeleteSMS(OperationInterface):
    # Class properties definition
    NAME: str = "Delete SMS"
    IDENTIFICATION: str = "DELETE_SMS"
    DESCRIPTION: str = "This operation allows to delete one SMS message stored on the SIM card, specifying its SIM_INDEX data"
    VERSION: str = "1"

    def __init__(self) -> None: pass

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

class DeleteSMSOperationParameters(OperationParametersInterface):
    def __init__(self,
        sim_index: int
    ) -> None:
        # Instance properties assignment
        self.sim_index = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=None,
            content=sim_index
        )
    
    # Public methods
    def validate(self) -> bool:
        return True

class DeleteSMSOperationResults(OperationResultsInterface):
    # Class properties definition
    STATUS_CODE: Dict[int, str] = {
        0:"SUCCESS",
        1:"UNKNOWN_ERROR"
    }

    def __init__(self,
        deleted_sms: bool,
        status_code: int
    ) -> None:
        # Instance properties assignment
        self.deleted_sms = PrimitiveData(
            data_type=bool,
            minimum_length=None,
            maximum_length=None,
            possible_values=(True, False),
            content=deleted_sms
        )

        self.status_code = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=(self.STATUS_CODE.keys()),
            content=status_code
        )
    
    def to_dict(self) -> dict:
        return {
            "DELETED_SMS":self.deleted_sms.content,
            "STATUS_CODE":self.status_code.content
        }