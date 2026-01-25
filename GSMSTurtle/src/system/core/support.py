# Library import
import time

# Functions definition
def _update_loaded_controllers_routine(core) -> None:
    while core.is_active:
        try:
            # Identify the available controllers    
            available_controllers = core.load_controllers(auto_update=False)

            with core.loaded_controllers_lock:
                # Load the new controller modules
                core.loaded_controllers = available_controllers
            
        except Exception as Error:
            print(f"[CORE.SUPPORT.CONTROLLERS_ROUTINE] Error updating the loaded controllers: {Error}")

        # Execution temporizer
        time.sleep(60)

def _update_available_compatible_devices(core) -> None:
    while core.is_active:
        # Verify that theres available controllers loaded
        if not core.loaded_controllers: time.sleep(3); continue

        try:
            # Recognize automatically new devices
            compatible_devices = core.auto_recognize_compatible_devices(auto_update=False)

            with core.compatible_devices_lock:
                # Securely update the data
                core.compatible_devices = compatible_devices
            
        except Exception as Error:
            print(f"[CORE.SUPPORT.COMPATIBLE_DEVICES_ROUTINE] Error updating the compatible devices: {Error}")
        
        # Execution temporizer
        time.sleep(65)

def _receive_sms(core) -> None:
    pass

def _update_controlled_devices_information(core) -> None:
    pass