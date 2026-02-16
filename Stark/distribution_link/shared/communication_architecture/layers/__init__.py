# Library import
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional
import os
import importlib
import importlib.util
import inspect
import traceback

# Constants definition
LAYER_TYPE_STRUCTURAL: str = "STRUCTURAL"
LAYER_TYPE_SESSION: str = "SESSION"
LAYER_TYPE_UNDEFINED: str = "UNDEFINED"

# Classes definition
class LayerInterface(ABC):
    # Class properties definition
    LAYER_NAME: str = "NOT_ASSIGNED"
    TYPE: str = "LAYER"
    LAYER_ROLE_ACTIVE: str = "ACTIVE"
    LAYER_ROLE_PASSIVE: str = "PASSIVE"
    LAYER_TYPE = LAYER_TYPE_UNDEFINED
    
    @property
    def NAME(self) -> str:
        return self.LAYER_NAME
    
    def __init__(self, layers_container: "LayerContainer") -> None:
        # Instance properties definition
        self.layers_container = layers_container

    @abstractmethod
    def query_modules(self) -> List[str]: raise NotImplementedError

    @abstractmethod
    def query_module(self, module_name: str) -> "ModuleInterface": raise NotImplementedError
    
    @abstractmethod
    def configure(self, configurations: object) -> bool: raise NotImplementedError

    @abstractmethod
    def start(self) -> bool: raise NotImplementedError

    @abstractmethod
    def stop(self) -> bool: raise NotImplementedError

class LayerContainer:
    def __init__(self) -> None:
        # Instance properties definition
        self.layers_table: Dict[str, LayerInterface] = {}
        
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
    def load_layers(self, package: str = None) -> int:
        # Import the available layers
        target_package = package if package else __package__
        current_layers = self.import_layers(package=target_package)

        # Insert the loaded layers
        for layer_module, layer_class in current_layers:
            if layer_class.LAYER_TYPE == LAYER_TYPE_STRUCTURAL:
                self.layers_table[layer_class.LAYER_NAME] = layer_class(self)
                print("Structural layer loaded and instanciated:", layer_class.LAYER_NAME)

            elif layer_class.LAYER_TYPE == LAYER_TYPE_SESSION:
                self.layers_table[layer_class.LAYER_NAME] = layer_class
                print("Session layer loaded:", layer_class.LAYER_NAME)

        return len(current_layers)

    def query_layers(self) -> List[str]:
        return list(self.layers_table.keys())
    
    def query_layer(self, layer_name: str,) -> LayerInterface | None:
        if layer_name not in self.layers_table: return None

        return self.layers_table.get(layer_name)
    
    def start(self) -> bool:
        self.load_layers()
        return True
    
    def stop(self) -> bool:
        return True
    
    @classmethod
    def import_layers(cls, package: str = None, base_path: str = None) -> List[Tuple]:
        # Determine package and path
        if package is None: package = __package__
        
        current_path = base_path
        if current_path is None and package:
            try:
                spec = importlib.util.find_spec(package)
                if spec and spec.submodule_search_locations:
                    current_path = spec.submodule_search_locations[0]
            except:
                pass
        
        if not current_path: return []

        try:
            current_resources = os.listdir(current_path)
        except FileNotFoundError:
            return []

        loaded_layers: List[Tuple] = []

        # Process every resource
        for resource in current_resources:
            # Filter other resources
            if cls._filter_resource(base_resource=current_path, resource=resource): continue

            # Process the layer resource
            try:
                # Try to import the layer using absolute import
                full_module_name = f"{package}.{resource}"
                layer = importlib.import_module(full_module_name)

                # Verify the module contents
                match_content: bool = False
                match_class: object = None

                for name, element in inspect.getmembers(layer):
                    if inspect.isclass(element):
                        # Verify if the class object heredate from the LayerInterface
                        if issubclass(element, LayerInterface) and element is not object and element is not LayerInterface:
                            match_content = True
                            match_class = element
                            break # Stop process

                if match_content:
                    # Save the module
                    loaded_layers.append(
                        (layer, match_class)
                    )
            except Exception as Error:
                print(f"[LayerContainer] Error on importing module: {resource}. [{type(Error).__name__}]")
                traceback.print_exc()

        # Return results
        return loaded_layers

class ModuleInterface(ABC):
    # Class properties definition
    MODULE_NAME: str = "NOT_ASSIGNED"
    TYPE: str = "MODULE"
    
    @property
    def NAME(self) -> str:
        return self.MODULE_NAME
    
    def __init__(self, layer: LayerInterface) -> None:
        # Instance properties definition
        self.configurations: object = None
        self.active: bool = False
        self.configurated: bool = False
        self.layer = layer

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
    def configure(self, configurations: object) -> bool: raise NotImplementedError

class ModuleContainer:
    def __init__(self) -> None:
        # Instance properties definition
        self.modules_table: Dict[str, object] = {}

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
            # FIX: Use MODULE_NAME for modules
            name = getattr(module_class, "MODULE_NAME", "UNKNOWN")
            self.modules_table[name] = module_class
        
        return len(current_modules)

    @classmethod
    def import_modules(cls, package: str = None, base_path: str = None) -> List[Tuple]:
        # Determine package and path logic
        if package is None: package = __package__
        
        current_path = base_path
        if current_path is None and package:
            try:
                spec = importlib.util.find_spec(package)
                if spec and spec.submodule_search_locations:
                    current_path = spec.submodule_search_locations[0]
            except:
                pass
        
        if not current_path: return []

        try:
            current_resources = os.listdir(current_path)
        except FileNotFoundError:
            return []
            
        loaded_modules: List[Tuple] = []

        for resource in current_resources:
            if cls._filter_resource(base_resource=current_path, resource=resource): continue
            
            try:
                # Importación absoluta
                full_module_name = f"{package}.{resource}"
                module = importlib.import_module(full_module_name)

                # Verify the module contents
                match_content: bool = False
                match_class: object = None

                for name, element in inspect.getmembers(module):
                    if inspect.isclass(element):
                        # Verify if the class object heredate from the ModuleInterface
                        if issubclass(element, ModuleInterface) and element is not object and element is not ModuleInterface:
                            match_content = True
                            match_class = element
                            break # Stop process

                if match_content:
                    # Save the module
                    loaded_modules.append(
                        (module, match_class)
                    )
            except Exception as Error:
                print(f"[ModuleContainer] Error on importing module: {resource}. [{type(Error).__name__}]")
                traceback.print_exc()
        
        # Return results
        return loaded_modules