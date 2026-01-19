# Library import
import time
from ....contracts.properties.signal_level import SignalLevel
from ....contracts.properties import PropertyInterface

# Classes definition
class Property(SignalLevel):
    """
        SignalLevel property implementation for SIM800C devices
    """

    def __init__(self, 
        controller: object
    ) -> None:
        # Instance properties assignment
        self.controller = controller

        # Verify the controller status
        if not self.controller.connection_status:
            raise RuntimeError(f"Controller is not connected with the device")
    
    # Public methods
    def read(self) -> SignalLevel:
        """
            Reads the signal level information from the SIM800C device and returns a standardized SignalLevel object
        """
        
        # Execute AT query command
        self.controller.transport_layer.send_at_command("AT+CSQ")
        
        # Get the query result
        response = self.controller.transport_layer.read_at_response()

        # Process the data results
        rssi_raw = None
        rssi_dbm = None
        ber = None

        for line in response:
            if line.startswith("+CSQ:"):
                try:
                    # Extract and format data
                    payload = line.split(":")[1].strip()
                    rssi_str, ber_str = payload.split(",")

                    rssi_raw = int(rssi_str)
                    ber = int(ber_str)

                    # Validate the extracted data
                    if rssi_raw != 99:
                        rssi_dbm = -113 + (rssi_raw * 2)
                    else:
                        rssi_raw = None
                        rssi_dbm = None
                    
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid CSQ response: {line}")
        
        # Normalize the signal quality data
        signal_quality = None
        if rssi_dbm is not None:
            signal_quality = max(0, min(100, int((rssi_dbm + 113) * 100 / 62)))
        
        # Create a SignalLevel standardized object
        return SignalLevel(
            technology="GSM",
            rssi_raw=rssi_raw,
            rssi_dbm=rssi_dbm,
            ber=ber,
            rsrp=None,
            rsrq=None,
            sinr=None,
            signal_quality=signal_quality,
            timestamp=time.time()
        )