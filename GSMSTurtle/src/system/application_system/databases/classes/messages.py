# Library import
import time
from . import Database
from typing import Dict, Any, Optional, List

# Classes definition
class MessagesDatabase(Database):
    def __init__(self,
        storage_path: str
    ) -> None:
        # Base class database hereditance
        super().__init__(
            file_name="messages",
            storage_path=storage_path
        )

        # Initialize the database connection
        if self.connect():
            self._initialize_database()
    
    # Private methods
    def _initialize_database(self):
        operation = """
        CREATE TABLE IF NOT EXISTS messages (
            INDEX_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            IMEI TEXT NOT NULL,
            CCID TEXT NOT NULL,
            ID TEXT UNIQUE NOT NULL,
            REGIST_DATE INTEGER NOT NULL,
            CONTENT TEXT NOT NULL,
            STATUS TEXT CHECK(STATUS IN ('READ', 'NOT_READ', 'PENDING')) NOT NULL,
            TYPE TEXT CHECK(TYPE IN ('SENT', 'RECEIVED')) NOT NULL,
            DESTINATARY TEXT NOT NULL
        );
        """
        try:
            self._execute_write(operation)
            return True
        except Exception as e:
            print(f"[MessagesDatabase] Error de inicialización: {e}")
            return False
    
    # Public methods
    def regist_message(self,
            unique_id: str,
            imei: str,
            ccid: str,
            content: str,
            message_type: str,
            status: str,
            destinatary: str
        ) -> int | bool:
            # Se añade DESTINATARY a la lista de columnas y se asegura la correspondencia con ?
            operation = """
            INSERT INTO messages (ID, IMEI, CCID, CONTENT, TYPE, STATUS, DESTINATARY, REGIST_DATE) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """
            parameters = (
                unique_id, 
                imei, 
                ccid, 
                content, 
                message_type, 
                status,
                destinatary, # Coma corregida
                int(time.time())
            )
            
            try:
                return self._execute_write(operation, parameters)
            except Exception as e:
                # En depuración, podrías querer ver el error de integridad (UNIQUE ID)
                # print(f"[MessagesDatabase] Error en registro: {e}")
                return False
    
    def get_message(self, index: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM messages WHERE INDEX_ID = ?;"
        return self._execute_read(query, (index,), fetch_one=True)

    def query_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna los últimos mensajes registrados."""
        query = "SELECT * FROM messages ORDER BY REGIST_DATE DESC LIMIT ?;"
        return self._execute_read(query, (limit,), fetch_one=False)

    def update_status(self, index: int, new_status: str) -> bool:
        operation = "UPDATE messages SET STATUS = ? WHERE INDEX_ID = ?;"
        return self._execute_write(operation, (new_status, index)) > 0
    