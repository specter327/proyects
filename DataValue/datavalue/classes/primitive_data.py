# Library import
import re
from typing import Type, Optional, Any, Iterable, Union
from .. import exceptions

# Classes definition
class PrimitiveData:
    def __init__(self,
        data_type: Type,
        value: Any,
        maximum_length: Optional[int] = None, minimum_length: Optional[int] = None,
        maximum_size: Optional[Union[int, float]] = None, minimum_size: Optional[Union[int, float]] = None,
        possible_values: Optional[Iterable] = None,
        regular_expression: Optional[str] = None,
        
        data_class: Optional[bool] = False
    ) -> None:
        # Instance properties assignment
        self.data_type = data_type
        self.value = value
        self.maximum_length = maximum_length; self.minimum_length = minimum_length
        self.maximum_size = maximum_size; self.minimum_size = minimum_size
        self.possible_values = possible_values
        self.regular_expression = regular_expression
        self.data_class = data_class
        
        if not self.data_class:
            self.validate()
    
    # Private methods
    def __get_length(self, data: Optional[Any] = None) -> Optional[int]:
        if data is None:
            data_objective = self.value
        else:
            data_objective = data

        if isinstance(data_objective, (str, bytes, bytearray)):
            return len(data_objective)
        elif isinstance(data_objective, (int, float)):
            return len([digit for digit in str(data_objective) if digit.isdigit()])
        else:
            return None
    
    # Public methods
    def to_dict(self) -> dict:
        return {
            "DATA_TYPE":self.data_type.__name__ if hasattr(self.data_type, '__name__') else str(self.data_type),
            "VALUE":self.value,
            "MAXIMUM_LENGTH":self.maximum_length,
            "MINIMUM_LENGTH":self.minimum_length,
            "MAXIMUM_SIZE":self.maximum_size,
            "MINIMUM_SIZE":self.minimum_size,
            "POSSIBLE_VALUES":self.possible_values if self.possible_values is not None else None,
            "REGULAR_EXPRESSION":self.regular_expression,
            "DATA_CLASS":self.data_class
        }
        
    def validate(self, data: Optional[Any] = None) -> bool:
        # Define the data to validate
        if data is None:
            data_objective = self.value
        else:
            data_objective = data

        # Validacion de tipo de dato
        if not isinstance(data_objective, self.data_type):
            raise exceptions.DataTypeException(
                f"Incorrect data type.\nExpected: {self.data_type.__name__} - Received: {type(data_objective).__name__}"
            )
        
        # Validacion de longitud de caracteres (minimo, y maximo)
        if self.minimum_length is not None or self.maximum_length is not None:
            length = self.__get_length(data_objective)
            
            if length is not None:
                if self.minimum_length is not None and length < self.minimum_length:
                    raise exceptions.LengthException(f"Character/digit length below the minimum: {length} < {self.minimum_length}")
                elif self.maximum_length is not None and length > self.maximum_length:
                    raise exceptions.LengthException(f"Character/digit length above the maximum: {length} > {self.maximum_length}")
        
        # Validacion de tamaño (magnitud)
        if self.minimum_size is not None or self.maximum_size is not None:
            if isinstance(data_objective, (int, float)):
                if self.minimum_size is not None and data_objective < self.minimum_size:
                    raise exceptions.SizeException(f"Numerical value below the minimum: {data_objective} < {self.minimum_size}")
                if self.maximum_size is not None and data_objective > self.maximum_size:
                    raise exceptions.SizeException(f"Numerical value above the maximum: {data_objective} > {self.maximum_size}")
        
        # Validacion de posibles valores (conjunto)
        if self.data_type is bool:
            if data_objective not in (True, False):
                raise exceptions.PossibleValueException(
                    f"The boolean value has to be True or False: {data_objective} != True/False"
                )
        if self.possible_values is not None:
            if data_objective not in self.possible_values:
                raise exceptions.PossibleValueException(
                    f"The value is not in the possible values set: {data_objective} not in {self.possible_values}"
                )
        
        # Validacion de expresion regular
        if self.regular_expression is not None:
            if isinstance(data_objective, (str, bytes, bytearray)):
                # Soporte para bytes/bytearray convirtiendo el patrón si es necesario
                pattern = self.regular_expression
                if isinstance(data_objective, (bytes, bytearray)) and isinstance(pattern, str):
                    pattern = pattern.encode()
                
                if not re.fullmatch(pattern, data_objective):
                    raise exceptions.RegularExpressionException(f"The value does not meet the required pattern: {self.regular_expression}")
        
        return True