# Library import
from ....contracts.events.message_received import MessageReceivedEvent
from ...transport_layers.ATEngine import Event

# Classes definition
class Event(MessageReceivedEvent):
    # Public methods
    def identify(self, content: Event) -> bool:
        if "+CMTI" in content.content: return True
    
    def prepare(self) -> bool:
        # Get the message type from the raw event
        raw_event_content = self.event.compact(encoded=False)
        content = raw_event_content.replace(b"+CMTI: ", b"")

        # Split by coma
        parts = content.split(b",")

        if len(parts) >= 2:
            # Delete trash
            message_type = parts[0].replace(b'"', b'').strip()

            # Extract and convert the SIM index
            sim_index = int(parts[1].strip())

            # Set the data properties
            self.message_type.content = message_type
            self.sim_index.content = sim_index
            
            return True
        
        return False