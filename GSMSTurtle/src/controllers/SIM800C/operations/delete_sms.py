# Library import
from ....contracts.operations.delete_sms import DeleteSMS, DeleteSMSOperationParameters, DeleteSMSOperationResults
from .. import NAME as CONTROLLER_NAME
from .. import VERSION as CONTROLLER_VERSION

# Classes definition
class Operation(DeleteSMS):
    def __init__(self,
        controller: object
    ) -> None:
        # Instance properties assignment
        self.controller = controller

        # Verify the controller status
        if not self.controller.connection_status:
            raise RuntimeError(f"Controller is not connected with the device")
    
    # Public methods
    def execute(self, parameters: DeleteSMSOperationParameters) -> DeleteSMSOperationResults:
        # Send the delete message AT command
        self.controller.ATEngine.send_at_command(f"AT+CMGD={parameters.sim_index.content}") 

        # Get the operation response
        response = self.controller.ATEngine.read_at_response()

        # Verify the result
        if response and b"OK" in response.content:
            return DeleteSMSOperationResults(
                deleted_sms=True,
                status_code=0
            )
        else:
            return DeleteSMSOperationResults(
                deleted_sms=False,
                status_code=1
            )