# Library import
from datavalue import PrimitiveData
from datavalue import ComplexData

# Classes definition
class Setting:
    "This class represent a setting, including its value and characteristics."

    def __init__(self,
        value: PrimitiveData | ComplexData,
        system_name: str,
        symbolic_name: str,
        description: str = "",
        optional: bool = False
        # default_value TODO !
    ) -> None:
        # Instance property definition
        self.system_name = system_name.upper() # Serialized in uppercase
        self.symbolic_name = symbolic_name
        self.description = description
        self.value = value
        self.optional = optional
    
    # Public methods
    def to_dict(self) -> dict:
        "This method serializes the configuration to a dict data structure."
        return {
            "SYSTEM_NAME":self.system_name,
            "SYMBOLIC_NAME":self.symbolic_name,
            "DESCRIPTION":self.description,
            "VALUE":self.value.to_dict(),
            "OPTIONAL":self.optional
        }