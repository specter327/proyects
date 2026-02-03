# Library import
from typing import Type, Optional, Any, Iterable
from .. import exceptions
from .primitive_data import PrimitiveData
import json

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
        
    @classmethod
    def _serialize_recursive(cls, element: Any) -> Any:
        # 1. Caso: Instancias de tus clases
        if isinstance(element, (PrimitiveData, ComplexData)):
            return {
                "__type__": element.__class__.__name__,
                "content": element.to_dict()
            }
        
        # 2. Caso: Tipos de datos (clases como str, int, dict)
        if isinstance(element, type):
            return {"__class__": element.__name__}
        
        # 3. Caso: Colecciones estándar (recursión profunda)
        if isinstance(element, (list, tuple, set, frozenset)):
            return [cls._serialize_recursive(i) for i in element]
        
        if isinstance(element, dict):
            return {str(k): cls._serialize_recursive(v) for k, v in element.items()}
        
        # 4. Caso: Literales serializables (int, str, float, bool, None)
        return element

    @classmethod
    def _deserialize_recursive(cls, element: Any) -> Any:
        SAFE_TYPES = {
            "list": list, "tuple": tuple, "set": set, "frozenset": frozenset, 
            "dict": dict, "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray
        }

        # A. Manejo de Diccionarios (Estructuras u Objetos Serializados)
        if isinstance(element, dict):
            # Caso 1: Es un objeto serializado (PrimitiveData o ComplexData)
            if "__type__" in element:
                obj_type = element["__type__"]
                content = element["content"]
                
                if obj_type == "PrimitiveData":
                    return PrimitiveData.from_dict(content)
                elif obj_type == "ComplexData":
                    return cls.from_dict(content)
                else:
                    raise ValueError(f"Unknown serialized object type: {obj_type}")

            # Caso 2: Es una referencia a un tipo de clase (__class__)
            if "__class__" in element:
                type_name = element["__class__"]
                if type_name in SAFE_TYPES:
                    return SAFE_TYPES[type_name]
                raise ValueError(f"Type '{type_name}' is not allowed or unknown.")

            # Caso 3: Es un diccionario de datos común (recurse keys & values)
            return {k: cls._deserialize_recursive(v) for k, v in element.items()}

        # B. Manejo de Listas (recurse items)
        if isinstance(element, list):
            return [cls._deserialize_recursive(item) for item in element]
        
        # C. Literales (retorno directo)
        return element


    # Public methods
    def to_dict(self) -> dict:
        return {
            "DATA_TYPE":self.data_type.__name__ if hasattr(self.data_type, '__name__') else str(self.data_type),
            "VALUE":self._serialize_recursive(self.value),
            "MAXIMUM_LENGTH":self.maximum_length,
            "MINIMUM_LENGTH":self.minimum_length,
            "POSSIBLE_VALUES":self._serialize_recursive(self.possible_values) if self.possible_values is not None else None,
            "DATA_CLASS":self.data_class,
            "__type__":"ComplexData"
        }

    
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexData':
        # 1. Secure types mapping
        SAFE_TYPES = {
            "list": list, "tuple": tuple, "set": set, "frozenset": frozenset, 
            "dict": dict, "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray
        }

        # 3. Validación y Reconstrucción del Root
        # Recuperamos el tipo de dato principal
        raw_type = data.get("DATA_TYPE")
        data_type = SAFE_TYPES.get(raw_type)
        if not data_type:
            raise TypeError(f"Invalid root data type: {raw_type}")

        # Procesamos los possible_values con el motor recursivo
        raw_possible = data.get("POSSIBLE_VALUES")
        possible_values = cls._deserialize_recursive(raw_possible) if raw_possible is not None else None
        
        # Corrección de tipo para tuplas (JSON no tiene tuplas, devuelve listas)
        # Si su __init__ es estricto y requiere tupla para possible_values, convertimos aquí:
        if isinstance(possible_values, list) and data_type != dict:
             possible_values = tuple(possible_values)
        
        # Para dicts, mantenemos la lista de listas o convertimos según su preferencia estricta
        if isinstance(possible_values, list) and data_type == dict:
             # Opcional: convertir sub-listas a tuplas si su validador lo prefiere, 
             # aunque su validación actual acepta listas.
             pass

        return cls(
            data_type=data_type,
            value=data.get("VALUE"), # Asumimos valor literal o serializable simple
            maximum_length=data.get("MAXIMUM_LENGTH"),
            minimum_length=data.get("MINIMUM_LENGTH"),
            possible_values=possible_values,
            data_class=data.get("DATA_CLASS", False)
        )

    
    @classmethod
    def from_json(cls, text_content: str) -> 'ComplexData':
        try:
            data = json.loads(text_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        return cls.from_dict(data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
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