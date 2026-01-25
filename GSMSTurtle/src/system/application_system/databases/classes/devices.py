import time
from . import Database
from typing import Dict, Any, Optional

# Classes definition
class DevicesDatabase(Database):
    def __init__(self, storage_path: str) -> None:
        # Inicialización de la base de datos de dispositivos
        super().__init__(file_name="devices", storage_path=storage_path)
        
        # Establecer conexión e inicializar tablas
        if self.connect():
            self._initialize_database()

    # Private methods
    def _initialize_database(self) -> bool:
        operation = """
        CREATE TABLE IF NOT EXISTS devices (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            IMEI TEXT UNIQUE NOT NULL,
            REGIST_DATE INTEGER NOT NULL
        );
        """
        try:
            self._execute_write(operation)
            return True
        except Exception as e:
            # En un entorno profesional, aquí se integraría el sistema de Logs
            print(f"[DevicesDatabase] Error de inicialización: {e}")
            return False
    
    # Public methods
    def regist_device(self, imei: str) -> int | bool:
        operation = "INSERT OR IGNORE INTO devices (IMEI, REGIST_DATE) VALUES (?, ?);"
        parameters = (imei, int(time.time()))
        
        return self._execute_write(operation, parameters)

    def get_device(self, imei: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM devices WHERE IMEI = ?;"
        return self._execute_read(query, (imei,), fetch_one=True)

    def delete_device(self, index: int) -> bool:
        operation = "DELETE FROM devices WHERE INDEX_ID = ?;"
        return self._execute_write(operation, (index,)) > 0