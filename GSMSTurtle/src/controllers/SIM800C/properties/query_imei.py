# Library import
from ....contracts.properties.query_imei import QueryIMEI
from .. import NAME as CONTROLLER_NAME
from .. import VERSION as CONTROLLER_VERSION

# Classes definition
class Property(QueryIMEI):
    def __init__(self,
        controller: object
    ) -> None:
        # Instance properties assignment
        self.controller = controller

        # Verify the controller status
        if not self.controller.connection_status:
            raise RuntimeError(f"Controller is not connected with the device")

    # Public methods
    def read(self) -> QueryIMEI:
        # Execute the IMEI query AT command
        self.controller.ATEngine.send_at_command("AT+GSN")

        # Get the command response
        response = self.controller.ATEngine.read_at_response()

        # Verify the response result
        if b"OK" not in response.content: return QueryIMEI(
            imei=None,
            status_code=1
        ); print("OK not in response")

        # Get the IMEI code
        imei_code = None
        for line in response.content:
            try:
                imei_code = int(line)
                imei_code = bytes(line)

                print("Code:", imei_code)
                break
            except:
                pass

        if not imei_code: return QueryIMEI(
            imei=None,
            status_code=1
        )

        # Return results
        return QueryIMEI(
            imei=imei_code.decode("UTF-8"),
            status_code=0
        )