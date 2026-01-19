# Library import
from abc import ABC, abstractmethod
from .configurations import Configurations
from typing import Dict, List, Any
from . import constants
from ..operations import OperationParametersInterface, OperationResultsInterface
from ..properties import PropertyInterface

# Classes definition
class DeviceControllerInterface(ABC):
    "This class represents a device controller contract."

    def __init__(self) -> None:
        # Instance properties definition
        self.configurations: Configurations = None
        self.properties: Dict[object, object] = {}
        self.operations: Dict[object, object] = {}
        self.capabilities: Dict[str, dict] = {
            "PROPERTIES":self.properties,
            "OPERATIONS":self.operations
        }
        self.physical_connection_status: str = constants.DISCONNECTED
        self.virtual_connection_status: str = constants.DISCONNECTED
        self.device_status: str = constants.UNAVAILABLE
        self.connection_controller: object | None = None
    
    @property
    def connection_status(self) -> bool:
        return (self.physical_connection_status == constants.CONNECTED) and (self.virtual_connection_status == constants.CONNECTED)
     
    @property
    def is_physically_connected(self) -> bool:
        return self.physical_connection_status == constants.CONNECTED
    
    @property
    def is_virtually_connected(self) -> bool:
        return self.virtual_connection_status == constants.CONNECTED
    
    # Private methods
    def _set_physical_connection_status(self, is_connected: bool) -> bool:
        if is_connected:
            self.physical_connection_status = constants.CONNECTED
        else:
            self.physical_connection_status = constants.DISCONNECTED
        
        return True
    
    def _set_virtual_connection_status(self, is_connected: bool) -> bool:
        if is_connected:
            self.virtual_connection_status = constants.CONNECTED
        else:
            self.virtual_connection_status = constants.DISCONNECTED
        
        return True
    
    @abstractmethod
    def _identify(self) -> List[str]:
        """This method allows to identify devices that apparent be compatible with this controller.

            Returns:
                List: List of elements string
        """
        raise NotImplementedError
    
    @abstractmethod
    def _detect(self, device: str) -> bool:
        """This method verify if a specified device is true compatible with this controller.
        
            Returns:
                bool: true (if is compatible)/false (if is not compatible)
        """
        raise NotImplementedError
    
    @abstractmethod
    def recognize(self) -> List[str]:
        """This method allows to detect if a device is compatible with this controller.

            Returns:
                List: compatible devices
        """
        raise NotImplementedError
    
    @abstractmethod
    def connect(self) -> bool:
        """This method allows to connect with the device, using the specified device configurations.

            Return:
                bool: true (success)/false (error)
        """
        raise NotImplementedError
    
    @abstractmethod
    def configure(self, configurations: Configurations) -> bool:
        """This method allows to configure the device: only if is disconnected. If the device is already connected,
            this will force a disconnection and re-configuration of the device.

            Return:
                bool: true (success)/false (error)
        """
    
    @abstractmethod
    def disconnect(self) -> bool:
        """This method allows to disconnect from the device currently connected.

            Returns:
                bool: true (success)/false (error)
        """
        raise NotImplementedError
    
    @abstractmethod
    def request_property(self, property: object) -> PropertyInterface:
        """This method allows to request a standard defined property (only if its available on this device)
            If the property is not available on this device, this will raise a NotImplementedError exception

            Returns:
                OperationResultsInterface: standard object structure of results for this operation
        """
        raise NotImplementedError
    
    @abstractmethod
    def request_operation(self, operation: object, parameters: OperationParametersInterface) -> OperationResultsInterface:
        """This method allows to request a standard operation with standard parameters to the device.
            If the operation is not supported by the device, it will raise a NotImplementedError exception

            Returns:
                OperationResultsInterface: standard object structure for the results of this operation
        """
        raise NotImplementedError