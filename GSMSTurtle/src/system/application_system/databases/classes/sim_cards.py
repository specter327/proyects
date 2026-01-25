# Library import
import time
from . import Database
from typing import Dict, Any, Optional, List

# Classes definition
class SIMCardsDatabase(Database):
    def __init__(self,
        storage_path: str
    ) -> None:
        # Class base database hereditance
        super().__init__(
            file_name="simcards",
            storage_path=storage_path
        )

        # Establecer conexión e inicializar tablas
        if self.connect():
            self._initialize_database()
        
    # Private methods
    def _initialize_database(self):
        operation = """
        CREATE TABLE IF NOT EXISTS sim_cards (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CCID TEXT UNIQUE NOT NULL,
            REGIST_DATE TEXT NOT NULL
        );
        """

        try:
            self._execute_write(operation)
            return True
        except Exception as e:
            # Integración con sistema de logs en entorno de producción
            print(f"[SIMCardsDatabase] Error de inicialización: {e}")
            return False
    
    # Public methods
    def regist_sim_card(self, ccid: str) -> int | bool:
        operation = """
        INSERT INTO sim_cards (CCID, REGIST_DATE) 
        VALUES (?, ?);
        """
        # Formato de fecha legible (ISO 8601) o podrías usar str(int(time.time()))
        current_date = time.strftime('%Y-%m-%d %H:%M:%S')
        parameters = (ccid, current_date)
        
        try:
            return self._execute_write(operation, parameters)
        except Exception:
            return False
    
    def get_sim_card(self, ccid: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM sim_cards WHERE CCID = ?;"
        return self._execute_read(query, (ccid,), fetch_one=True)

    def delete_sim_card(self, index: int) -> bool:
        operation = "DELETE FROM sim_cards WHERE INDEX_ID = ?;"
        return self._execute_write(operation, (index,)) > 0
    
    def query_sim_cards(self) -> List[Dict[str, Any]]:
        operation = "SELECT * FROM sim_cards"
        return self._execute_read(operation, fetch_one=False)