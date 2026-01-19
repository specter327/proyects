# Library import
from typing import Type, Dict, Any, List

# Classes definition
class PrimitiveData:
    "This class represents a primitive data type, including his characteristics."
    
    def __init__(self,
        data_type: Type[str] | Type[int] | Type[float] | Type[bool] | None,
        minimum_length: int | float | None,
        maximum_length: int | float | None,
        possible_values: tuple | list | None,
        content: None | str | int | float | bool
    ) -> None:
        # Instance properties definition
        self.data_type = data_type
        self.minimum_length = minimum_length
        self.maximum_length = maximum_length
        self.possible_values = possible_values
        self.content = content
        self.metadata: Dict[str, Any] = {}

        # Validate the creation data
        self.validate(self.content)
    
    # Private methods
    def _validate_datatype(self, data) -> bool:
        if self.data_type is None: return True

        if not isinstance(data, self.data_type): raise ValueError(f"The data: {data}, is not of data type class: {self.data_type.__name__}")

        return True
    
    def _validate_minimum_length(self, data) -> bool:
        if self.minimum_length is None: return True

        if isinstance(data, str) and len(data) < self.minimum_length:
            raise ValueError(f"The data: {data}, is less than the minimum length: {self.minimum_length}")
        elif (isinstance(data, int) or isinstance(data, float)) and data < self.minimum_length:
            raise ValueError(f"The data: {data}, is less than the minimum length: {self.minimum_length}")

        return True
    
    def _validate_maximum_length(self, data) -> bool:
        if self.maximum_length is None: return True

        if isinstance(data, str):
            if len(data) > self.maximum_length: raise ValueError(f"The data: {data}, is greather than the maximum value: {self.maximum_length}")
        elif isinstance(data, int) or isinstance(data, float):
            if data > self.maximum_length: raise ValueError(f"The data: {data}, is greather than the maximum value: {self.maximum_length}")
    
        return True
    
    def _validate_possible_values(self, data) -> bool:
        if self.possible_values is None: return True

        if data not in self.possible_values: raise ValueError(f"The data: {data}, is not in the possible values: {str(self.possible_values)}")
        return True

    # Public methods
    def validate(self, data) -> bool:
        """This method validate a data using the local characteristics of data.
            If the validation fails a verification, it raises a exception

            Returns:
                bool: true (sucess)/false (error)
        """
        self._validate_datatype(data)
        self._validate_possible_values(data)
        self._validate_minimum_length(data)
        self._validate_maximum_length(data)

        return True

    def update(self, data) -> bool:
        """This method validate a data and if is approbed, it updates the local value
            It raises a error if a validation fails

            Returns:
                bool: true (sucess)/false (error)
        """
        if self.validate(data):
            self.content = data
            #self.data_type = type(data)
        
        return True

    def append_metadata(self, key: str, value: Any) -> bool:
        """This method append a metadata pair key-value to the data.
            It validates if the key currently exists: if exists, raise a KeyError exception

            Returns:
                bool: true (success)/false (error)
        """

        if key in self.metadata: raise KeyError(f"The key: {key}, already exists in the metadata: {list(self.metadata.keys())}")
        
        # Append the metadata
        self.metadata[key] = value

        return True

    def delete_metadata(self, key: str) -> bool:
        "This method deletes a metadata pair key-value."
        self.metadata.pop(key, None)
        return True
    
    def get_metadata(self, key: str) -> Any:
        "This method query for a metadata value specified by its key. Raise a KeyError exception if the key not exists."
        if key not in self.metadata: raise KeyError(f"The key: {key}, not exists in the metadata: {list(self.metadata.keys())}")
        return self.metadata[key]
    
    def query_metadata(self) -> List[str]:
        "This method returns all the current metadata keys."
        return list(self.metadata.keys())

    def to_string(self) -> str:
        "This method serializes the value content to a string format"
        return str(self.content)