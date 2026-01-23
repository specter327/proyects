# Library import
from ...contracts.device_controller.device_controller import DeviceControllerInterface
from ...contracts.properties import PropertyInterface
from ...contracts.operations import OperationParametersInterface, OperationResultsInterface
from ...contracts.device_controller.configurations import Configurations
from ...contracts.device_controller.setting import Setting
from ...contracts.data_classes.primitive_data import PrimitiveData
from typing import List, Type, Optional, Dict
from .. import PlatformLayer
from ..transport_layers.serial import TransportLayer
from ..transport_layers.ATEngine import ATEngine

from ...contracts.properties.signal_level import SignalLevel
from .properties.signal_level import Property as SignalLevelImplementation

from ...contracts.operations.send_sms import SendSMS
from .operations.send_sms import Operation as SendSMSImplementation
from ...contracts.operations.receive_sms import ReceiveSMS
from ...contracts.operations.delete_sms import DeleteSMS
from ...contracts.properties.query_imei import QueryIMEI

from .operations.receive_sms import Operation as ReceiveSMSImplementation
from .operations.delete_sms import Operation as DeleteSMSImplementation
from .properties.query_imei import Property as QueryIMEIImplementation

# Classes definition
class Controller(DeviceControllerInterface):
    def __init__(self) -> None:
        # Constructor hereditance
        super().__init__()

        # Instance properties definition
        self.configurations = Configurations()
        self.properties: Dict[object, object] = {
            SignalLevel:SignalLevelImplementation,
            QueryIMEI:QueryIMEIImplementation
        }
        self.operations: Dict[object, object] = {
            SendSMS:SendSMSImplementation,
            ReceiveSMS:ReceiveSMSImplementation,
            DeleteSMS:DeleteSMSImplementation
        }
        self.ATEngine: Optional[ATEngine] = None
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
        transport_layer: Optional[TransportLayer] = None
        at_engine: Optional[ATEngine] = None

        try:
            transport_layer = TransportLayer(
                device_port=device,
                baudrate=115200,
                timeout=10
            )
            transport_layer.connect()

            at_engine = ATEngine(transport_layer)
            at_engine.start()

            # Comando de identificación de modelo
            at_engine.send_at_command("AT+CGMM")

            # Consumir TODA la respuesta del comando
            response = at_engine.read_at_response()
            print("Response:")
            print(response.content)
            print(response.compact())

            # Verificación explícita
            return any(b"SIM800C" in r for r in response.content)

        except Exception:
            return False

        finally:
            if at_engine:
                at_engine.stop()
            if transport_layer:
                try:
                    transport_layer.disconnect()
                except Exception:
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
        # Validar configuración
        port = self.configurations.query_setting("COMMUNICATION_PORT").value.content
        baudrate = self.configurations.query_setting("BAUDRATE").value.content

        if not port:
            raise ValueError("The COMMUNICATION_PORT setting is invalid")
        if not baudrate:
            raise ValueError("The BAUDRATE setting is invalid")

        # Crear capa de transporte
        self.transport_layer = TransportLayer(
            device_port=port,
            baudrate=baudrate
        )
        self.transport_layer.connect()

        # Crear y arrancar ATEngine
        self.ATEngine = ATEngine(self.transport_layer)
        self.ATEngine.start()

        # Inicialización estándar del módem
        # ATE0: desactivar eco
        self.ATEngine.send_at_command("ATE0")
        response = self.ATEngine.read_at_response()
        if b"OK" not in response.content: raise RuntimeError(f"Error connecting with the device. ATE0 command respond: {response.content}")

        # AT+CMEE=1: errores extendidos
        self.ATEngine.send_at_command("AT+CMEE=1")
        response = self.ATEngine.read_at_response()

        # Actualizar estado
        self._set_physical_connection_status(is_connected=True)
        self._set_virtual_connection_status(is_connected=True)

        return True

    def configure(self, configurations: Configurations) -> bool:
        # Update new configurations
        if self.connection_status: raise RuntimeError(f"The device is currently connected and operating")

        self.configurations = configurations
        return True 

    def disconnect(self) -> bool:
        if not self.connection_status:
            return True

        if self.ATEngine:
            self.ATEngine.stop()
            self.ATEngine = None
        if self.transport_layer:
            try:
                self.transport_layer.disconnect()
            except Exception:
                pass
            self.transport_layer = None

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