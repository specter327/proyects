# Library import
import requests

# classes definition
class SMSMessageRecipient:
    def __init__(self,
        phone_number: str,
        state: str
    ) -> None:
        # Instance property assigment
        self.phone_number = phone_number
        self.state = state
    
class SMSMessageStatus:
    def __init__(self,
        id: str,
        deviceId: str,
        state: str,
        isHashed: bool,
        isEncrypted: bool,
        recipients: list,
        states: dict
    ) -> None:
        # Instance property assigment
        self.id = id
        self.deviceId = deviceId
        self.state = state
        self.isHashed = isHashed
        self.isEncrypted = isEncrypted
        self.recipients = [
            SMSMessageRecipient(
                r.get("phoneNumber"),
                r.get("state")
            )
            for r in (recipients or [])
        ]
        self.states = states
        self.state_pending = self.states.get("Pending", None)
        self.state_processed = self.states.get("Processed", None)
        self.state_sent = self.states.get("Sent", None)
    
class SMSMessageSent:
    def __init__(self,
        controller: object,
        id: str,
        device_identifier: str,
        state: str,
        recipients: list,
        isHashed: bool,
        isEncrypted: bool
    ) -> None:
        # Instance property assigment
        self._controller = controller
        self.id = id
        self.device_identifier = device_identifier
        self.state = state
        self.recipients = [
            SMSMessageRecipient(
                r.get("phoneNumber"),
                r.get("state")
            )
            for r in (recipients or [])
        ]
            
    # Public methods
    def get_message_status(self) -> object:
        query_url = self._controller.API_PATH["SERVER_FULLPATH"] + self._controller.API_PATH["BASE"] + self._controller.API_PATH["MESSAGES"] + f"/{self.id}"
        
        query_headers = {
            "accept":"application/json",
            "Authorization":f"Basic {self._controller.API_TOKEN}"
        }
        
        response = requests.get(query_url, headers=query_headers, timeout=10)
        response.raise_for_status()
        
        message_data = response.json()
        print(message_data)
        message_status_profile = SMSMessageStatus(
            message_data.get("id", None),
            message_data.get("deviceId", None),
            message_data.get("state", None),
            message_data.get("isHashed", None),
            message_data.get("isEncrypted", None),
            message_data.get("recipients", None),
            message_data.get("states", None)
        )
        
        return message_status_profile