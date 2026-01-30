# Library import
import time
from typing import Dict

from ...contracts.events.sim_removed import SIMRemovedEvent

# Classes definition
class EventHandlers:
    def __init__(self,
        application: object
    ) -> None:
        # Instance properties assignment
        self.application = application

        # Instance properties definition
        self.event_handlers: Dict[object, callable] = {
            SIMRemovedEvent:self._on_sim_removed_event
        }
    
    # Private methods
    def _on_sim_removed_event(self, core: object, event: object, device_identifier: str) -> None:
        print(f"[APPLICATION] SE EXTRAJO LA SIM DEL DISPOSITIVO:", device_identifier)
        time.sleep(30)
        print("FINALIZANDO MANEJADOR DE EVENTO")
    
    # Public methods
    def subscribe_event_handlers(self) -> bool:
        for standard_event, handler_function in self.event_handlers.items():
            print("[EVENT_HANDLERS] Subscribing:", standard_event.NAME, "To the function:", handler_function)
            self.application.core.subscribe_notification(standard_event, handler_function)
        
        return True