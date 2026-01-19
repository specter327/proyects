# Library import
from .. import TransportLayerInterface
import serial
import time
from typing import Optional, List

# Classes definition
class TransportLayer(TransportLayerInterface):
    def __init__(self,
        device_port: str,
        baudrate: int,
        timeout: int = 10
    ) -> None:
        # Constructor hereditance
        super().__init__()

        # Instance properties assignment
        self.device_port = device_port
        self.baudrate = baudrate
        self.timeout = timeout
    
    # Public methods
    def send_at_command(self, command: str) -> bool:
        full_command = f"{command}\r\n"

        return self.write(full_command.encode("UTF-8"))

    def read_at_response(self, timeout=None) -> List[str]:
        if timeout is None: timeout = self.timeout
        
        if not self._connection_controller: raise RuntimeError(f"Serial connection not established")

        start_time = time.time()
        buffer: List[str] = []

        while True:
            if (time.time() - start_time) > self.timeout:
                break

            line = self._connection_controller.readline()
            if not line:
                continue
            
            decoded = line.decode("UTF-8", errors="ignore").strip()
            if decoded:
                buffer.append(decoded)

                # Terminaciones AT estandar
                if decoded == "OK" or decoded.startswith("ERROR"):
                    break
        
        return buffer

    def connect(self) -> bool:
        try:
            self._connection_controller = serial.Serial(
                port=self.device_port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )

            self.send_at_command("AT")
            response = self.read_at_response()

            return "OK" in response
        except serial.SerialException as Error:
            self._connection_controller = None

            raise ConnectionError(f"Serial connection failed: {Error}")

    
    def write(self, data: bytes) -> bool:
        if not self._connection_controller: raise RuntimeError(f"Serial connection is not established")

        self._connection_controller.write(data)
        self._connection_controller.flush()

        return True
    
    def read(self, amount: int = 1) -> bytes:
        if not self._connection_controller: raise RuntimeError(f"Serial connection not established")

        return self._connection_controller.read(amount)
    
    def disconnect(self) -> bool: 
        if not self._connection_controller: raise RuntimeError(f"Serial connection not established")
        return self._connection_controller.close()

        return True