# Library import
from typing import Dict, List
from .setting import Setting
import json

# Classes definition
class Configurations:
    "This class represents a set of settings of a device."

    def __init__(self) -> None:
        # Instance properties definition
        self.settings: Dict[str, Setting]= {}
    
    # Public methods
    def add_setting(self, setting: Setting) -> str:
        """This method append the setting to the local settings table.
            It validates if the system name of the setting currently exists: if already exists, raises a exception

            Returns:
                bool: true (sucess)/false (error)
        """

        system_name = setting.system_name.upper()

        # Validate the current existence
        if system_name in self.settings: raise KeyError(f"The system name: {system_name}, already exists in the current settings table: {str(self.settings.keys())}")

        # Append new settings to the settings table
        self.settings[system_name] = setting

        return system_name
    
    def query_settings(self) -> List[str]:
        "This method returns a list of strings that represents the system names of the currrent settings."
        return list(self.settings.keys())

    def query_setting(self, system_name: str) -> Setting:
        """This method search for a specified setting by its system name, and if exists, return the Setting instance object.
            If the setting not exists, it raises a key error.

            Returns:
                Setting instance object
        """
        system_name = system_name.upper()

        if system_name not in self.settings.keys(): raise KeyError(f"The specified system name setting key: {system_name}, not exists on the current settings table: {list(self.settings.keys())}")
        return self.settings.get(system_name)
    
    def delete_setting(self, system_name: str) -> bool:
        """This method deletes a setting object from the current local settings table. It raises a error if the setting not exists.
            
            Returns:
                bool: true (sucess)/false (error)
        """
        system_name = system_name.upper()

        if system_name not in self.settings.keys(): raise KeyError(f"The system name key: {system_name}, not exists in the current settings: {list(self.settings.keys())}")
        self.settings.pop(system_name)

        return True
    
    def to_dict(self) -> dict:
        settings = {}
        for setting_name in self.settings:
            setting_instance = self.settings.get(setting_name)
            settings[setting_name] = setting_instance.to_dict()
        return settings
    
    @classmethod
    def from_dict(cls, data: dict) -> "Configurations":
        configurations = cls()
        for setting_name in data:
            setting_datatable = data.get(setting_name)
            setting_instance = Setting.from_dict(setting_datatable)
            configurations.add_setting(setting_instance)

        return configurations
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4)

    @classmethod
    def from_json(cls, text_content: str) -> "Configurations":
        return cls.from_dict(json.loads(text_content))