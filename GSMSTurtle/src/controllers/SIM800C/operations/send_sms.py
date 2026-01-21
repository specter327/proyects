# Library import
import time
from ....contracts.operations.send_sms import SendSMS, SendSMSOperationParameters, SendSMSOperationResults
from .. import NAME as CONTROLLER_NAME
from .. import VERSION as CONTROLLER_VERSION

# Classes definition
class Operation(SendSMS):
    def __init__(self,
        controller: object
    ) -> None:
        # Instance property assignment
        self.controller = controller

        # Verify the controller status
        if not self.controller.connection_status:
            raise RuntimeError(f"Controller is not connected with the device")
    
    def execute(self, parameters: SendSMSOperationParameters) -> SendSMSOperationResults:
        # Verify the operation parameters
        if not parameters.validate():
            raise ValueError(f"The operation parameters: {SendSMSOperationParameters}, are invalid.")
        
        # Try the operation execution
        try:
            at = self.controller.ATEngine
            if not at:
                return SendSMSOperationResults(send_result=False, status_code=1)

            # Set the device on text mode
            print("Setting the device on text mode (SMS)...")
            at.send_at_command("AT+CMGF=1")
            r = at.read_at_response()

            # Validate the response
            #if b"OK" not in r.content: raise RuntimeError(f"There was an error on setting the device on text mode: AT+CMGF=1: {r.content}")
            
            print(f"Result: {r.content if r else None}")

            command = f'AT+CMGS="{parameters.destinatary_phone_number.phone_number.content}"'
            print(f"[LOG] Sending AT Command: {command}...")
            at.send_at_command(command)
            print("Command send successfully")

            # Wait for the ">" prompt (timeout 5s)
            response = at.read_at_response()

            print("Response:", response.content)
            # Verify the response
            if b">" not in response.compact(): raise RuntimeError(f"There was an error receiving the prompt simbol: {response.content}")

            # Send the message (Ctrl+Z para finalizar SMS) por transport, no AT
            message_content = parameters.message.content.content
            print(f"[LOG] Sending message: {message_content[:50]}...")
            
            at.send_at_command(f"{message_content}\x1a", append_newline=False)

            # Esperar resultado final (OK / ERROR / +CMS ERROR) con timeout 15s
            response = at.read_at_response(timeout_seconds=60)

            # Validate the final response
            #if c == "OK" or c == "ERROR" or "+CMS ERROR:" in c:

            print(f"[LOG] Final result: {response.content if response else None}")

            if b"OK" in response.content:
                return SendSMSOperationResults(send_result=True, status_code=0)
            if b"+CMS ERROR:" in response.content or b"ERROR" in response.content:
                return SendSMSOperationResults(send_result=False, status_code=3)
            if response is None:
                return SendSMSOperationResults(send_result=False, status_code=2)
            return SendSMSOperationResults(send_result=False, status_code=3)
        
        except KeyboardInterrupt:
            print(f"[{CONTROLLER_NAME}x{CONTROLLER_VERSION}:{SendSMS().name}x{SendSMS().version}] Unknown error: {Error.__class__}")
            return SendSMSOperationResults(send_result=False, status_code=1)