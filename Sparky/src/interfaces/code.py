# Library import
from ..data.classes import Text, PersonalizeProfile

# Functions definition
def personalize_text(text: str, data_table: dict) -> str:
    text = Text(text)
    profile = PersonalizeProfile(data_table)

    return profile.personalize_text(text)