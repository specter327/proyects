# Library import
from ..properties import PropertyInterface
from ..data_classes.primitive_data import PrimitiveData
from typing import Dict

# Classes definition
class QueryIMEI(PropertyInterface):
    # Class properties definition
    STATUS_CODE: Dict[int, str] = {
        0:"SUCCESS",
        1:"UNKNOWN_ERROR"
    }
    NAME: str = "QUERY_IMEI"
    
    def __init__(self,
        imei: str,
        status_code: int
    ) -> None:
        # Instance properties assignment
        self.imei = PrimitiveData(
            data_type=str,
            minimum_length=15,
            maximum_length=None,
            possible_values=None,
            content=imei
        )

        self.status_code = PrimitiveData(
            data_type=int,
            minimum_length=None,
            maximum_length=None,
            possible_values=(self.STATUS_CODE.keys()),
            content=status_code
        )
    
    def read(self): raise NotImplementedError
    
    def to_dict(self) -> dict:
        return {
            "IMEI":self.imei.content,
            "STATUS_CODE":self.status_code.content
        }