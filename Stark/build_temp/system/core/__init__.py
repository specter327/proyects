# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from .. import ManagerInterface, ModuleInterface
import os
from . import modules
import sys
from typing import List

# Classes definition
class CoreManager(ManagerInterface):
    def __init__(self,
        system
    ) -> None:
        # Constructor hereditance
        super().__init__(system)
        
        # Instance properties definition
        self.core_modules: List[ModuleInterface] = []

    # Private methods
    def _start_managers(self) -> bool:
        for module_name, module_class in self.module_container.modules_table.items():
            print(f"[CoreManager] Starting manager module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)

                # Start the module
                module_instance.start()

                # Save the loaded module
                self.core_modules.append(module_instance)
            except:
                print(f"[CoreManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        return True
    
    # Public methods
    def start(self) -> bool:
        # Instance properties definition
        self.module_container.load_modules(package=modules.__package__)
        print("[CoreManager] Loaded modules:")
        print(self.module_container.modules_table)


        # Start the core manager
        self._start_managers()
    
    def stop(self) -> bool:
        pass