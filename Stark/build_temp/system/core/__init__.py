# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from abc import ABC, abstractmethod
from .. import ManagerInterface, ModuleInterface
from shared.utils.logger import logger
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
        self.logger = logger("CORE_MANAGER")

    # Private methods
    def _start_managers(self) -> bool:
        self.logger.info("Starting core manager modules")
        for module_name, module_class in self.module_container.modules_table.items():
            print(f"[CoreManager] Starting manager module: {module_name}")
            self.logger.info(f"Starting module: {module_name}")

            try:
                # Instance the module
                module_instance = module_class(self.module_container, self.system)

                # Start the module
                self.logger.info(f"Starting module: {module_name}")
                start_result = module_instance.start()
                self.logger.info(f"Module start result: {start_result}")

                # Save the loaded module
                self.core_modules.append(module_instance)
            except:
                self.logger.error(f"Error starting the module: {module_name}")
                print(f"[CoreManager] Error starting the module: {module_name}")
                continue
        
        # Return results
        self.logger.info("Finishing core manager start modules")
        return True
    
    # Public methods
    def start(self) -> bool:
        self.logger.info("Starting core manager")

        # Instance properties definition
        self.module_container.load_modules(package=modules.__package__)
        print("[CoreManager] Loaded modules:")
        print(self.module_container.modules_table)
        self.logger.info(f"Available loaded modules: {self.module_container.query_modules()}")

        # Start the core manager
        self._start_managers()
        self.logger.info("Stopping core manager")
        return True
    
    def stop(self) -> bool:
        self.logger.info("Stopping core manager")
        pass
        self.logger.info("Core manager stopped")
        return True