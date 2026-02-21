# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
from .configurations import ConfigurationsManager
from .virtual_filesystem import import_virtual_file_system
from abc import ABC, abstractmethod
from configurations import Configurations
from typing import Dict, List, Tuple
import traceback
import os
import inspect
import importlib

# Classes definition
class System:
    def __init__(self) -> None:
        # Load the configurations manager
        self.configurations_manager = ConfigurationsManager()

        # Load the virtual file system
        from .install import InstallManager
        from .core import CoreManager

        self.virtual_file_system = import_virtual_file_system()
        self.install_manager = InstallManager(self)
        self.core_manager = CoreManager(self)
        
    # Public methods
    def start(self) -> bool:
        # Start the virtual file system
        self.virtual_file_system.start()

        # Start the install manager
        self.install_manager.start()
        
        # Execute the system
        self.execute()

        # Return results
        return True

    def execute(self) -> bool:
        self.core_manager.start()
        
        pass

    def stop(self) -> bool:
        pass

class ManagerInterface(ABC):
    def __init__(self,
        system: "System"
    ) -> None:
        # Instance properties assignment
        self.system = system

        # Instance properties definition
        self.module_container = ModulesContainer()
    
    # Public methods
    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

class ModuleInterface(ABC):
    # Class properties definition
    MODULE_NAME: str = "UNDEFINED"
    TYPE: str = "MODULE"
    PLATFORM_WINDOWS: str = "WINDOWS",
    PLATFORM_GNU_LINUX: str = "GNU/LINUX",
    PLATFORM_MAC_OS: str = "MACOS"
    COMPATIBILITY: tuple = ()

    def __init__(self, 
        container: "ModulesContainer",
        system: System
    ) -> None:
        # Instance properties definition
        self.active: bool = False
        self.configurated: bool = False
        self.configurations: Configurations = None
        self.container = container
        self.system = system
    
    # Private methods
    def _set_status(self, active: bool) -> bool:
        self.active = active
        return True

    def _set_configurated(self, configurated: bool) -> bool:
        self.configurated = configurated
        return True

    # Public methods
    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

    @abstractmethod
    def configure(self, configurations: Configurations) -> bool: raise NotImplementedError

class ModulesContainer:
    def __init__(self) -> None:
        # Instance properties definition
        self.modules_table: Dict[str, ModuleInterface] = {}
    
    # Private methods
    # Private methods
    @staticmethod
    def _filter_resource(base_resource: str, resource: str) -> bool:
        full_path = os.path.join(base_resource, resource)
        # 1. Must be a directory and not start with dunder
        if not os.path.isdir(full_path) or resource.startswith("__"):
            return True
        # 2. CRITICAL: Must contain __init__.py to be a valid package
        if not os.path.exists(os.path.join(full_path, "__init__.py")):
            return True
        return False
    
    # Public methods
    def start(self) -> bool:
        self.load_modules()
        return True
    
    def stop(self) -> bool:
        return True
    
    def query_modules(self) -> List[str]:
        return list(self.modules_table.keys())
    
    def query_module(self, module_name: str) -> ModuleInterface | None:
        if not module_name in self.modules_table: return None

        return self.modules_table.get(module_name)
    
    def load_modules(self, package: str = None) -> int:
        target_package = package if package else __package__
        current_modules = self.import_modules(package=target_package)
        
        for module_module, module_class in current_modules:
            print("Loaded module:", module_module)

            name = getattr(module_class, "MODULE_NAME", "UNKNOWN")
            self.modules_table[name] = module_class
        
        return len(current_modules)

    @classmethod
    def import_modules(cls, package: str = None, base_path: str = None) -> List[Tuple]:
        if package is None: package = __package__
        
        current_path = base_path
        
        # Resolución robusta de la ruta del paquete
        if current_path is None and package:
            try:
                # Importamos el paquete de módulos para inspeccionar su ubicación real
                target_mod = importlib.import_module(package)
                if hasattr(target_mod, "__path__"):
                    current_path = target_mod.__path__[0]
                elif hasattr(target_mod, "__file__"):
                    current_path = os.path.dirname(target_mod.__file__)
            except Exception as e:
                print(f"[ModulesContainer] Fallo al localizar paquete {package}: {e}")
        
        print("Current path:", current_path)
        if not current_path or not os.path.exists(current_path): 
            print("The current path not exists")
            return []

        try:
            current_resources = os.listdir(current_path)
            print("Current resources:")
            print(current_resources)
        except FileNotFoundError:
            print("File not found error")
            return []
            
        loaded_modules: List[Tuple] = []

        for resource in current_resources:
            if cls._filter_resource(base_resource=current_path, resource=resource): 
                continue

            try:
                full_module_name = f"{package}.{resource}"
                module = importlib.import_module(full_module_name)
                # ... (resto de la lógica de inspección)
            except ModuleNotFoundError as e:
                print(f"[ModuleContainer] Error on importing module: {resource}. Missing dependency: {e.name}")
                # Si e.name != full_module_name, el fallo es una dependencia interna como 'shared'
                traceback.print_exc()

            try:
                full_module_name = f"{package}.{resource}"
                module = importlib.import_module(full_module_name)

                match_content: bool = False
                match_class: object = None

                for name, element in inspect.getmembers(module):
                    if inspect.isclass(element):
                        # Obtenemos los nombres de las clases en la jerarquía (MRO)
                        # Esto es inmune a si la clase 'ModuleInterface' proviene de distintas importaciones
                        class_hierarchy = [base.__name__ for base in inspect.getmro(element)]
                        
                        if "ModuleInterface" in class_hierarchy \
                            and not inspect.isabstract(element) \
                            and element.__module__ == module.__name__:
                            
                            match_content = True
                            match_class = element
                            break

                if match_content:
                    loaded_modules.append((module, match_class))
                    
            except Exception as Error:
                print(f"[ModuleContainer] Error on importing module: {resource}. [{type(Error).__name__}]")
                # En producción, considera logging.error en lugar de traceback
                # traceback.print_exc() 
        
        return loaded_modules