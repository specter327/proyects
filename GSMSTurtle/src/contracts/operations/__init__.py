# Library import
from abc import ABC, abstractmethod
from typing import Any

# Classes definition
class OperationParametersInterface(ABC):
    "This class represents a interface (contract) for a operation parameters, following the defined standard."
    def __init__(self) -> None:
        pass

    @abstractmethod
    def validate(self) -> bool:
        """This method validates if the current parameters are correct and valid or not.

            If are invalid: return False
            If are valid: return True

            Returns:
                bool
        """
        raise NotImplementedError

    def to_dict(self) -> dict: raise NotImplementedError

class OperationResultsInterface(ABC):
    "This class represents a interface (contract) for a operation results, following the defined standard."
    def __init__(self) -> None:
        pass

    def to_dict(self) -> dict: raise NotImplementedError

class OperationInterface(ABC):
    "This class represents a interface (contract) for a operation, following the defined standard."
    def __init__(self) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def identification(self) -> str:
        raise NotImplementedError

    def execute(self, parameters: OperationParametersInterface) -> OperationResultsInterface: raise NotImplementedError