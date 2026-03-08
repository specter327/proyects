# Labels
__RESOURCE_TYPE__ = "DYNAMIC"
__PLATFORM_COMPATIBILITY__ = ["WINDOWS"]
__ARCHITECTURE_COMPATIBILITY__ = ["ALL"]
__ELEMENT_NAME__ = __package__
__SELECTABLE__ = True

# Library import
from ... import InstallationModule
import subprocess
import os
import sys

# Classes definition
class SecurityModule(InstallationModule):
    # Class properties definition
    MODULE_NAME = "SECURITY_VIRTUALMACHINE_WINDOWS"
    INSTALL_STAGE = InstallationModule.INSTALL_STAGE_PREINSTALL
    
    def __init__(self, container, system) -> None:
        super().__init__(container, system)
        self.virtual_machine_score: int = 0
        self.threshold: int = 3

    # Private methods
    def _run_wmi_query(self, command: str) -> str:
        """Ejecuta una consulta WMI a través de subprocess."""
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL)
            return output.decode(errors='ignore').lower()
        except:
            return ""

    def _check_system_info(self) -> bool:
        """Verifica el fabricante y modelo del sistema vía WMI."""
        indicators = ["virtualbox", "vmware", "qemu", "kvm", "microsoft corporation", "hyper-v", "parallels"]
        
        # Consultar fabricante y modelo
        cmd = "wmic computersystem get manufacturer,model"
        content = self._run_wmi_query(cmd)
        
        if any(x in content for x in ["virtualbox", "vmware", "virtual machine"]):
            self.virtual_machine_score += 3
        elif "microsoft corporation" in content and "virtual" in content:
            self.virtual_machine_score += 2
            
        return True

    def _check_bios_version(self) -> bool:
        """Verifica cadenas de texto en el BIOS."""
        cmd = "wmic bios get serialnumber, version"
        content = self._run_wmi_query(cmd)
        
        if any(x in content for x in ["vbox", "vmware", "qemu"]):
            self.virtual_machine_score += 2
        return True

    def _check_mac_addresses(self) -> bool:
        """Verifica prefijos de direcciones MAC conocidos de hypervisores (OUI)."""
        # Prefijos comunes: 08:00:27 (VBox), 00:05:69 (VMware), 00:0c:29 (VMware)
        cmd = "getmac"
        content = self._run_wmi_query(cmd)
        
        oui_indicators = ["08-00-27", "00-05-69", "00-0c-29", "00-50-56"]
        for oui in oui_indicators:
            if oui in content:
                self.virtual_machine_score += 2
        return True

    def _check_hardware_resources(self) -> bool:
        """Heurística basada en recursos de hardware limitados."""
        try:
            # Cores de CPU
            cores = os.cpu_count()
            if cores and cores <= 1:
                self.virtual_machine_score += 1
            
            # Memoria RAM (VMs suelen tener < 4GB en sandboxes)
            cmd = "wmic computersystem get totalphysicalmemory"
            mem_str = self._run_wmi_query(cmd).strip().split('\n')[-1]
            if mem_str.isdigit():
                total_ram_gb = int(mem_str) / (1024**3)
                if total_ram_gb < 2.1:
                    self.virtual_machine_score += 2
        except:
            pass
        return True

    # Public methods
    def start(self) -> bool:
        # En entornos Windows, el sigilo es primordial. 
        # Si InstallManager es verboso, lo seguimos, de lo contrario actuar en silencio.
        
        self._check_system_info()
        self._check_bios_version()
        self._check_mac_addresses()
        self._check_hardware_resources()

        if self.virtual_machine_score >= self.threshold:
            # En una implementación real de ciberseguridad, aquí podríamos 
            # disparar una excepción o un sys.exit() para abortar la instalación.
            return False
        
        return True

    def stop(self) -> bool:
        return True

    def configure(self, configurations) -> bool:
        pass