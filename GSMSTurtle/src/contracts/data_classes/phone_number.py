# Library import
import phonenumbers
from ..data_classes.primitive_data import PrimitiveData

# Classes definition
class PhoneNumber:
    "This class represents a phone number represented in the standard universla format."

    def __init__(self,
        phone_number: str
    ) -> None:
        # Instance property definitions
        self.phone_number = PrimitiveData(
            data_type=str,
            minimum_length=1,
            maximum_length=50,
            possible_values=None,
            content=phone_number
        )

        # Validate the phone number (or raise exception)
        self.validate(self.phone_number.content)
    
    # Public methods
    def validate(self, data: str) -> bool:
        """This method allows to validate if a phone number is correct, following the universal standard:

            Returns:
                bool: true (success) / raise exception ValueError (wrong phone number format) 
        """
        
        try:
            phonenumber = phonenumbers.parse(data, None) # If is none: its currently international

            if not phonenumbers.is_valid_number(phonenumber):
                raise ValueError(f"Invalid phone number: {data}")
            
            return phonenumbers.format_number(
                phonenumber,
                phonenumbers.PhoneNumberFormat.E164
            )
        
        except phonenumbers.phonenumberutil.NumberParseException as Error:
            raise ValueError(str(Error))