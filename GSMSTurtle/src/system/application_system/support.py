# Library import
from typing import Type, Dict, Any
import time
from ...contracts.operations.receive_sms import ReceiveSMS, ReceiveSMSOperationParameters
from ...contracts.operations.delete_sms import DeleteSMS, DeleteSMSOperationParameters

# Functions definition
def _receive_sms(application: object, device_identifier: str) -> None:
    while application.is_active:
        # Verify the device connection status
        print("Controlador de dispositivo:")
        print(application.controlled_devices.get(device_identifier))

        if not application.controlled_devices.get(device_identifier).get("DEVICE_CONTROLLER").connection_status:
            print("Device disconnected detected...")
            break

        # Get the current storaged messages
        current_storaged_messages = application.core.request_operation(device_identifier, ReceiveSMS, ReceiveSMSOperationParameters())

        print("Current storaged messages:")
        print(current_storaged_messages.messages)
        for message in current_storaged_messages.messages: print("Nuevo mensaje:"); print(message.to_dict())

        print(dir(current_storaged_messages))

        # Execution temporizer
        time.sleep(120)

def _update_device_information(application: object, device_identifier: str) -> None:
    while application.is_active:
        # Verify the device connection status
        if not application.controlled_devices.get(device_identifier).get("DEVICE_CONTROLLER").connection_status:
            print("Device disconnected detected...")
            break

        # Get the device controller supported standard properties
        update_result = application.update_device_information(device_identifier)

        # Query every dinamic available property
        #for supported_property in 

        # Execution temporizer
        time.sleep(360)