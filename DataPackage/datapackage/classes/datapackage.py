# Library import
import json
import time
import threading
import queue
from typing import Optional, Any
import traceback

# Classes definition
class Datapackage:
    # Class properties definition
    PACKAGE_DELIMITER: bytes = b"\01\02\03\01\01\01"

    def __init__(self,
        write_function: callable,
        read_function: callable,

        read_arguments: Optional[tuple] = None,
        read_keyword_arguments: Optional[dict] = None
    ) -> None:
        # Instance properties assignment
        self._write_function = write_function
        self._read_function = read_function

        # Package list
        self._package_queue: queue.Queue = queue.Queue()

        # Data reception
        self._read_arguments: tuple = read_arguments if read_arguments else ()
        self._read_keyword_arguments: dict = read_keyword_arguments if read_keyword_arguments else {}
        self._reception_buffer: bytes = bytes()

        # Control
        self._running = True

        # Routines
        self._parameters_lock: threading.Lock = threading.Lock()
        self._reader_thread: threading.Thread = threading.Thread(
            target=self._reader_thread_routine,
            daemon=True
        )
        self._reader_thread.start()

    # Private methods
    def _reader_thread_routine(self) -> None:
        while self._running:
            try:
                # Read a load of bytes
                with self._parameters_lock:
                    chunk = self._read_function(*self._read_arguments, **self._read_keyword_arguments)

                # Verify read result
                if not chunk:
                    # Wait execution temporizer
                    time.sleep(0.01)
                    continue

                # Save the received data
                self._reception_buffer += chunk

                # Process the buffer to identify package delimiters
                while self.PACKAGE_DELIMITER in self._reception_buffer:
                    # Extract the first datapackage from the buffer
                    data_package, self._reception_buffer = self._reception_buffer.split(self.PACKAGE_DELIMITER, 1)

                    # Verify the result
                    if data_package:
                        self._process_packet(data_package)

            except Exception as Error:
                traceback.print_exc()
    
    def _process_packet(self, data_package: bytes) -> bool:
        try:
            decoded_data = data_package.decode("UTF-8")
            datapackage = json.loads(decoded_data)

            # Save the processed package
            self._package_queue.put(datapackage)
        except (json.JSONDecodeError, UnicodeDecodeError):
            traceback.print_exc()

    # Public methods
    def update_reception_parameters(self, *args, **kwargs) -> bool:
        with self._parameters_lock:
            self._read_arguments = args
            self._read_keyword_arguments = kwargs
        
        return True
    
    def send_datapackage(self, data_package: dict, *args, **kwargs) -> bool:
        try:
            datapackage_serialized = json.dumps(data_package).encode("UTF-8")
            full_dataframe = datapackage_serialized + self.PACKAGE_DELIMITER

            return self._write_function(full_dataframe, *args, **kwargs)
        except (TypeError, ValueError):
            traceback.print_exc()
            return False
    
    def receive_datapackage(self, timeout: Optional[int] = None) -> Optional[dict]:
        try:
            return self._package_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            traceback.print_exc()
            return None
    
    def stop(self) -> bool:
        self._running = False
        if self._reader_thread.is_alive():
            self._reader_thread.join(timeout=1.0)
        
        return True