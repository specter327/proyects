# Library import
from . import PropertyInterface
from typing import Dict
from ..data_classes.primitive_data import PrimitiveData

# Classes definition
class QueryCCID(PropertyInterface):
    # Class properties definition
    NAME: str = "QUERY_CCID"
    STATUS_CODE: Dict[int, str] = {
        0:"SUCCESS",
        1:"SIM_NOT_INSERTED",
        2:"UNKNOWN_ERROR"
    }

    def __init__(self,
        ccid: str,
        status_code: int
    ) -> None:
        # Instance properties assignment
        self.ccid = PrimitiveData(
            data_type=str,
            minimum_length=19,
            maximum_length=20,
            content=ccid
        )

        self.status_code = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=tuple(self.STATUS_CODE.keys()),
            content=status_code
        )
    
    # Public methods
    def to_dict(self) -> dict:
        return {
            "CCID":self.ccid.content,
            "STATUS_CODE":self.status_code.content
        }
    
    def read(self): raise NotImplementedError