# Library import
from datavalue import PrimitiveData
from datavalue import ComplexData
import json

# Classes definition
class Setting:
    "This class represent a setting, including its value and characteristics."

    def __init__(self,
        value: PrimitiveData | ComplexData,
        system_name: str,
        symbolic_name: str,
        description: str = "",
        optional: bool = False,
        private: bool = False
        # default_value TODO !
    ) -> None:
        # Instance property definition
        self.system_name = system_name.upper() # Serialized in uppercase
        self.symbolic_name = symbolic_name
        self.description = description
        self.value = value
        self.optional = optional
        self.private = private
    
    # Public methods
    def to_dict(self) -> dict:
        "This method serializes the configuration to a dict data structure."
        structure = {
            "SYSTEM_NAME":self.system_name,
            "SYMBOLIC_NAME":self.symbolic_name,
            "DESCRIPTION":self.description,
            "VALUE":self.value.to_dict(),
            "OPTIONAL":self.optional,
            "PRIVATE":self.private
        }

        if self.private:
            private_value = self.value.to_dict()
            private_value["VALUE"] = "*****"

            structure["VALUE"] = private_value
    
        return structure
    
    @classmethod
    def from_dict(cls, data: dict) -> "Setting":
        # Extract the Setting metadata
        system_name = data.get("SYSTEM_NAME")
        symbolic_name = data.get("SYMBOLIC_NAME")
        description = data.get("DESCRIPTION")
        optional = data.get("OPTIONAL", False)
        private = data.get("PRIVATE", False)

        raw_value = data.get("VALUE")

        # Verify the metadata
        if not system_name or raw_value is None:
            raise ValueError("Missing mandatory fields (SYSTEM_NAME or VALUE).")
        
        # Re-creation from instance PrimitiveData or ComplexData
        if raw_value.get("__type__") == "PrimitiveData":
            value_object = PrimitiveData.from_dict(raw_value)
        elif raw_value.get("__type__") == "ComplexData":
            value_object = ComplexData.from_dict(raw_value)
        else:
            raise ValueError(f"Unsupported data type for Setting: {raw_value}")
        
        return cls(
            value=value_object,
            system_name=system_name,
            symbolic_name=symbolic_name,
            description=description,
            optional=optional,
            private=private
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)
    
    @classmethod
    def from_json(cls, text_content: str) -> "Setting":
        return cls.from_dict(json.loads(text_content))