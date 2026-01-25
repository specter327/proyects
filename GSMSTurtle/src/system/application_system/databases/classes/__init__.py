# Library import
import sqlite3
import threading
import os
from typing import List, Dict, Any, Union, Tuple

# Classes definition
class Database:
    # Class properties definition
    file_extension: str = "sqlite"

    def __init__(self,
        file_name: str,
        storage_path: str
    ) -> None:
        # Instance properties definition
        self.file_name = file_name
        self.storage_path = storage_path

        self.connection: object = None
        self.operation_lock = threading.Lock()
    
    @property
    def database_resource(self) -> str: return f"{self.storage_path}/{self.file_name}.{self.file_extension}"

    # Public methods
    def connect(self) -> bool:
        connection = sqlite3.connect(
            self.database_resource,
            check_same_thread=False
        )

        # Enable access by name columns
        connection.row_factory = sqlite3.Row

        # Enable foreign keys on the database
        connection.execute("PRAGMA foreign_keys = ON;")

        # Set the connection property
        self.connection = connection

        # Return results
        return True

    def _initialize_database(self) -> bool: raise NotImplementedError

    def _execute_write(self, operation: str, parameters: tuple = ()) -> int:
        with self.operation_lock:
            with self.connection as connection:
                # Get a database cursor to operate
                cursor = connection.cursor()

                # Execute the operation
                cursor.execute(operation, parameters)

                # Confirm changes
                connection.commit()

                # Return results
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    
    def _execute_read(self, operation_query: str, parameters: tuple = (), fetch_one: bool = False) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        with self.operation_lock:
            with self.connection as connection:
                # Get a database cursor
                cursor = connection.cursor()

                # Execute the query operation
                cursor.execute(operation_query, parameters)

                # Get the query results
                if fetch_one:
                    # Get one row of the query results
                    row = cursor.fetchone()
                    return dict(row) if row else None
                else:
                    # Get all the query results
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows] if rows else []
    
    def close(self) -> bool:
        # Get a lock
        with self.operation_lock:
            # Verify the current connection
            if self.connection:
                # Close the current connection
                self.connection.close()

                # Restablish the previous connection
                self.connection = None
        
        return True