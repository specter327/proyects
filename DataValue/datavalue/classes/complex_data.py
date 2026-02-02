# Library import
from typing import Type, Optional, Any, Iterable
from .. import exceptions
from .primitive_data import PrimitiveData

# Classes definition
class ComplexData:
    def __init__(self,
        data_type: Type[list] | Type[tuple] | Type[set] | Type[frozenset] | Type[dict],
        value: Any,
        maximum_length: Optional[int] = None, minimum_length: Optional[int] = None,
        possible_values: Optional[Iterable] = None,
        
        data_class: Optional[bool] = False
    ) -> None:
        # Instance properties assignment
        self.data_type = data_type
        self.value = value
        self.maximum_length = maximum_length; self.minimum_length = minimum_length
        self.possible_values = possible_values
        self.data_class = data_class

        # Validate constructor parameters
        if self.possible_values:
            # Base validation: it has to be a collection
            if not isinstance(self.possible_values, (list, tuple)):
                raise ValueError(f"The possible values has to be a list/tuple. Received: {type(self.possible_values).__name__}")
            
            # Validation to collections (list, tuple, set, frozenset)
            if self.data_type != dict:
                if not isinstance(self.possible_values, (list, tuple)):
                    raise ValueError(f"Possible values for {self.data_type.__name__} must be exactly one list/tuple containing the options.")
            
            # Specific validation for dicts
            else: # self.data_type == dict
                if len(self.possible_values) not in (1, 2):
                    raise ValueError("Possible values for dict must be 1 (keys) or 2 (keys, values) list/tuples.")
                
                # Validate the first element
                if not isinstance(self.possible_values[0], (list, tuple)):
                    raise ValueError("The first element of possible_values for dict must be a list/tuple of keys.")
                
                # Validate the second element
                if len(self.possible_values) == 2 and not isinstance(self.possible_values[1], (list, tuple)):
                    raise ValueError("The second element of possible_values for dict must be a list/tuple of value validators.")
        
        # Execute instance data validation
        if not self.data_class:
            self.validate()
    
    # Private methods
    def _is_match(self, element: Any, schema: Any) -> bool:
        # Validate data types
        if isinstance(schema, (PrimitiveData, ComplexData)):
            try:
                return schema.validate(element)
            except:
                return False
        
        # Validate class data types
        if isinstance(schema, type):
            return isinstance(element, schema)
    
        # Validate literal values
        return element == schema
            
    def _validate_collection(self, data: Any) -> bool:
        element_index: int = 0
        for element in data:
            if not any(self._is_match(element, validator) for validator in self.possible_values):
                raise ValueError(f"[ComplexData] Element: {element}, on index: {element_index} is not allowed.")
            element_index += 1
        
        # Return results
        return True
    
    def _validate_dictionary(self, data: Any) -> bool:
        # Validate keys and (if applies) values
        if not isinstance(self.possible_values, (list, tuple)) or len(self.possible_values) != 2:
            keys_schema = self.possible_values
            values_schema = None
        else:
            keys_schema, values_schema = self.possible_values
        
        for key, value in data.items():
            # Validación de Claves (Debe ser un iterable de opciones)
            if keys_schema:
                if not any(self._is_match(key, validator) for validator in keys_schema):
                    raise ValueError(f"[ComplexData] Invalid key: {key}")
            
            # Validación de Valores
            if values_schema:
                if not any(self._is_match(value, validator) for validator in values_schema):
                    raise ValueError(f"[ComplexData] Invalid value '{value}' for key '{key}'")

        return True
        
    # Public methods
    def validate(self, data: Any = None) -> bool:
        # Determine objective data
        if data is None:
            objective_data = self.value
        else:
            objective_data = data

        # Data type validation
        if not isinstance(objective_data, self.data_type):
            raise exceptions.DataTypeException(
                f"Incorrect data type.\nExpected: {self.data_type.__name__} - Received: {type(objective_data).__name__}"
            )
    
        # Length validation
        current_length = len(objective_data)
        
        if self.minimum_length is not None and current_length < self.minimum_length:
            raise ValueError(f"Minimum length not reached: {current_length} < {self.minimum_length}")
    
        if self.maximum_length is not None and current_length > self.maximum_length:
            raise ValueError(f"Maximum length reached: {current_length} > {self.maximum_length}")
    
        # Content validation and recurse
        if self.possible_values:
            # Validate dictionaries
            if isinstance(objective_data, dict):
                self._validate_dictionary(objective_data)
            else:
                self._validate_collection(objective_data)
        
        # Return results
        return True