# Library import
from ....contracts.properties.query_ccid import QueryCCID

# Classes definition
class Property(QueryCCID):
    def __init__(self, controller: object):
        self.controller = controller
    
    # Public methods
    def read(self) -> QueryCCID:
        # Execute the AT command for the query operation
        self.controller.ATEngine.send_at_command("AT+CCID")

        # Get the command AT response
        response = self.controller.ATEngine.read_at_response()

        print(f"[SIM800C: Query CCID] Response: {response.content}")

        # Verify the command response
        if b"OK" in response.content:
            ccid = response.content[0].decode("UTF-8").strip()
            print("CCID:", ccid)
            return QueryCCID(
                ccid=ccid,
                status_code=0
            )
        else:
            return QueryCCID(
                ccid=None,
                status_code=1
            )