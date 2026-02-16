# Library import
from .. import VirtualFileSystem
from pathlib import Path
import os

# Classes definition
class VirtualFileSystem(VirtualFileSystem):
    pass

    # Public methods
    def start(self) -> bool:
        print("Starting VirtualFileSystem for GNU/Linux...")

        # Define the secure directory path
        homepath = Path.home()
        secure_path = os.path.join(homepath, ".local", "share", "system-service")

        # Set the secure directory path
        self.update("SECURE_DIRECTORY_PATH", secure_path)

        # Define the installation flag filepath
        self.update("INSTALL_FLAG_FILEPATH", os.path.join(secure_path, ".service_lock"))

        return True

    def stop(self) -> bool:
        return True