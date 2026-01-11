# Library import
from typing import List, Dict, Any

# Classes definition
class Text:
    "This class represents editable text and contains all the properties and methods for its high-level manipulation and use."
    
    def __init__(self,
        text_content: str
    ) -> None:
        # Instance property assignment
        self.text_content = text_content
    
    # Public methods
    def query_tokens(self, tokens: List[str]) -> List[str]:
        "This method allows the identification of personalization keys present in the textual content."
        
        # Data creation
        present_keys: List[str] = []
        
        # Search and detect every key on the PersonalizeProfile
        for key in tokens:
            if key in self.text_content:
                # Identify the present keys
                present_keys.append(key)
        
        # Return results
        return present_keys

class PersonalizeProfile:
    "This class represents a data profile for text personalization. It includes all properties and methods related to this aspect."
    
    # Class properties definition
    KEY_PREFIX: str = "{{"
    KEY_SUFFIX: str = "}}"
    NOTATION_SEPARATOR: str = "."
    
    def __init__(self, data_profile: dict) -> None:
        # Instance properties assignment
        self.data_profile: Dict[str, Any] = data_profile
        self.normalized_profile: Dict[str, Any] = self._normalize_profile()

    # Private methods
    def _format_normalized_key(self, key: str) -> str:
        return f"{self.KEY_PREFIX}{key}{self.KEY_SUFFIX}" 
    
    def _normalize_profile(
        self,
        data: Dict[str, Any] | None = None,
        parent_key: str = ""
    ) -> Dict[str, Any]:
        "This method normalizes a data table into a set of unique keys: direct values, ready for replacement."
        
        # Verify the data received
        if data is None:
            data = self.data_profile

        # Create a new keys table
        keys: Dict[str, Any] = {}

        # Process and normalize every key with recursion execution
        for key, value in data.items():
            full_key = (
                f"{parent_key}{self.NOTATION_SEPARATOR}{key}"
                if parent_key
                else key
            )

            if isinstance(value, dict):
                keys.update(self._normalize_profile(value, full_key))
            else:
                keys[full_key] = value

        # Return results
        return keys

    # Public methods
    def personalize_text(self, text: Text) -> str:
        "This method receives a Text object, identifies the unique keys present in it, and replaces them with their corresponding values, delivering a custom text according to the current normalized table."
        
        # Personalize text content
        new_text = text.text_content
        
        for key, value in self.normalized_profile.items():
            token = self._format_normalized_key(key)
            
            if token in new_text:
                new_text = new_text.replace(token, str(value))

        # Return results
        return new_text