# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["GNU/LINUX"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__ELEMENT_NAME__ = __package__
__SELECTABLE__ = True

# Library import
from ... import InstallationModule
import subprocess
import os
import __main__
import traceback

# Classes definition
class SecurityModule(InstallationModule):
    # Class properties definition
    MODULE_NAME = "SECURITY_VIRTUALMACHINE_LINUX"
    INSTALL_STAGE = InstallationModule.INSTALL_STAGE_PREINSTALL
    COMPATIBILITY = (InstallationModule.PLATFORM_GNU_LINUX, )
    
    def __init__(self,
        container,
        system
    ) -> None:
        # Constructor hereditance
        super().__init__(container, system)

        # Instance properties definition
        self.virtual_machine_score: int = 0
        self.threshold: int = 3

    # Private methods
    def _check_cpu_flags(self) -> bool:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                if "hypervisor" in f.read():
                    self.virtual_machine_score += 2
        
        return True
    
    def _check_dmi_information(self) -> bool:
        indicators = ["vbox", "vmware", "qemu", "kvm", "virtualbox"]
        paths = [
            "/sys/class/dmi/id/product_name",
            "/sys/class/dmi/id/sys_vendor"
        ]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read().lower()
                    if any(x in content for x in indicators):
                        self.virtual_machine_score += 2
        
        return True
    
    def _check_hardware_resources(self) -> bool:
        try:
            cores = os.cpu_count()
            if cores and cores < 2:
                self.virtual_machine_score += 1
        except:
            pass
        finally:
            return True
    
    # Public methods
    def start(self) -> bool:
        print(f"[{self.MODULE_NAME}] Starting module...")
        # Execute list of checks
        self._check_cpu_flags()
        self._check_dmi_information()
        self._check_hardware_resources()

        # Determine if the software is in a virtual machine
        if self.virtual_machine_score >= self.threshold:
            print(f"[{self.MODULE_NAME}] Virtual environment detected (Score: {self.score}). Aborting.")
            return False
        
        print(f"[{self.MODULE_NAME}] Environment seems safe.")
        return True

    def stop(self) -> bool:
        pass

    def configure(self, configurations) -> bool:
        pass