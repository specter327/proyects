# Library import
import time

# Functions definition
def _update_loaded_controllers_routine(core) -> None:
    while core.status == core.STATUS_ACTIVE:
        # Execution temporizer
        if time.time() - core.last_update["CONTROLLERS"] > 60 or core.last_update["CONTROLLERS"] == 0:
            core.last_update["CONTROLLERS"] = time.time()
        else:
            continue
        
        # Load the new controller modules
        core.load_controllers()

def _update_available_compatible_devices(core) -> None:
    while core.status == core.STATUS_ACTIVE:
        if time.time() - core.last_update["COMPATIBLE_DEVICES"] > 40 or core.last_update["COMPATIBLE_DEVICES"] == 0:
            if not core.loaded_controllers: continue
            
            core.last_update["COMPATIBLE_DEVICES"] = time.time()
        else:
            continue
        

        # Recognize automatically new devices
        core.available_compatible_devices = core.auto_recognize_compatible_devices()