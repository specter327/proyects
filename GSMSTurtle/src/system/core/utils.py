# Library import
from ...contracts.device_controller.device_controller import DeviceControllerInterface
from ...controllers import identify_controllers, PlatformLayer
from typing import List

# Functions definition
def identify_devices() -> List[DeviceControllerInterface]:
    return PlatformLayer().identify_system_ports()

def load_controllerS() -> List[DeviceControllerInterface]:
    return identify_controllers()