# Library import
import pathlib
from typing import Dict, Any
from utils import LinkScanner, load_file_metadata
import logging
from configurations import Configurations, Setting
from datavalue import PrimitiveData, ComplexData

# Classes definition
class LinkConstructor:
    def __init__(self,
        platform_objective: str,
        architecture_objective: str,
        application_rootpath: str
    ) -> None:
        # Instance properties assignment
        self.platform_objective = platform_objective
        self.architecture_objective = architecture_objective
        self.application_rootpath = application_rootpath
        
        # Instance properties definition
        self.base_resources: Dict[str, Any] = {} # Master table
        self.software_resources: Dict[str, Any] = {} # Final table
        self.application_scanner = LinkScanner(self.application_rootpath)
        self.logger = logging.getLogger("LinkBuilder")
    
    # Private methods
    def _verify_dependencies_integrity(self) -> bool:
        """Esta funcion verifica la integridad de dependencias de la tabla final"""
        pass
    
    def _enrich_base_table(self, scanner_node: dict, current_id: str = "") -> None:
        # 1. Procesar archivos en el nodo actual
        for filename in scanner_node["content"]["files"]:
            if not filename.endswith(".py"): 
                continue
            
            # Generar ID (notación de puntos)
            file_id = f"{current_id}.{filename[:-3]}".strip(".")
            file_path = pathlib.Path(scanner_node["path"]) / filename
            
            # Enriquecer con metadatos (Fase AST)
            metadata = load_file_metadata(str(file_path))
            
            if "__ELEMENT_NAME__" not in metadata:
                metadata["__ELEMENT_NAME__"] = file_id

            self.base_resources[file_id] = {
                "physical_path": str(file_path),
                "type": "FILE",
                "metadata": metadata
            }
    
        # 2. Procesar subdirectorios de forma recursiva
        for dir_name, dir_node in scanner_node["content"]["subdirectories"].items():
            new_id = f"{current_id}.{dir_name}".strip(".")
            
            # Si es un módulo, tratamos la carpeta como un recurso también
            if dir_node["is_module"]:
                init_path = pathlib.Path(dir_node["path"]) / "__init__.py"
                metadata = load_file_metadata(str(init_path)) # Cargar metadatos específicos del módulo
                metadata["__ELEMENT_NAME__"] = new_id
                    
                self.base_resources[new_id] = {
                    "physical_path": str(init_path),
                    "type": "MODULE",
                    "metadata": load_file_metadata(str(init_path))
                }
            
            # Seguir bajando en el árbol
            self._enrich_base_table(dir_node, new_id)
    
    def _hydrate_configuration(self, rid: str, descriptor: dict) -> Configurations:
        """
        Maneja la entrada de usuario para llenar el descriptor de configurations-stc.
        """
        config = Configurations.from_dict(descriptor)
        print(f"Requested configurations by the resource: {rid}")

        for setting_name in config.query_settings():
            setting = config.query_setting(setting_name)
            print(f"Setting: {setting_name}")
            print(f"    Symbolic name: {setting.symbolic_name}")
            print(f"    Description: {setting.description}")
            print(f"    Value descriptor:")
            print(f"        Data type: {setting.value.data_type}")
            print(f"        Maximum length: {setting.value.maximum_length}")
            print(f"        Minimum length: {setting.value.minimum_length}")
            print(f"        Maximum size: {setting.value.maximum_size}")
            print(f"        Minimum size: {setting.value.minimum_size}")
            print(f"        Possible values: {setting.value.possible_values}")
            print(f"    Is required: {setting.optional}")

            while True:
                value = input("> ")

                print(f"Validating input")
                if setting.value.data_type == int:
                    try:
                        value = int(value)
                    except TypeError:
                        print("The data type is not valid")
                        print("Try again")
                
                validation_result = setting.value.validate(value)
                if validation_result:
                    print("Validation success")
                    break
                else:
                    print("Error validating value")
                    print("Try again")
                
        return config

    # Public methods
    def recognize_resources(self) -> None:
        """Identifica y perfila los recursos almacenándolos en la tabla base"""
        # Launch application scan
        resources_tree = self.application_scanner.scan()
        
        # Limpiar tabla base antes de poblar
        self.base_resources = {}
        
        # Enrich the data (Flattening tree to Master Table)
        self._enrich_base_table(resources_tree)
        
    def depuration_stage(self) -> None:
        """Elimina recursos residuales de la tabla base"""
        self.logger.info(f"Starting depuration stage. Total resources: {len(self.software_resources)}")

        redundant = [rid for rid in self.base_resources.keys() if rid.endswith(".__init__")]
            
        for rid in redundant:
            del self.software_resources[rid]
            self.logger.debug(f"Deleted redundancy: {rid}")
        
        self.logger.info(f"Depuration finished. Unique resources: {len(self.software_resources)}")
        return True
     
    def compatibility_stage(self) -> None:
        """Elimina recursos incompatibles de la tabla de software final."""
        self.logger.info(f"Starting compatibility filter stage for platform: {self.platform_objective}, with architecture: {self.architecture_objective}")
        
        # Lista de IDs a eliminar para no mutar el dict durante la iteración
        to_remove = []
        
        self.logger.info(f"Supported platform: {self.platform_objective} | Supported architecture: {self.architecture_objective}")

        for rid, data in self.software_resources.items():
            metadata = data.get("metadata", {})
            res_type = metadata.get("__RESOURCE_TYPE__", "DYNAMIC")
            
            # 1. Los recursos estructurales son agnósticos y se mantienen siempre.
            if res_type == "STRUCTURAL":
                continue
                
            # 2. Validación de Plataforma
            platforms = metadata.get("__PLATFORM_COMPATIBILITY__", [])
            if self.platform_objective not in platforms and "ALL" not in platforms:
                to_remove.append(rid)
                self.logger.debug(f"Discarted by platform incompatibility: {rid}")
                continue
                
            # 3. Validación de Arquitectura
            archs = metadata.get("__ARCHITECTURE_COMPATIBILITY__", [])
            if self.architecture_objective not in archs and "ALL" not in archs:
                to_remove.append(rid)
                self.logger.debug(f"Discarted by architecture: {rid}")
                continue
                
        # Ejecutar la eliminación
        for rid in to_remove:
            del self.software_resources[rid]
            
        self.logger.info(f"Compatibility filter stage finished. Total compatible resources: {len(self.software_resources)}")
        return True
    
    def selection_stage(self) -> None:
        """Elimina recursos no seleccionados por el usuario"""
        self.logger.info("Iniciando fase de selección y configuración interactiva...")
                
        to_remove = []
        
        for rid, data in self.software_resources.items():
            metadata = data.get("metadata", {})
            
            # 1. Verificar si el recurso es seleccionable
            if not metadata.get("__SELECTABLE__", False):
                continue

            # 2. Interacción con el usuario para inclusión
            print(f"\n[?] Do you want to include the module: '{rid}'? (s/n): ", end="")
            user_choice = input().lower().strip()
            
            if user_choice != 's':
                to_remove.append(rid)
                self.logger.info(f"Module: '{rid}', discarted by the user")
                continue

            # 3. Verificación de configuraciones estáticas
            if metadata.get("__CONFIGURABLE__", False):
                self.logger.info(f"Configurating resource: {rid}")
                config_descriptor = metadata.get("__STATIC_CONFIGURATIONS__", {})
                
                if not config_descriptor:
                    self.logger.warning(f"The resource: {rid}, set: __CONFIGURABLE__ but it has no descriptor in: __STATIC_CONFIGURATIONS__")
                    continue

                # 4. Hidratación y Validación con configurations-stc
                try:
                    # Suponiendo que el descriptor ya viene como dict desde el AST
                    config_obj = self._hydrate_configuration(rid, config_descriptor)
                    
                    # Almacenamos el objeto de configuración serializado en los metadatos finales
                    # para que sea empaquetado por el LinkCompiler
                    data["metadata"]["__PACKAGED_CONFIGURATIONS__"] = config_obj.to_dict()
                    
                except Exception as e:
                    self.logger.error(f"Error on the configuration of the resource: {rid}: {str(e)}")
                    # Si falla la configuración crítica, podrías decidir si eliminar el módulo
        
        # Limpiar recursos no seleccionados
        for rid in to_remove:
            del self.software_resources[rid]
    
    def preparation_stage(self) -> None:
        """Solicita configuraciones de los recursos finales que lo requieran"""
        pass
    
    def build(self):
        """Construye y empaqueta una copia de software"""
        # Identify the base resources
        self.logger.info("Starting build process")
        self.logger.info("Starting resources recognition")
        recognized_resources = self.recognize_resources()
        #print(self.base_resources)

        for resource_name, data_profile in self.base_resources.items():
            self.logger.debug(f"Resource: {resource_name} | Type: {data_profile.get('type')} | Physical path: {data_profile.get('physical_path')} | Metadata: {data_profile.get('metadata')}")

        # Copy software resources
        self.software_resources = self.base_resources.copy()

        # Execute stages
        self.depuration_stage()
        self.compatibility_stage()
        self.selection_stage()
        self.preparation_stage()
    
        return True
    
    def compile(self) -> None:
        """Lanza el script de compilacion (LinkCompiler.sh)"""
        pass