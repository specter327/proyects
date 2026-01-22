# Library import
from ....contracts.operations.receive_sms import ReceiveSMS, ReceiveSMSOperationParameters, ReceiveSMSOperationResults
from .. import NAME as CONTROLLER_NAME
from .. import VERSION as CONTROLLER_VERSION
from ....contracts.data_classes.message import Message, MessageMetadata
import time
from typing import List
import re

# Classes definition
class Operation(ReceiveSMS):
    def __init__(self,
        controller: object
    ) -> None:
        # Instance properties assignment
        self.controller = controller

        # Verify the controller status
        if not self.controller.connection_status:
            raise RuntimeError(f"Controller is not connected with the device")
        
        # Instance properties definition
        self.message_pattern = re.compile(r'\+CMGL:\s*(\d+),"([^"]+)","([^"]+)",.*,"([^"]+)"')    
    
    # Private methods
    def _read_all_stored_messages(self) -> List[Message]:
        messages: List[Message] = []
        
        # Consultamos todos los mensajes
        self.controller.ATEngine.send_at_command('AT+CMGL="ALL"')
        
        try:
            # Aumentamos el timeout: la lectura de SIM puede ser muy lenta (I2C/SPI interno del módem)
            response = self.controller.ATEngine.read_at_response(timeout_seconds=30)
            
            if not response or b"OK" not in response.content:
                return messages

            for index in range(len(response.content)):
                line = response.content[index].decode("UTF-8", errors="replace").strip()

                match = self.message_pattern.search(line)
                if match:
                    try:
                        sim_index = int(match.group(1))
                        status = match.group(2)
                        sender = match.group(3)
                        scts = match.group(4)

                        if index + 1 < len(response.content):
                            body_raw = response.content[index + 1].decode("UTF-8", errors="replace").strip()

                            metadata = MessageMetadata(
                                sim_index=sim_index,
                                sim_status=status,
                                network_timestamp=scts,
                                raw_header=line
                            )

                            message = Message(
                                message=body_raw,
                                metadata=metadata,
                                sender=sender,
                                type=Message.TYPE_RECEIVED,
                                timestamp=int(time.time())
                            )

                            messages.append(message)
                    except Exception as Error:
                        print(f"[{CONTROLLER_NAME}] Error parsing message at line: {index}: {Error}")

        except TimeoutError:
            print(f"[{CONTROLLER_NAME}] Critic timeout: The SIM not responses at time")
        
        return messages

    # Public methods
    def execute(self, parameters: ReceiveSMSOperationParameters) -> ReceiveSMSOperationResults:
        # Set the device on text mode
        self.controller.ATEngine.send_at_command("AT+CMGF=1")
        print("Response AT+CMGF=1:", self.controller.ATEngine.read_at_response())

        # Get the current storaged messages
        current_storaged_messages = self._read_all_stored_messages()

        # Prepare results
        print("Messages:")
        print(current_storaged_messages)

        return ReceiveSMSOperationResults(
            current_storaged_messages,
            status_code=0 if current_storaged_messages else 1
        )