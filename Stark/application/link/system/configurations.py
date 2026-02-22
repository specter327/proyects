# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
import sys
import os

# Constants definition
ConfigurationsTable = {}
    
# Classes definition
class ConfigurationsManager:
    _instance = None

    def __new__(cls):
        """Implementación de Singleton para acceso global único."""
        if cls._instance is None:
            cls._instance = super(ConfigurationsManager, cls).__new__(cls)
            # Al inicializarse, ya tiene acceso a la tabla inyectada
            cls._instance._table = ConfigurationsTable
        return cls._instance

    def query_configuration(self, element_name: str) -> dict:
        """Recupera la configuración de un elemento por su identificador único."""
        return self._table.get(element_name, {})

    def get_all(self) -> dict:
        """Retorna la base de datos completa de configuración."""
        return self._table
