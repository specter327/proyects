# Library import
from dataclasses import dataclass
import os
import traceback
from ..contracts.device_controller.device_controller import DeviceControllerInterface
from typing import List, Type
import importlib
import pkgutil
import platform
from serial.tools import list_ports
from abc import ABC, abstractmethod


# Classes definition
@dataclass(frozen=True)
class ControllerDescriptor:
    # Class properties definition
    name: str
    description: str
    version: str
    controller: Type[DeviceControllerInterface]

    STANDARD_ATTRIBUTES: tuple = (
        "NAME",
        "DESCRIPTION",
        "VERSION"
    )

@dataclass(frozen=True)
class SystemPort:
    # Class properties definition
    name: str
    description: str
    hwid: str
    vid: int | None
    pid: int | None
    serial_number: str | None
    manufacturer: str | None
    product: str | None

class PlatformLayer:
    "This class represents a abstraction of the current platform, to implement standard data and functions."
    def __init__(self) -> None:
        self.__current_platform = platform.system().upper()
    
    # Public methods
    def identify_system_ports(self) -> List[SystemPort]:
        system_ports = []

        for system_port in list_ports.comports():
            system_ports.append(SystemPort(
                name=system_port.device,
                description=system_port.description,
                hwid=system_port.hwid,
                vid=system_port.vid,
                pid=system_port.pid,
                serial_number=system_port.serial_number,
                manufacturer=system_port.manufacturer,
                product=system_port.product
            ))
        
        return system_ports

# Functions definition
def identify_controllers() -> List[ControllerDescriptor]:
    package_name = __name__
    controllers: List[ControllerDescriptor] = []

    for module_information in pkgutil.iter_modules(__path__):
        controller_name = module_information.name

        try:
            module = importlib.import_module(f"{package_name}.{controller_name}")

            # Validate exceptional-attribute
            if not hasattr(module, "__controller__"): continue

            # Validate standard attributes
            for attribute in ControllerDescriptor.STANDARD_ATTRIBUTES:
                if not hasattr(module, attribute):
                    raise ImportError(f"Controller: {controller_name}, missing attribute: {attribute}")
            
            # Get the controller standard class
            controller_module = importlib.import_module(f"{package_name}.{controller_name}.controller")

            ControllerClass = getattr(controller_module, "Controller", None)

            # Vaidate the controller class
            if ControllerClass is None:
                raise ImportError(f"Controller class not found")
            
            if not issubclass(ControllerClass, DeviceControllerInterface):
                raise TypeError(f"Controller: {controller_name}, does not implement: DeviceControllerInterface")
            
            
            controllers.append(
                ControllerDescriptor(
                    name=module.NAME,
                    description=module.DESCRIPTION,
                    version=module.VERSION,
                    controller=ControllerClass
                )
            )
        
        except Exception as Error:
            full_trace = traceback.format_exc()
            error_details = traceback.format_exception_only(type(Error), Error)

            print(f"[Controller loader] Skipped {controller_name}: {Error}")
        
    return controllers

# Auto-identify the current existent modules controllers
available_controllers = identify_controllers()


# Code API
__all__ = ["ControllerDescriptor", "identify_controllers", "available_controllers", "PlatformLayer"]