# Library import
import time
import threading

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
        time.sleep(300)

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
        time.sleep(600)

def _receive_sms(core) -> None:
    pass

def _update_controlled_devices_information(core) -> None:
    pass

def _handle_standard_events(core) -> None:
    print("Starting event handler routine...")

    # While the core is active...
    while core.status == core.CORE_STATUS_ACTIVE:
        # Query the current devices controlled
        with core.controlled_devices_lock:
            devices_controlled = tuple(core.controlled_devices.items())
        
        # For every device in the controlled devices
        for device_identifier, device_profile in devices_controlled:
            print("[CORE] Controlled device:", device_identifier)
            # Get the device controller
            controller = device_profile.get("DEVICE_CONTROLLER")

            # Query the standard events on the device
            for standard_event, events in tuple(controller.events.items()):
                print("[CORE] Standard event:", standard_event.NAME)

                if standard_event in core.event_notification_table:
                    for occurrence_identifier, event in tuple(events.items()):
                        # Verify if the event is already seen marked
                        print("ESTADO DEL EVENTO:", event.status_seen)
                        if event.status_seen:
                            print("[CORE HANDLER] Skipping seen event:", event)
                            continue
                            
                        
                        handlers = core.event_notification_table.get(standard_event, {})
                        for handler_identifier, handler_function in handlers.items():
                            _execute_event_notification_handler(
                                core,
                                event,
                                handler_function,
                                device_identifier
                            )

                            # Execution temporizer
                            time.sleep(0.1)

                        # Mark the event as readed
                        event.mark_seen()
                
                # Execution temporizer
                time.sleep(0.3)
    
            # Execution temporizer
            time.sleep(0.3)

    # Finish the routine
    print("Finishing handler event routine...")
    return None

def _execute_event_notification_handler(core, event: object, handler_function: callable, device_identifier: str = None) -> bool:
    # Create the function object
    function_arguments = [core, event]
    if device_identifier is not None:
        function_arguments.append(device_identifier) 

    function_controller = threading.Thread(
        target=handler_function,
        args=function_arguments,
        daemon=True
    )

    # Launch the function handler
    function_controller.start()

    # Return results
    return True