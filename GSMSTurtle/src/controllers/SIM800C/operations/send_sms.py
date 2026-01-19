# Library import
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
            command = f'AT+CMGS="{parameters.destinatary_phone_number.phone_number.content}"'
            
            print(f"[LOG] Sending AT Command: {command}...")

            # Send the command
            self.controller.transport_layer.send_at_command(command)

            print(f"Command send sucessfully")

            # Wait for the prompt
            prompt = self.controller.transport_layer.read_at_response(timeout=5)
            
            print(f"[LOG] Received prompt: {prompt}")

            # Verify the prompt result
            if ">" not in prompt:
                return SendSMSOperationResults(send_result=False, status_code=2)
            
            # Send the message
            message = f"{parameters.message.content.content}\\x1a"

            print(f"[LOG] Sending message: {message}")

            self.controller.transport_layer.send_at_command(message)

            # Capture the send result
            final_result = self.controller.transport_layer.read_at_response(timeout=15)

            print(f"[LOG] Final result: {final_result}")
            # Evaluate the final result
            if "OK" in final_result:
                return SendSMSOperationResults(send_result=True, status_code=0)
            else:
                return SendSMSOperationResults(send_result=False, status_code=3)
        except Exception as Error:
            print(f"[{CONTROLLER_NAME}x{CONTROLLER_VERSION}:{SendSMS().name}x{SendSMS().version}] Unknown error: {Error.__class__}")
            return SendSMSOperationResults(send_result=False, status_code=1)