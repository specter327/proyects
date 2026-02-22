# Library import
import pathlib
from typing import Dict, Any
from utils import LinkScanner, load_file_metadata, resolve_fully_qualified_name
import logging
from configurations import Configurations, Setting
from datavalue import PrimitiveData, ComplexData
import shutil
import PyInstaller.__main__
import os
import pprint

# Classes definition
class LinkConstructor:
    def __init__(self,
        platform_objective: str,
        architecture_objective: str,
        application_rootpath: str,
        preparation_path: str,
        output_path: str,
        application_name: str
    ) -> None:
        # Instance properties assignment
        self.platform_objective = platform_objective
        self.architecture_objective = architecture_objective
        self.application_rootpath = str(pathlib.Path(application_rootpath).resolve())
        self.preparation_path = pathlib.Path(preparation_path).resolve()
        self.output_path = output_path
        self.application_name = application_name
        
        # Instance properties definition
        self.base_resources: Dict[str, Any] = {} # Master table
        self.software_resources: Dict[str, Any] = {} # Final table
        self.application_scanner = LinkScanner(self.application_rootpath)
        self.logger = logging.getLogger("LinkBuilder")
    
    # Private methods
    def _verify_dependencies_integrity(self) -> bool:
        self.logger.info("Verifying dependency integrity...")
        selected_fqns = set(self.software_resources.keys())
        missing_critical = False

        for rid, data in list(self.software_resources.items()):
            internal_deps = data["metadata"].get("__RESOLVED_INTERNAL__", [])
            
            for dep in internal_deps:
                if dep not in selected_fqns:
                    # Si la dependencia es STRUCTURAL, la auto-incluimos sin preguntar
                    if dep in self.base_resources:
                        res_type = self.base_resources[dep].get("type")
                        if res_type == "STRUCTURAL":
                            self.software_resources[dep] = self.base_resources[dep]
                            selected_fqns.add(dep)
                            continue
                            
                        self.logger.warning(f"Resource '{rid}' requires '{dep}'. Auto-including.")
                        self.software_resources[dep] = self.base_resources[dep]
                        selected_fqns.add(dep)
                    else:
                        self.logger.error(f"CRITICAL: Resource '{rid}' depends on '{dep}', not found.")
                        missing_critical = True
        return not missing_critical

    def _enrich_base_table(self, scanner_node: dict, current_id: str = "") -> None:
        """
        Registra cada nodo del árbol. Si no tiene __init__.py, se registra como
        STRUCTURAL para mantener la integridad del FQN.
        """
        # 1. Registro del nodo actual (Directorio/Paquete)
        if current_id: # Evitar la raíz vacía
            is_module = scanner_node.get("is_module", False)
            init_path = pathlib.Path(scanner_node["path"]) / "__init__.py"
            
            # Si no tiene __init__, es un Namespace Package (Structural)
            self.base_resources[current_id] = {
                "physical_path": str(init_path) if is_module else scanner_node["path"],
                "type": "MODULE" if is_module else "STRUCTURAL",
                "metadata": load_file_metadata(str(init_path)) if is_module else {
                    "__RESOURCE_TYPE__": "STRUCTURAL",
                    "__SELECTABLE__": False
                }
            }

        # 2. Procesar archivos .py (excepto __init__.py que ya es la identidad del MODULE)
        for filename in scanner_node["content"]["files"]:
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            
            file_id = f"{current_id}.{filename[:-3]}".strip(".")
            file_path = pathlib.Path(scanner_node["path"]) / filename
            metadata = load_file_metadata(str(file_path))
            
            if "__ELEMENT_NAME__" not in metadata:
                metadata["__ELEMENT_NAME__"] = file_id

            self.base_resources[file_id] = {
                "physical_path": str(file_path),
                "type": "FILE",
                "metadata": metadata
            }
    
        # 3. Recursión
        for dir_name, dir_node in scanner_node["content"]["subdirectories"].items():
            self._enrich_base_table(dir_node, f"{current_id}.{dir_name}".strip("."))
            
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
            if hasattr(setting.value, "maximum_size"):
                print(f"        Maximum size: {setting.value.maximum_size}")
            
            if hasattr(setting.value, "minimum_size"):
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

    def _finalize_dependency_graph(self, resources: Dict[str, Any]):
        """
        Transforma dependencias relativas en FQN y clasifica entre 
        recursos internos (Stark) y externos (Librerías/PyPI).
        """
        all_internal_fqns = set(resources.keys())
        # Extraemos los namespaces raíz internos (ej: 'shared', 'system') 
        internal_root_namespaces = {fqn.split('.')[0] for fqn in all_internal_fqns}

        for fqn, data in resources.items():
            resolved_internal = set()
            resolved_external = set()
            
            # 1. Procesar Importaciones Globales (import X)
            for ext_dep in data['metadata'].get("__DEPENDENCIES_EXTERNAL__", []):
                if not ext_dep or ext_dep == "__main__": 
                    continue
                    
                base_module = ext_dep.split('.')[0]
                
                # Si el inicio del import coincide con un root interno, es interno 
                if base_module in internal_root_namespaces:
                    resolved_internal.add(ext_dep)
                else:
                    resolved_external.add(base_module)

            # 2. Procesar Importaciones Específicas (from X import Y)
            for dep in data['metadata'].get("__DEPENDENCIES_INTERNAL__", []):
                # AJUSTE TÉCNICO: Si es un MODULE (__init__), el nivel relativo 
                # cuenta desde una posición más profunda en el stack de Python.
                adjusted_level = dep['level']
                if data['type'] == "MODULE" and dep['level'] > 0:
                    adjusted_level = dep['level'] - 1

                target_fqn = resolve_fully_qualified_name(
                    current_fqn=fqn,
                    dep_module=dep['module'],
                    level=adjusted_level
                )
                
                if not target_fqn:
                    continue
                
                base_target_root = target_fqn.split('.')[0]

                # Validación de pertenencia al proyecto 
                if target_fqn in all_internal_fqns or base_target_root in internal_root_namespaces:
                    resolved_internal.add(target_fqn)
                else:
                    resolved_external.add(base_target_root)

            # Actualización de metadatos sanitizados 
            data['metadata']['__RESOLVED_INTERNAL__'] = list(resolved_internal)
            data['metadata']['__RESOLVED_EXTERNAL__'] = list(resolved_external)
            
    def _get_external_dependencies(self) -> list:
        """Consolida dependencias externas reales de los recursos seleccionados."""
        external_set = set()
        # Los built-ins de Python no necesitan ser declarados como hidden-imports
        python_builtins = {'sys', 'os', 'pathlib', 'abc', 'typing', 'time', 'logging', 'functools', 'itertools'}
        
        for rid, data in self.software_resources.items():
            deps = data["metadata"].get("__RESOLVED_EXTERNAL__", [])
            for d in deps:
                clean_dep = d.split('.')[0]
                if clean_dep and clean_dep not in python_builtins:
                    external_set.add(clean_dep)
        
        return sorted(list(external_set))    
    
    def _deploy_temporal_directory(self) -> bool:
        if self.preparation_path.exists():
            shutil.rmtree(self.preparation_path)
        
        self.preparation_path.mkdir(parents=True)

        return True

    def _deploy_software_resources(self) -> None:
        """Copia físicamente los archivos de software_resources al directorio de staging"""
        
        for rid, data in self.software_resources.items():
            src_path = pathlib.Path(data['physical_path'])
            
            # Calculamos la ruta relativa respecto a la raíz de la aplicación
            # para mantener la estructura de paquetes (shared/..., system/...)
            rel_path = src_path.relative_to(self.application_rootpath)
            dest_path = self.preparation_path / rel_path
            
            if src_path.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)
            else:
                # Caso de nodos STRUCTURAL (directorios puros)
                dest_path.mkdir(parents=True, exist_ok=True)

    def _inject_static_configurations(self) -> bool:
        """
        Localiza el archivo configurations.py en el staging y reemplaza 
        la constante ConfigurationsTable con los datos recolectados.
        """
        # 1. Definir la ruta del archivo en el directorio de preparación
        # Según tu árbol: system/configurations.py
        target_file = self.preparation_path / "system" / "configurations.py"
        
        if not target_file.exists():
            self.logger.error(f"Injection failed: {target_file} not found in staging.")
            return False

        # 2. Construir la tabla maestra a partir de software_resources
        master_table = {}
        for rid, data in self.software_resources.items():
            # Buscamos si el recurso tiene configuraciones empaquetadas
            packaged_config = data.get("metadata", {}).get("__PACKAGED_CONFIGURATIONS__")
            
            if packaged_config:
                # Usamos el __ELEMENT_NAME__ como llave de la tabla
                element_name = data["metadata"].get("__ELEMENT_NAME__", rid)
                master_table[element_name] = packaged_config
                self.logger.debug(f"Queuing configuration for injection: {element_name}")

        # 3. Leer el contenido actual del archivo
        with open(target_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 4. Generar la nueva tabla serializada en texto plano de Python
        # Usamos pprint para asegurar que la sintaxis sea válida
        formatted_table = pprint.pformat(master_table, indent=4, width=120)
        
        # 5. Reemplazar la línea de la constante
        new_lines = []
        injected = False
        for line in lines:
            if line.strip().startswith("ConfigurationsTable = {}"):
                new_lines.append(f"ConfigurationsTable = {formatted_table}\n")
                injected = True
                self.logger.info("Static configurations successfully injected into source.")
            else:
                new_lines.append(line)

        if not injected:
            self.logger.warning("Could not find 'ConfigurationsTable = {}' placeholder in configurations.py")
            return False

        # 6. Escribir el archivo modificado
        with open(target_file, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        return True

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

        redundant = [rid for rid in self.base_resources.keys() if rid.endswith(".pyc") or rid == "__pycache__"]
            
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
        self.logger.info("Starting selection stage")
                
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
        self._finalize_dependency_graph(self.base_resources)

        self.software_resources = self.base_resources.copy()

        # Execute stages
        self.depuration_stage()
        self.compatibility_stage()
        self.selection_stage()
        self.preparation_stage()
    
        # Verify the dependencies integrity
        validation_result = self._verify_dependencies_integrity()

        if validation_result:
            self.logger.info("Dependencies integrity verified successfully")
        else:
            self.logger.error(f"There was an error verifyng the dependencies integrity. Missing: {validation_result}")

        self.logger.info(f"External dependencies: {self._get_external_dependencies()}")

        self.logger.info("Deploying preparation directory")
        self._deploy_temporal_directory()

        self.logger.info("Deploying prepared software resources")
        self._deploy_software_resources()

        self.logger.info("Injecting hard-coded configurations")
        injection_result = self._inject_static_configurations()

        if injection_result:
            self.logger.info("Configurations injected successfully")
        else:
            self.logger.error("There was an error injecting the configurations")

        return True
    
    def compile(self) -> bool:
        self.logger.info(f"Iniciando fase de compilación: {self.application_name}")

        entry_script = self.preparation_path / f"{self.application_name}.py"
        
        # Definición del separador de rutas para PyInstaller (":" en Linux, ";" en Windows)
        sep = os.pathsep

        pyi_args = [
            str(entry_script),
            '--onefile',
            '--name', self.application_name,
            '--distpath', str(pathlib.Path(self.output_path).resolve()),
            '--workpath', str(self.preparation_path / "pyi_work"),
            '--specpath', str(self.preparation_path),
            '--paths', str(self.preparation_path),
            '--noconfirm',
            '--clean',
            '--log-level', 'WARN',
            # FORZAMOS la inclusión de las carpetas de módulos como DATA
            # Formato: "origen{sep}destino_dentro_del_binario"
            '--add-data', f"{self.preparation_path / 'system'}{sep}system",
            '--add-data', f"{self.preparation_path / 'shared'}{sep}shared",
        ]

        # Filtrado de Hidden Imports (Solo dependencias reales de terceros)
        internal_roots = ['shared', 'system', 'core', 'install', 'virtual_filesystem', 'gnulinux']
        external_deps = self._get_external_dependencies()
        
        for dep in external_deps:
            # Solo agregamos si no es parte de nuestra estructura interna
            if not any(dep.startswith(root) for root in internal_roots):
                pyi_args.extend(['--hidden-import', dep])

        try:
            PyInstaller.__main__.run(pyi_args)
            return True
        except Exception as e:
            self.logger.error(f"Fallo crítico: {str(e)}")
            return False