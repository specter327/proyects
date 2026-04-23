# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["GNU/LINUX"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = False

# Library import
from .. import VirtualFileSystem
from pathlib import Path
import os
from shared.utils import debug

# Classes definition
class VirtualFileSystem(VirtualFileSystem):
    pass

    # Public methods
    def start(self) -> bool:
        print("Starting VirtualFileSystem for GNU/Linux...")

        # Define the secure directory path
        homepath = Path.home()
        secure_path = os.path.join(homepath, ".local", "share", "system-service")
        secure_executable_filepath = os.path.join(homepath, ".local", "share", "system-service", debug.get_current_executable())

        # Set the secure directory path
        self.update("SECURE_DIRECTORY_PATH", secure_path)

        # Define the installation flag filepath
        self.update("INSTALL_FLAG_FILEPATH", os.path.join(secure_path, ".service_lock"))

        # Define the secure executable filepath
        self.update("SECURE_EXECUTABLE_FILEPATH", secure_executable_filepath)

        return True

    def stop(self) -> bool:
        return True