# Library import
import pathlib
import ast
from typing import Any, Dict

# Classes definition
class LinkScanner:
    def __init__(self, root_path: str):
        self.root = pathlib.Path(root_path)

    def scan(self):
        """Inicia el análisis recursivo desde la raíz."""
        return self._recursive_scan(self.root)

    def _recursive_scan(self, current_path: pathlib.Path):
        """Analizador de profundidad para identificar el árbol de recursos."""
        node = {
            "path": str(current_path),
            "is_module": (current_path / "__init__.py").exists(),
            "content": {"files": [], "subdirectories": {}}
        }

        for item in current_path.iterdir():
            # Filtrado de residuos
            if item.name in ["__pycache__", ".pyc"] or item.name.startswith("."):
                continue

            if item.is_file():
                node["content"]["files"].append(item.name)
            elif item.is_dir():
                node["content"]["subdirectories"][item.name] = self._recursive_scan(item)

        return node

# Functions definition
def check_platform_compatibility(metadata: dict, target_os: str) -> bool:
    """Realiza la discriminación por compatibilidad de plataforma."""
    if metadata.get("__RESOURCE_TYPE__") == "STRUCTURAL":
        return True

    supported_platforms = metadata.get("__PLATFORM_COMPATIBILITY__", [])
    return target_os in supported_platforms
    
def is_compatible(metadata: dict, target_os: str, target_arch: str) -> bool:
    """Valida plataforma y arquitectura simultáneamente."""
    if metadata.get("__RESOURCE_TYPE__") == "STRUCTURAL":
        return True
    
    platforms = metadata.get("__PLATFORM_COMPATIBILITY__", [])
    architectures = metadata.get("__ARCHITECTURE_COMPATIBILITY__", [])
    
    return target_os in platforms and target_arch in architectures
    
def load_file_metadata(file_path: str) -> Dict[str, Any]:
    """Analiza estáticamente un archivo .py para extraer etiquetas dunder y dependencias."""
    metadata = {
        "__DEPENDENCIES_INTERNAL__": [],
        "__DEPENDENCIES_EXTERNAL__": []
    }
    path = pathlib.Path(file_path)

    if not path.exists() or path.suffix != ".py":
        return metadata

    try:
        with open(path, "r", encoding="utf-8") as source_file:
            tree = ast.parse(source_file.read())

        for node in ast.walk(tree):
            # 1. Extracción de Metadatos Dunder (Variables __KEY__)
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("__"):
                        try:
                            value = ast.literal_eval(node.value)
                            metadata[target.id] = value
                        except (ValueError, SyntaxError):
                            continue

            # 2. Detección de importaciones globales (import A, B as C)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    # Almacenamos el nombre base para clasificar luego
                    metadata["__DEPENDENCIES_EXTERNAL__"].append(alias.name)

            # 3. Detección de importaciones específicas/relativas (from X import Y)
            elif isinstance(node, ast.ImportFrom):
                # node.level > 0 indica importación relativa (., .., etc)
                dep_info = {
                    "module": node.module,
                    "level": node.level,
                    "names": [n.name for n in node.names]
                }
                # Guardamos la estructura para que el LinkScanner la resuelva
                metadata["__DEPENDENCIES_INTERNAL__"].append(dep_info)
                            
    except Exception as e:
        print(f"[!] Error analizando metadatos y dependencias en {file_path}: {e}")

    return metadata

def resolve_fully_qualified_name(current_fqn: str, dep_module: str, level: int) -> str:
    """Resuelve un import relativo a un FQN absoluto."""
    if level == 0:
        return dep_module if dep_module else ""
    
    parts = current_fqn.split('.')
    # En Python, 'from . import x' tiene level=1 y elimina 0 partes del path del paquete,
    # pero 'from .. import x' (level=2) elimina 1 parte. 
    # Ajustamos el truncamiento según la lógica de importación de Python:
    truncated = parts[:-level] 
    
    if dep_module:
        truncated.append(dep_module)
        
    return ".".join(truncated)