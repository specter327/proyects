# Library import
from typing import List, Dict, Any
import threading
import traceback
from . import utils, support
from ...controllers import ControllerDescriptor, DeviceControllerInterface, SystemPort
from ...contracts.operations import OperationInterface, OperationParametersInterface, OperationResultsInterface
from ...contracts.properties import PropertyInterface
from ...contracts.properties.query_imei import QueryIMEI
from ...contracts.device_controller.configurations import Configurations

# Classes definition
class Core:
    # Class properties definition
    CORE_STATUS_ACTIVE: str = "ACTIVE"
    CORE_STATUS_INACTIVE: str = "INACTIVE"

    def __init__(self) -> None:
        # Instance properties definition
        # Example
        #     [ControllerModule, ControllerModule, ControllerModule...]
        # Esto incluye el modulo controlador, con todos sus detalles y el controlador
        # de dispositivo especifico
        self.loaded_controllers: List[ControllerDescriptor] = []

        # Example
        # Esto incluye el puerto de sistema (SystemPort.name (nombre)), y el modulo controlador compatible 
        # con toda su informacion
        self.compatible_devices: Dict[str, ControllerDescriptor] = {}

        # Esto incluye todos los dispositivos conectados actualmente. Esta indexado
        # por la identificacion unica del dispositivo, y su controlador instanciado,
        # ademas del puerto del sistema (SystemPort), y el modulo del controlador (
        # con toda la informacion)
        self.controlled_devices: Dict[str, Any] = {}

        #self.available_compatible_devices: Dict[str, DeviceControllerInterface] = {}
        self.status: str = self.CORE_STATUS_INACTIVE
        #self.controlled_devices: Dict[int, (SystemPort, DeviceControllerInterface)] = {}

        # Support routines
        self.support_routines = [
            support._update_loaded_controllers_routine,
            support._update_available_compatible_devices,
            support._handle_standard_events
        ]

        # Event notification system
        self.event_notification_table: Dict[object, Dict[int, callable]] = {}

        # Concurrence security (mutex's)
        self.loaded_controllers_lock = threading.Lock()
        self.compatible_devices_lock = threading.Lock()
        self.controlled_devices_lock = threading.Lock()

    # Properties
    @property
    def is_active(self) -> bool: return self.status == self.CORE_STATUS_ACTIVE

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
    
    def _set_status_active(self) -> bool: self.status = self.CORE_STATUS_ACTIVE; return True
    def _set_status_inactive(self) -> bool: self.status = self.self.CORE_STATUS_INACTIVE; return True


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

    def get_device_configurations(self, controller_module: ControllerDescriptor) -> Configurations:
        return controller_module.controller().configurations
    
    def load_controllers(self, auto_update: bool = True) -> List[ControllerDescriptor]:
        identified_controllers = utils.identify_controllers()
        loaded_controllers: list = []

        if identified_controllers:
            for module in identified_controllers:
                if module not in self.loaded_controllers:
                    print("New module:", module)
                    loaded_controllers.append(module)
        
        if auto_update:
            with self.loaded_controllers_lock:
                self.loaded_controllers = loaded_controllers
        
        print("New controllers loaded:",loaded_controllers)
        return loaded_controllers
    
    def auto_recognize_compatible_devices(self, auto_update: bool = True) -> Dict[str, DeviceControllerInterface]:
        recognized_devices: Dict[str, DeviceControllerInterface] = {}

        for module_controller in self.loaded_controllers:
            recognize_result = module_controller.controller().recognize()

            if recognize_result:
                for device in recognize_result:
                    recognized_devices[device] = module_controller
        
        # Update local data
        if auto_update:
            with self.compatible_devices_lock:
                self.compatible_devices = recognized_devices

        # Return results
        return recognized_devices
    
    def connect_device(self, 
            configurations: Configurations,
            device_port: SystemPort = None, 
            device_controller_module: ControllerDescriptor = None 
        ) -> str | bool:
            
            # 1. Resolución del Controlador
            if device_port and not device_controller_module:
                with self.compatible_devices_lock:
                    if device_port not in self.compatible_devices:
                        raise NotImplementedError(f"No compatible controller found for port: {device_port.name}")
                    device_controller_module = self.compatible_devices.get(device_port)
            
            if not device_controller_module:
                raise ValueError("A Device Controller or a compatible System Port must be provided.")

            # 2. Verificación de exclusión mutua (Evitar doble conexión al mismo puerto)
            if device_port:
                with self.controlled_devices_lock:
                    for imei, data in self.controlled_devices.items():
                        if data.get("SYSTEM_PORT") == device_port:
                            raise ProcessLookupError(f"Port {device_port.name} is already in use by device {imei}")

            # 3. Instanciación e Inicialización
            # Obtenemos la instancia real del controlador desde el descriptor
            instance: DeviceControllerInterface = device_controller_module.controller()
            
            try:
                # Inyección de configuración
                instance.configure(configurations)
                
                # Intento de apertura de canal de comunicación
                if not instance.connect():
                    return False
                
                # 4. Identificación del Hardware
                # Consultamos el IMEI para registrar la identidad única
                imei_query = instance.request_property(QueryIMEI)
                
                if imei_query.status_code.content != 0:
                    instance.disconnect()
                    raise RuntimeError(f"Identity query failed. Device at {device_port.name if device_port else 'VIRTUAL'} is not responding.")
                
                imei_code = imei_query.imei.content

                # 5. Registro en tabla de dispositivos controlados
                with self.controlled_devices_lock:
                    self.controlled_devices[imei_code] = {
                        "DEVICE_CONTROLLER": instance,
                        "SYSTEM_PORT": device_port,
                        "CONTROLLER_MODULE": device_controller_module,
                    }
                
                return imei_code

            except Exception as e:
                # Rollback de conexión en caso de error durante el handshake
                if instance:
                    instance.disconnect()
                print(f"[CORE.CONNECT] Critical error: {e}")
                print("Traceback:")
                print("==========")
                traceback.print_exc()
                print("==========")

                return False

    def disconnect_device(self, device_identification: str) -> bool:
        with self.controlled_devices_lock:
            if device_identification not in self.controlled_devices:
                return False
            
            device_data = self.controlled_devices.get(device_identification)
            instance: DeviceControllerInterface = device_data.get("INSTANCE")
            
            # Desconexión física
            instance.disconnect()
            
            # Eliminación del registro
            del self.controlled_devices[device_identification]
            
        return True
    
    def request_operation(self,
            device_identification: str,
            operation: OperationInterface,
            parameters: OperationParametersInterface
        ) -> OperationResultsInterface:
        # Verify if the specified device is currently connected
        if device_identification not in self.controlled_devices: raise KeyError(f"The device: {device_identification}, not exists in the currently controlled devices: {str(self.controlled_devices.keys())}")

        # Get the device controller
        device_controller = self.controlled_devices.get(device_identification).get("DEVICE_CONTROLLER")

        # Verify the device connection status
        if not device_controller.connection_status: raise ConnectionError(f"The connection with the device: {device_identification}, is currently closed. Physical: {device_controller.physical_connection_status} | Virtual: {device_controller.virtual_connection_status}")

        # Request the standard operation with standard parameters to the device controller
        operation_results = device_controller.request_operation(
            operation,
            parameters
        )

        # Return results
        return operation_results
    
    def request_property(self,
            device_identification: str,
            property: PropertyInterface
        ) -> PropertyInterface:
            # Verify if the specified device is currently connected
            if device_identification not in self.controlled_devices: raise KeyError(f"The device: {device_identification}, not exists in the currently controlled devices: {str(self.controlled_devices.keys())}")

            # Get the device controller
            device_controller = self.controlled_devices.get(device_identification).get("DEVICE_CONTROLLER")

            # Verify the device connection status
            if not device_controller.connection_status: raise ConnectionError(f"The connection with the device: {device_identification}, is currently closed. Physical: {device_controller.physical_connection_status} | Virtual: {device_controller.virtual_connection_status}")

            # Request the standard property to the device controller
            property = device_controller.request_property(
                    property
            )

            # Return results
            return property

    def subscribe_notification(self, event: object, handler_function: callable) -> int:
        # Verify the current event existence (or regist it if not exists)
        if event not in self.event_notification_table: self.event_notification_table[event] = {}

        # Append the handler function to the subscribed handlers
        next_event_identification = len(self.event_notification_table[event].keys())

        # Insert the handler function
        self.event_notification_table[event][next_event_identification] = handler_function

        # Return results
        return next_event_identification