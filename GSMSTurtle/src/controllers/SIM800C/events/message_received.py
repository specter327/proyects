# Library import
from ....contracts.events.message_received import MessageReceivedEvent
from ...transport_layers.ATEngine import Event

# Classes definition
class Event(MessageReceivedEvent):
    # Public methods
    def identify(self, content: Event) -> bool:
        print("MessageReceivedEventImplementation: identifyng...")
        print("Content:", content)
        print("Event content:", content.content)

        if b"+CMTI" in content.content: print("Incoming message detected!!!"); return True
        return False
    
    def prepare(self) -> bool:
        # Get the message type from the raw event
        raw_event_content = self.event.content
        print("Evento crudo de mensaje recibido:", raw_event_content)

        content = raw_event_content.replace(b"+CMTI: ", b"")

        # Split by coma
        parts = content.split(b",")
        print("Partes divididas del evento crudo de mensaje recibido:")
        print(content)

        if len(parts) >= 2:
            # Delete trash
            message_type = parts[0].replace(b'"', b'').strip()

            # Extract and convert the SIM index
            sim_index = int(parts[1].strip())

            # Convert the data
            if message_type == b"SM":
                message_type = "SMS"

            print("Validacion de tipo de contenido de mensaje:")
            print("Message type:", message_type)
            print(self.message_type.validate(message_type))
            
            print("Validacion de indice de SIM:")
            print("SIM index:", sim_index)
            print(self.sim_index.validate(sim_index))

            # Set the data properties
            self.message_type.value = message_type
            self.sim_index.value = sim_index

            return True
        
        return False