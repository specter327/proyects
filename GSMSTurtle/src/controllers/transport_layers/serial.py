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

        # Instance properties definition
        self._connection_controller = None
    
    # Public methods
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

            #self.send_at_command("AT")
            #response = self.read_at_response()

            return True
        except serial.SerialException as Error:
            self._connection_controller = None

            raise ConnectionError(f"Serial connection failed: {Error}")

    def write(self, data: bytes) -> bool:
        if not self._connection_controller: raise RuntimeError(f"Serial connection is not established")
        
        print("Writted:")
        print(data)
        
        self._connection_controller.write(data)
        self._connection_controller.flush()

        return True
    
    def read(self, amount: int = 1) -> bytes:
        if not self._connection_controller: raise RuntimeError(f"Serial connection not established")
        data = self._connection_controller.read(amount)

        print("Data readed:")
        print(data)
        
        return data
    
    def disconnect(self) -> bool:
        if not self._connection_controller:
            raise RuntimeError("Serial connection not established")

        self._connection_controller.close()
        self._connection_controller = None
        return True