# Library import
from typing import Type, Optional, Any, Iterable, Dict, Union
from .. import exceptions
from .primitive_data import PrimitiveData
import json

# Classes definition
class ComplexData:
    def __init__(self,
        data_type: Type[list] | Type[tuple] | Type[set] | Type[frozenset] | Type[dict],
        value: Any,
        name: Optional[str] = None,
        description: Optional[str] = None,
        maximum_length: Optional[int] = None, minimum_length: Optional[int] = None,
        possible_values: Optional[Union[Iterable, Dict[Any, Any]]] = None,
        
        data_class: Optional[bool] = False
    ) -> None:
        # Instance properties assignment
        self.data_type = data_type
        self.value = value
        self.name = name
        self.description = description
        self.maximum_length = maximum_length; self.minimum_length = minimum_length
        self.possible_values = possible_values
        self.data_class = data_class

        # Validate constructor parameters
        if self.possible_values:
            # 1. Caso Diccionario (Mapping Schema)
            if self.data_type is dict and isinstance(self.possible_values, dict):
                pass # Es un esquema de mapeo válido

            # 2. Caso Colecciones (list/tuple)
            elif isinstance(self.possible_values, (list, tuple)):
                if self.data_type is dict:
                    if len(self.possible_values) not in (1, 2):
                        raise ValueError("Possible values for dict must be 1 (keys) or 2 (keys, values) list/tuples.")
                    if not isinstance(self.possible_values[0], (list, tuple)):
                        raise ValueError("The first element of possible_values for dict must be a list/tuple of keys.")
            else:
                raise ValueError(f"Possible values must be list/tuple or dict. Received: {type(self.possible_values).__name__}")
        

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
        # ESCENARIO A: Schema Mapping (possible_values es un dict)
        if isinstance(self.possible_values, dict):
            for input_key, input_value in data.items():
                matched_rule = False
                for schema_key, value_validators in self.possible_values.items():
                    # Validamos si la clave de entrada coincide con la regla (soporta Regex o Tipos)
                    if self._is_match(input_key, schema_key):
                        matched_rule = True
                        
                        # Normalizamos validadores a lista para permitir múltiples opciones por clave
                        if not isinstance(value_validators, (list, tuple, set, frozenset)):
                            validators = [value_validators]
                        else:
                            validators = value_validators
                        
                        if not any(self._is_match(input_value, v) for v in validators):
                            raise ValueError(f"[ComplexData] Invalid value '{input_value}' for key '{input_key}'")
                        break # Match encontrado para esta clave, pasar a la siguiente
                
                if not matched_rule:
                    raise ValueError(f"[ComplexData] Key '{input_key}' is not allowed by schema mapping.")
            return True

        # ESCENARIO B: Validación Posicional/Tradicional
        if not isinstance(self.possible_values, (list, tuple)) or len(self.possible_values) != 2:
            keys_schema = self.possible_values
            values_schema = None
        else:
            keys_schema, values_schema = self.possible_values
        
        for key, value in data.items():
            if keys_schema:
                if not any(self._is_match(key, validator) for validator in keys_schema):
                    raise ValueError(f"[ComplexData] Invalid key: {key}")
            
            if values_schema:
                if not any(self._is_match(value, validator) for validator in values_schema):
                    raise ValueError(f"[ComplexData] Invalid value '{value}' for key '{key}'")

        return True

    @classmethod
    def _serialize_recursive(cls, element: Any) -> Any:
        # 1. Caso: Instancias de validadores propios
        if isinstance(element, (PrimitiveData, ComplexData)):
            return {
                "__type__": element.__class__.__name__,
                "content": element.to_dict()
            }
        
        # 2. Caso: Referencias a tipos de clase (int, str, etc.)
        if isinstance(element, type):
            return {"__class__": element.__name__}
        
        # 3. Caso: Colecciones estándar
        if isinstance(element, (list, tuple, set, frozenset)):
            return [cls._serialize_recursive(i) for i in element]
        
        if isinstance(element, dict):
            new_dict = {}
            for k, v in element.items():
                # Serialización de clave: si es compleja, se convierte a JSON string
                # para mantener la validez del formato JSON.
                serialized_key = cls._serialize_recursive(k)
                if isinstance(serialized_key, (dict, list)):
                    import json
                    key_repr = json.dumps(serialized_key)
                else:
                    key_repr = str(serialized_key)
                
                new_dict[key_repr] = cls._serialize_recursive(v)
            return new_dict
        
        # 4. Caso: Literales
        return element

    @classmethod
    def _deserialize_recursive(cls, element: Any) -> Any:
        SAFE_TYPES = {
            "list": list, "tuple": tuple, "set": set, "frozenset": frozenset, 
            "dict": dict, "str": str, "int": int, "float": float, "bool": bool,
            "bytes": bytes, "bytearray": bytearray, "NoneType": type(None)
        }

        if isinstance(element, dict):
            # CASO A: Es un objeto serializado (PrimitiveData o ComplexData)
            if "__type__" in element:
                obj_type = element["__type__"]
                content = element["content"]
                if obj_type == "PrimitiveData":
                    return PrimitiveData.from_dict(content)
                elif obj_type == "ComplexData":
                    return cls.from_dict(content)
                raise ValueError(f"Unknown serialized object type: {obj_type}")

            # CASO B: Es una referencia a un tipo (__class__)
            if "__class__" in element:
                type_name = element["__class__"]
                if type_name in SAFE_TYPES:
                    return SAFE_TYPES[type_name]
                raise ValueError(f"Type '{type_name}' is not allowed or unknown.")

            # CASO C: Diccionario de datos (Reconstrucción de claves y valores)
            decoded_dict = {}
            for k, v in element.items():
                processed_key = k
                # Detectar si la clave es un objeto empaquetado en string
                if isinstance(k, str) and (k.startswith('{') or k.startswith('[')):
                    try:
                        import json
                        potential_obj = json.loads(k)
                        if isinstance(potential_obj, (dict, list)):
                            processed_key = cls._deserialize_recursive(potential_obj)
                    except:
                        pass # Si falla, se queda como string literal
                
                decoded_dict[processed_key] = cls._deserialize_recursive(v)
            return decoded_dict

        if isinstance(element, list):
            return [cls._deserialize_recursive(item) for item in element]
        
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

    def cli_capture(self, prompt_context: str = "") -> Any:
        label = self.name if self.name else f"Estructura ({self.data_type.__name__})"
        print(f"\n{prompt_context}[*] Configurando: {label}")
        if self.description:
            print(f"{prompt_context}    (Info: {self.description})")

        min_len = self.minimum_length if self.minimum_length is not None else 0
        max_len = self.maximum_length if self.maximum_length is not None else float('inf')

        # Procesamiento de Colecciones Iterables (Listas, Tuplas, Sets)
        if self.data_type in (list, tuple, set, frozenset):
            results = []
            while True:
                if len(results) >= min_len:
                    if len(results) >= max_len:
                        break
                    op = input(f"{prompt_context}    [?] ¿Añadir elemento a {label}? [s/N]: ").strip().lower()
                    if op not in ('s', 'si', 'y', 'yes'):
                        break
                else:
                    print(f"{prompt_context}    [-] Elementos requeridos: {len(results)}/{min_len}")

                # Identificar el esquema de los ítems internos
                item_schema = self.possible_values[0] if self.possible_values else None
                val = self._capture_from_options([item_schema] if item_schema else [], prompt_context + "    ")
                results.append(val)
            
            final_data = self.data_type(results)
            self.value = final_data
            return final_data

        # Procesamiento de Diccionarios (Mapas K:V)
        elif self.data_type is dict:
            results = {}
            
            # ESCENARIO A: Mapeo por Diccionario (Mapping Schema)
            if isinstance(self.possible_values, dict):
                # Iteramos sobre las claves exactas definidas en el esquema
                for schema_key, value_validators in self.possible_values.items():
                    # Resolver el nombre visual de la clave
                    if isinstance(schema_key, str):
                        key_name = schema_key
                    elif hasattr(schema_key, 'name') and schema_key.name:
                        key_name = schema_key.name
                    else:
                        key_name = "Clave dinámica"
                    
                    print(f"{prompt_context}    --- Configurando '{key_name}' ---")
                    
                    # Normalizamos los validadores a lista para el menú de opciones
                    validators = value_validators if isinstance(value_validators, (list, tuple)) else [value_validators]
                    val = self._capture_from_options(validators, prompt_context + "    ")
                    
                    # Asignación de la clave final
                    if isinstance(schema_key, str):
                        results[schema_key] = val
                    else:
                        # Si la clave es un PrimitiveData (ej. Regex), solicitamos que la ingrese el usuario
                        print(f"{prompt_context}    [>] Ingrese el nombre de la clave para este valor:")
                        custom_key = schema_key.cli_capture(prompt_context + "    ")
                        results[custom_key] = val

            # ESCENARIO B: Validación Posicional Tradicional
            elif isinstance(self.possible_values, (list, tuple)) and len(self.possible_values) == 2:
                keys_schema, values_schema = self.possible_values
                while True:
                    if len(results) >= min_len:
                        if len(results) >= max_len:
                            break
                        op = input(f"{prompt_context}    [?] ¿Añadir par Clave-Valor a {label}? [s/N]: ").strip().lower()
                        if op not in ('s', 'si', 'y', 'yes'):
                            break
                    else:
                        print(f"{prompt_context}    [-] Pares requeridos: {len(results)}/{min_len}")

                    print(f"{prompt_context}    --- Definiendo Clave ---")
                    key = self._capture_from_options(keys_schema, prompt_context + "    ")

                    print(f"{prompt_context}    --- Definiendo Valor para '{key}' ---")
                    val = self._capture_from_options(values_schema, prompt_context + "    ")

                    results[key] = val
            
            self.value = results
            return results

    def _capture_from_options(self, options: Iterable, prompt_context: str) -> Any:
        if not options:
            return input(f"{prompt_context}[>] Valor Libre (str): ")

        options_list = list(options)
        
        # Inferencia directa si solo hay una opción lógica
        if len(options_list) == 1:
            return self._capture_single_option(options_list[0], prompt_context)

        # Menú de selección interactiva (Polimorfismo)
        print(f"{prompt_context}[+] Opciones disponibles:")
        for i, opt in enumerate(options_list):
            if isinstance(opt, str):
                opt_name = opt
            else:
                opt_name = getattr(opt, 'name', None) or (opt.__name__ if isinstance(opt, type) else str(opt))
            print(f"{prompt_context}    {i}) {opt_name}")
            
        while True:
            idx = input(f"{prompt_context}    > Selección: ").strip()
            if idx.isdigit() and 0 <= int(idx) < len(options_list):
                selected = options_list[int(idx)]
                # Si se selecciona un string literal (ej: "INTERNET"), se asume como valor constante
                if isinstance(selected, str):
                    print(f"{prompt_context}    [=] Valor auto-asignado: {selected}")
                    return selected
                return self._capture_single_option(selected, prompt_context)
            print(f"{prompt_context}    [!] Selección inválida. Ingrese un índice numérico válido.")

    def _capture_single_option(self, opt: Any, prompt_context: str) -> Any:
        if isinstance(opt, (PrimitiveData, ComplexData)):
            return opt.cli_capture(prompt_context)
        elif isinstance(opt, type):
            while True:
                raw_in = input(f"{prompt_context}[>] Valor ({opt.__name__}): ").strip()
                try:
                    return opt(raw_in)
                except ValueError:
                    print(f"{prompt_context}[!] Formato inválido para tipo {opt.__name__}.")
        else:
            print(f"{prompt_context}[=] Valor inferido (Literal): {opt}")
            return opt