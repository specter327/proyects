# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from .. import ManagerInterface, ModuleInterface
import os
from . import modules
import shutil
import traceback
import sys
import subprocess
from typing import Optional

# Classes definition
class InstallManager(ManagerInterface):
    # Private methods
    def _execute_preinstall(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PREINSTALL:
                # Skip the module
                continue

            print(f"[InstallManager] Starting pre-install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True
    
    def _execute_install(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PROINSTALL:
                # Skip the module
                continue
            
            print(f"[InstallManager] Starting install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True

    def _execute_postinstall(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_POSTINSTALL:
                # Skip the module
                continue
            
            print(f"[InstallManager] Starting post-install module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)
                
                # Start the module
                module_instance.start()
            except:
                print(f"[InstallManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True

    def _deploy_resources(self) -> bool:
        process_source = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        secure_directory = self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")

        new_process_name = "dbus-monitor"
        target_path = os.path.join(secure_directory, new_process_name)
        
        try:
            shutil.copy2(process_source, target_path)

            os.chmod(target_path, 0o700)
            print("[InstallManager] Program file deployed to:", target_path)

            # Re-name the new destination file
            self.system.virtual_file_system.update("PROCESS_SOURCE_FILEPATH", os.path.join(secure_directory, new_process_name))
            return True
        except:
            traceback.print_exc()
            return False

    def _deploy_install_flag(self) -> bool:
        try:
            install_flag_filepath = self.system.virtual_file_system.query("INSTALL_FLAG_FILEPATH")
            file = open(
                file=install_flag_filepath,
                mode='w',
                encoding="UTF-8"
            )
            file.close()
        except:
            traceback.print_exc()
            return False
        
        return True
    
    def _respawn_system(self) -> Optional[bool]:
        vfs = self.system.virtual_file_system
        new_executable = vfs.query("PROCESS_SOURCE_FILEPATH")

        print(f"[InstallManager] Handing off execution to: {new_executable}")
        
        try:
            # Popen con start_new_session=True para que no muera al cerrar la terminal
            # Redirigimos streams a DEVNULL para no dejar rastro de salida
            subprocess.Popen(
                [new_executable],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                detach=True if os.name == 'nt' else False # Manejo para Windows en el futuro
            )
            
            # Suicidio limpio del proceso instalador
            print("[InstallManager] Installation complete. Exiting original process.")
            sys.exit(0)
            
        except Exception as e:
            print(f"[InstallManager] Error during respawn: {e}")
            return False

    # Public methods
    def start(self) -> bool:
        # Instance properties definition
        self.module_container.load_modules(package=modules.__package__)
        print("Loaded modules:")
        print(self.module_container.modules_table)

        # Start the install manager
        if self.system.virtual_file_system.is_installed():
            print("[Link] The software is installed")
        else:
            print("[Link] The software is not installed. Proceeding with the installation...")
            self.install()

    def stop(self) -> bool:
        pass

    def install(self) -> bool:
        # Execute the pre-install modules
        self._execute_preinstall()

        # Verify the existence of the secure directory
        if os.path.exists(self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")):
            print("The secure directory path already exists")
        else:
            os.mkdir(self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH"))
            print("[InstallManager] Secure directory path created successfully")
            
        # Deploy software resources
        if not self._deploy_resources():
            return False

        # Execute the install modules
        self._execute_install()

        # Deploy the installed flag
        if not self._deploy_install_flag():
            return False
        
        # Execute the post-install modules
        self._execute_postinstall()

        # Return results
        return True
    
class InstallationModule(ModuleInterface, ABC):
    # Class properties definition
    INSTALL_STAGE_UNDEFINED: str = "UNDEFINED"
    INSTALL_STAGE_PREINSTALL: str = "PRE-INSTALL"
    INSTALL_STAGE_PROINSTALL: str = "PRO-INSTALL"
    INSTALL_STAGE_POSTINSTALL: str = "POST-INSTALL"

    INSTALL_STAGE: str = INSTALL_STAGE_UNDEFINED