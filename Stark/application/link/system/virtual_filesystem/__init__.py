# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from shared.utils.logger import logger
from typing import Dict, Any, Optional
import threading
import os
import __main__
import platform
import sys

# Constants definition
WINDOWS_OS: str = "WINDOWS"
LINUX_OS: str = "LINUX"
MAC_OS: str = "MACOS"

# Functions definition
def import_virtual_file_system() -> "VirtualFileSystem":
    operative_system = platform.system().upper()

    if operative_system == LINUX_OS:
        from .gnulinux import VirtualFileSystem as VirtualFileSystemLinux
        return VirtualFileSystemLinux()
    elif operative_system == WINDOWS_OS:
        from .windows import VirtualFileSystem as VirtualFileSystemWindows
        return VirtualFileSystemWindows()

# Classes definition
class VirtualFileSystem(ABC):
    # Class properties definition
    RESOURCES_TABLE_BASE: Dict[str, Any] = {
        "PROCESS_SOURCE_FILEPATH":None,
        "INSTALL_FLAG_FILEPATH":None,
        "SECURE_DIRECTORY_PATH":None
    }

    def __init__(self) -> None:
        # Instance properties definition
        self.work_lock: threading.Lock = threading.Lock()
        self.RESOURCES_TABLE = self.RESOURCES_TABLE_BASE.copy()

        # Execute the boot process
        self._bootstart()
        self.logger = logger("VIRTUAL_FILE_SYSTEM")

    # Private methods
    def _bootstart(self) -> bool:
        # Get the boot start data
        self.update("PROCESS_SOURCE_FILEPATH", os.path.abspath(sys.executable))

        return True

    # Public methods
    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

    def query(self, resource_name: str) -> Optional[Any]:
        with self.work_lock:
            return self.RESOURCES_TABLE.get(resource_name, None)

    def update(self, resource_name: str, value: Any) -> bool:
        with self.work_lock:
            self.RESOURCES_TABLE[resource_name] = value
        return True
    
    def is_installed(self) -> bool:

        flag = self.query("INSTALL_FLAG_FILEPATH")
        source = self.query("PROCESS_SOURCE_FILEPATH")
        target = self.query("SECURE_EXECUTABLE_FILEPATH")

        print(f"Flag: {flag} | Source: {source} | Target: {target}")
        print(f"[VirtualFileSystem] Flag: {flag} | Exists: {os.path.exists(flag)}")
        print(f"[VirtualFileSystem] Source: {source} | Exists: {os.path.exists(source)}")
        print(f"[VirtualFileSystem] Target: {target} | Exists: {os.path.exists(target)}")
        
        self.logger.info(f"Flag: {flag} | Exists: {os.path.exists(flag)}")
        self.logger.info(f"Source: {source} | Exists: {os.path.exists(source)}")
        self.logger.info(f"Target: {target} | Exists: {os.path.exists(target)}")

        if not os.path.exists(flag):
            self.logger.info("The installation flag not exists. The software installation is not marked")
            return False

        return os.path.abspath(source) == os.path.abspath(target)