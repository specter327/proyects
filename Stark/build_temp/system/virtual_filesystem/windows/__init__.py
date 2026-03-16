# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["WINDOWS"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = False

# Library import
from .. import VirtualFileSystem
import os
import sys

# Classes definition
class VirtualFileSystem(VirtualFileSystem):
    # Public methods
    def start(self) -> bool:
        appdata_path = os.getenv("APPDATA")
        secure_path = os.path.join(appdata_path, "Microsoft", "Protect", "Service")

        os.makedirs(secure_path, exist_ok=True)

        executable_name = os.path.basename(sys.executable)
        secure_executable = os.path.join(secure_path, executable_name)

        self.update("SECURE_DIRECTORY_PATH", secure_path)
        self.update("SECURE_EXECUTABLE_FILEPATH", secure_executable)
        self.update("INSTALL_FLAG_FILEPATH", os.path.join(secure_path, "svc_lock.dat"))

        return True

    def stop(self) -> bool:
        return True