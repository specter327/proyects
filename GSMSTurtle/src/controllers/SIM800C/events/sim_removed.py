# Library import
from ....contracts.events.sim_removed import SIMRemovedEvent
from ...transport_layers.ATEngine import Event

# Classes definition
class Event(SIMRemovedEvent):
    # Public methods
    def identify(self, content: Event) -> bool:
        if b"CPIN: NOT READY" in content.content: return True
    
    def prepare(self) -> bool: return True