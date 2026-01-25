# Library import
from .databases.classes import devices, sim_cards, messages
from .databases import resources as DatabasesResources
from ..core.core import Core, utils as CoreUtils
from . import support
from typing import Type, List, Dict, Any
import threading
import time


# Classes definition
class ApplicationSystem:
    # Class properties definition
    DATABASES_STORAGE: str = DatabasesResources.__path__[0]
    APPLICATION_STATUS_ACTIVE: str = "ACTIVE"
    APPLICATION_STATUS_INACTIVE: str = "INACTIVE"

    def __init__(self) -> None:
        # Instance properties definition
        self.status: str = self.APPLICATION_STATUS_INACTIVE
        self.core: Type[Core] = None

        # Databases
        self.DevicesDatabase: Type[devices.DevicesDatabase] = None
        self.SIMCardsDatabase: Type[sim_cards.SIMCardsDatabase] = None
        self.MessagesDatabase: Type[messages.MessagesDatabase] = None

        # Support routines
        self.support_routines: tuple = ()
        self.connection_support_routines: tuple = (
            support._receive_sms,
            support._update_device_information,
            support._update_device_information
        )

        # Indexed by the device identification. Every field is the name
        # of the standard property, and every value is their query result
        self._cached_controlled_devices_information: Dict[str, object] = {}
        self.cached_controlled_devices_information_lock = threading.Lock()


    # Properties
    @property
    def system_ports(self) -> list[CoreUtils.SystemPort]:
        return CoreUtils.identify_devices()
    
    @property
    def compatible_devices(self) -> Dict[str, Any]:
        return self.core.compatible_devices if self.core else {}

    @property
    def is_active(self) -> bool: return self.status == self.APPLICATION_STATUS_ACTIVE

    @property
    def controlled_devices(self) -> Dict[str, Dict[str, Any]]:
        with self.core.controlled_devices_lock:
            # Get a protected copy of the entire table
            controlled_devices = self.core.controlled_devices.copy()

        for device_identification in controlled_devices: 
            # Get a protected copy of the specified device
            device_copy = controlled_devices.get(device_identification).copy()

            # Insert the data (or default data if any exists)
            device_copy["INFORMATION_PROFILE"] = self._cached_controlled_devices_information.get(device_identification, {})  

            # Update the new updated device
            controlled_devices[device_identification] = device_copy

        return controlled_devices
    
    # Private methods
    def _set_status_active(self) -> bool: self.status = self.APPLICATION_STATUS_ACTIVE; return True
    def _set_status_inactive(self) -> bool: self.status = self.APPLICATION_STATUS_INACTIVE; return True

    def _start_support_routines(self) -> bool:
        for routine in self.support_routines:
            routine_controller = threading.Thread(
                target=routine,
                args=[self],
                daemon=True
            )

            # Start the routine
            routine_controller.start()
        
        return True
    
    def _start_connection_support_routines(self, device_identifier: str) -> bool:
        for routine in self.connection_support_routines:
            routine_controller = threading.Thread(
                target=routine,
                args=[self, device_identifier],
                daemon=True
            )

            # Launch the support routine
            routine_controller.start()
        
        return True
    
    def _load_databases(self) -> bool:
        # Devices database
        self.DevicesDatabase = devices.DevicesDatabase(storage_path=self.DATABASES_STORAGE)
        self.DevicesDatabase.connect()

        # SIM Cards database
        self.SIMCardsDatabase = sim_cards.SIMCardsDatabase(storage_path=self.DATABASES_STORAGE)
        self.SIMCardsDatabase.connect()

        # Messages database
        self.MessagesDatabase = messages.MessagesDatabase(storage_path=self.DATABASES_STORAGE)
        self.MessagesDatabase.connect()

        # Return results
        return True
    
    # Public methods
    def start(self) -> bool:
        # Set the application system status: ACTIVE
        self._set_status_active()

        # Load databases
        self._load_databases()

        # Start the core
        self.core = Core()
        self.core.start()

        # Start the support routines
        self._start_support_routines()

        # Return results
        return True
    
    def stop(self) -> bool:
        # Set the application system status: INACTIVE
        self._set_status_inactive()

        # Execute a time-wait until the application system is securely stopped
        #time.sleep(3)

        # Disconnect all the databases
        self.DevicesDatabase.close()
        self.SIMCardsDatabase.close()
        self.MessagesDatabase.close()

        # Return results
        return True
    
    def connect(self,
        configurations: object,
        device_port: object,
        device_controller: object
    ) -> str | bool:
        connection_result = self.core.connect_device(
            configurations=configurations,
            device_port=device_port,
            device_controller_module=device_controller
        )

        # Validate the connection result
        if connection_result:
            # Launch connections support routines
            launch_result = self._start_connection_support_routines(connection_result)

            # Log the device in the DevicesDatabase
            self.DevicesDatabase.regist_device(connection_result)
        else:
            return False

        return connection_result 

    def get_device_configurations(self) -> object:
        pass

    def disconnect(self,
        device_identification: str
    ) -> bool:
        return self.core.disconnect_device(
            device_identification=device_identification
        )
    
    def update_device_information(self, device_identifier: str) -> Dict[str, Any]:
        with self.cached_controlled_devices_information_lock:
            # Verify the device existence
            if not self.controlled_devices.get(device_identifier, False): raise KeyError(f"The specified device identification: {device_identifier}, not exists")

            # Verify the current device connection status
            if not self.controlled_devices.get(device_identifier, False).get("DEVICE_CONTROLLER").connection_status: raise ConnectionError(f"The device: {device_identifier}, is currently disconnected")

            # Get the standard properties supported by the device
            standard_properties_supported = self.controlled_devices.get(device_identifier).get("DEVICE_CONTROLLER").properties

            # Query and update every property
            for property in standard_properties_supported:
                # Query the current data status
                new_data = self.core.request_property(device_identifier, property)

                # Update the new data
                if device_identifier not in self._cached_controlled_devices_information: self._cached_controlled_devices_information[device_identifier] = {}

                print("NEW DATA:")
                print(new_data.to_dict())

                self._cached_controlled_devices_information[device_identifier][property.NAME] = new_data
            

        return True