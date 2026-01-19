# Library import
from ...contracts.device_controller.device_controller import DeviceControllerInterface
from ...contracts.properties import PropertyInterface
from ...contracts.operations import OperationParametersInterface, OperationResultsInterface
from ...contracts.device_controller.configurations import Configurations
from ...contracts.device_controller.setting import Setting
from ...contracts.data_classes.primitive_data import PrimitiveData
from typing import List, Type, Optional
from .. import PlatformLayer
from ..transport_layers.serial_at import TransportLayer

from ...contracts.properties.signal_level import SignalLevel
from .properties.signal_level import Property as SignalLevelImplementation

from ...contracts.operations.send_sms import SendSMS
from .operations.send_sms import Operation as SendSMSImplementation

# Classes definition
class Controller(DeviceControllerInterface):
    def __init__(self) -> None:
        # Constructor hereditance
        super().__init__()

        # Instance properties definition
        self.configurations = Configurations()
        self.properties: Dict[object, object] = {
            SignalLevel:SignalLevelImplementation
        }
        self.operations: Dict[object, object] = {
            SendSMS:SendSMSImplementation
        }
        self.transport_layer: Optional[TransportLayer] = None

        # Adjust settings of Configurations
        # Communication port setting
        self.configurations.add_setting(
            Setting(
                value=PrimitiveData(
                    data_type=str,
                    minimum_length=None,
                    maximum_length=None,
                    possible_values=None,
                    content=""
                ),
                system_name="COMMUNICATION_PORT",
                symbolic_name="Communication Device Port",
                description="This setting specifies the device communication port",
                optional=False
            )
        )

        # Baud rate setting
        self.configurations.add_setting(
            Setting(
                value=PrimitiveData(
                    data_type=int,
                    minimum_length=None,
                    maximum_length=None,
                    possible_values=None,
                    content=0
                ),
                system_name="BAUDRATE",
                symbolic_name="Baud Rate",
                description="This setting specifies the baud rate to communicate with the device",
                optional=False
            )
        )
    
    # Private methods
    def _identify(self) -> List[str]:
        system_ports = PlatformLayer().identify_system_ports()

        return system_ports
    
    def _detect(self, device: str) -> bool:
        # Try to connect with the device
        try:
            transport_layer = TransportLayer(
                device_port=device,
                baudrate=115200
            )

            # Open connection
            transport_layer.connect()

            # Send AT identification command
            transport_layer.send_at_command("AT+CGMM")

            # Get the AT command response
            response = transport_layer.read_at_response()

            # Verify the response result
            if "SIM800C" in " ".join(response):
                return True
            else:
                return False
        except:
            return False
        
        finally:
            try:
                transport_layer.disconnect()
            except:
                pass
    
    # Public methods
    def recognize(self) -> List[str]:
        potential_identified_devices = self._identify()
        confirmed_devices = []

        for potential_device in potential_identified_devices:
            if self._detect(potential_device.name):
                confirmed_devices.append(potential_device)
        
        return confirmed_devices

    def connect(self) -> bool:
        # Validate the current settings
        if not self.configurations.query_setting("COMMUNICATION_PORT").value.content: raise ValueError(f"The COMMUNICATION_PORT setting is invalid")
        if not self.configurations.query_setting("BAUDRATE").value.content: raise ValueError(f"The BAUDRATE setting is invalid")

        # Try to connect with the current settings 
        self.transport_layer = TransportLayer(
            device_port=self.configurations.query_setting("COMMUNICATION_PORT").value.content,
            baudrate=self.configurations.query_setting("BAUDRATE").value.content
        )

        # Connect with the device
        self.transport_layer.connect()

        # Update the connection status
        self._set_physical_connection_status(is_connected=True)
        self._set_virtual_connection_status(is_connected=True)

        # Return results
        return True

    def configure(self, configurations: Configurations) -> bool:
        # Update new configurations
        if self.connection_status: raise RuntimeError(f"The device is currently connected and operating")

        self.configurations = configurations
        return True 

    def disconnect(self) -> bool:
        if not self.connection_status: return True

        self.transport_layer.disconnect()

        self._set_physical_connection_status(is_connected=False)
        self._set_virtual_connection_status(is_connected=False)
        return True

    def request_operation(self, operation: object, parameters: OperationParametersInterface) -> OperationResultsInterface:
        # Verify the connection status
        if not self.connection_status: raise RuntimeError(f"The controller is not connected with the device")

        # Verify if the device supports the requested operation
        if operation not in self.operations: raise NotImplementedError(f"The operation: {operation.__class__}, is not supported by this device. Read the operations list: {str(self.operations.keys())}")

        # Get the operation implementation
        operation_implementation = self.operations.get(operation)

        # Instance the operation implementation
        operation_implementation = operation_implementation(self)

        # Execute the operation and get the results
        results = operation_implementation.execute(parameters)

        # Return standard results
        return results

    def request_property(self, property: object) -> PropertyInterface:
        # Verify the connection status
        if not self.connection_status: raise RuntimeError(f"The controller is not connected with the device")

        # Verify if the device supports the requested operation
        if property not in self.properties: raise NotImplementedError(f"The property: {property.__class__}, is not supported by this device. Read the properties list: {str(self.properties.keys())}")

        # Get the specified property implementation object
        property_implementation = self.properties.get(property)

        # Instance the property implementation
        property_implementation = property_implementation(self)

        # Get the data query result
        results = property_implementation.read()

        # Return results
        return results