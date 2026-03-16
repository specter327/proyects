# Library import
import time
from typing import Dict
from ...contracts.events.sim_removed import SIMRemovedEvent
from ...contracts.events.message_received import MessageReceivedEvent
from ...contracts.properties.query_ccid import QueryCCID
from ...contracts.operations.receive_sms import ReceiveSMS, ReceiveSMSOperationParameters, ReceiveSMSOperationResults
from ...contracts.operations.delete_sms import DeleteSMS, DeleteSMSOperationParameters, DeleteSMSOperationResults
import os

# Functions
def play_sound_notification():
    os.system("play /home/specter/Descargas/beep-6-96243.mp3")
    return True

# Classes definition
class EventHandlers:
    def __init__(self,
        application: object
    ) -> None:
        # Instance properties assignment
        self.application = application

        # Instance properties definition
        self.event_handlers: Dict[object, callable] = {
            SIMRemovedEvent:self._on_sim_removed_event,
            MessageReceivedEvent:self._on_message_received
        }
    
    # Private methods
    def _on_sim_removed_event(self, core: object, event: object, device_identifier: str) -> None:
        print(f"[APPLICATION] SE EXTRAJO LA SIM DEL DISPOSITIVO:", device_identifier)        
        time.sleep(30)
        print("FINALIZANDO MANEJADOR DE EVENTO")
    
    def _on_message_received(self, core: object, event: object, device_identifier: str) -> None:
        print("NUEVO MENSAJE RECIBIDO EN EL DISPOSITIVO:", device_identifier)

        # Query the current SIM identification (CCID code)
        query_ccid = core.request_property(device_identifier, QueryCCID)

        # Verify query results
        if not query_ccid.ccid: print(f"[APPLICATION.EVENTS.ON_MESSAGE_RECEIVED] There was an error querying the current SIM identification (CCID code)"); return False

        # Query all the current storage messages
        query_parameters = ReceiveSMSOperationParameters()
        current_storaged_messages = core.request_operation(device_identifier, ReceiveSMS, query_parameters)

        # Process every storaged message
        for message in current_storaged_messages.messages:
            print("Storaged message:")
            print(message.to_dict())

            # Verify if the message already exists on the messages database
            storage_result = self.application.MessagesDatabase.regist_message(
                unique_id=message.generate_uid(),
                imei=device_identifier,
                ccid=query_ccid.ccid.content,
                content=message.content.content,
                message_type=message.type.content,
                status="NOT_READ",
                destinatary=message.sender.content
            )

            # Verify the storage result
            if not storage_result:
                print(f"There was an error storing the message:", message.generate_uid(), "Content:", message.content.content)
                continue

            # Delete the message in the SIM card
            delete_parameters = DeleteSMSOperationParameters(sim_index=message.metadata.sim_index)
            delete_result = core.request_operation(device_identifier, DeleteSMS, delete_parameters)

            # Verify the delete result
            if delete_result.deleted_sms.content:
                print("The message:", message.generate_uid(), "Content:", message.content.content, "Was SUCESSFULLY deleted from the SIM card")
            
            play_sound_notification()
            time.sleep(1)
        
        print(event)

    # Public methods
    def subscribe_event_handlers(self) -> bool:
        for standard_event, handler_function in self.event_handlers.items():
            print("[EVENT_HANDLERS] Subscribing:", standard_event.NAME, "To the function:", handler_function)
            self.application.core.subscribe_notification(standard_event, handler_function)
        
        return True