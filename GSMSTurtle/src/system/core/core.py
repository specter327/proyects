# Library import
from typing import List, Dict
import threading
from . import utils, support
from ...controllers import ControllerDescriptor, DeviceControllerInterface, SystemPort
from ...contracts.properties.query_imei import QueryIMEI
from ...contracts.device_controller.configurations import Configurations

# Classes definition
class Core:
    # Class properties definition
    STATUS_ACTIVE: str = "ACTIVE"
    STATUS_INACTIVE: str = "INACTIVE"

    def __init__(self) -> None:
        # Instance properties definition
        self.loaded_controllers: List[ControllerDescriptor] = []
        self.available_compatible_devices: Dict[str, DeviceControllerInterface] = {}
        self.status: str = self.STATUS_INACTIVE
        self.controlled_devices: Dict[int, (SystemPort, DeviceControllerInterface)] = {}

        # Support routines
        self.support_routines = [
            support._update_loaded_controllers_routine,
            #support._update_available_compatible_devices
        ]

        self.last_update = {
            "CONTROLLERS":0,
            "COMPATIBLE_DEVICES":0
        }

    # Private methods
    def _start_support_routines(self) -> True:
        for routine in self.support_routines:
            controller = threading.Thread(
                target=routine,
                args=[self],
                daemon=True
            )
            controller.start()
        
        return True
    
    def _set_status_active(self) -> bool: self.status = self.STATUS_ACTIVE; return True
    def _set_status_inactive(self) -> bool: self.status = self.STATUS_INACTIVE; return True

    # Public methods
    def start(self) -> bool:
        # Set the core status: ACTIVE
        self._set_status_active()

        # Launch the support routines for the core
        self._start_support_routines()

        # Return results
        return True

    def stop(self) -> bool:
        # Set the core status: INACTIVE
        self._set_status_inactive()

        # Return results
        return True

    def get_device_configurations(self, device_controller: DeviceControllerInterface) -> Configurations:
        return device_controller.controller().configurations
    
    def connect_device(self, device_port: object, configurations: object) -> bool:
        # Verify the device port and compatibility detected
        if device_port not in self.available_compatible_devices: raise NotImplemented(f"This device is not on the available compatible devices table")

        # Verify the current connection
        for device_identifier in self.controlled_devices:
            if self.controlled_devices.get(device_identifier)[0] == device_port: raise ProcessLookupError(f"The device is currently connected: detected by the same system port")
        
        # Create a device controller instance
        device_controller = self.available_compatible_devices.get(device_port).controller()

        # Try to configurate the device
        device_controller.configure(configurations)

        # Try to connect with the device
        connection_result = device_controller.connect()

        # Verify connection results
        if not connection_result: raise ConnectionError(f"There was an error opening the connection. Check the provided configurations or the device disponibility")

        # Get the device identification (IMEI)
        imei_query = device_controller.request_property(QueryIMEI)

        # Validate the query result
        if imei_query.status_code.content != 0: raise RuntimeError(f"There was an error querying the IMEI code of the device: {device_port.name}")
        else: imei_code = imei_query.imei.content

        # Integrate the new controlled device (and his conneciton)
        self.controlled_devices[imei_code] = device_controller

        # Return results
        return True

    def load_controllers(self) -> int:
        identified_controllers = utils.identify_controllers()
        loaded_controllers: int = 0

        if identified_controllers:
            for module in identified_controllers:
                if module not in self.loaded_controllers:
                    self.loaded_controllers.append(module)
                    loaded_controllers += 1
        
        return loaded_controllers
    
    def auto_recognize_compatible_devices(self) -> Dict[str, DeviceControllerInterface]:
        recognized_devices: Dict[str, DeviceControllerInterface] = {}

        for module_controller in self.loaded_controllers:
            recognize_result = module_controller.controller().recognize()

            if recognize_result:
                for device in recognize_result:
                    recognized_devices[device] = module_controller
        
        # Update local data
        self.available_compatible_devices = recognized_devices

        # Return results
        return recognized_devices