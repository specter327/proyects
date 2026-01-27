# Library import
from . import data
from . import functions

from typing import List, Dict
import requests
import base64
from .data.classes.device import Device
from .data.classes.sms import SMSMessageSent

# Constants definition
API_SERVER_PROTOCOL: str = "HTTPS"
API_SERVER_DOMAIN: str = "api.sms-gate.app"
API_SERVER_PORT: int = 443
API_SERVER_FULLPATH: str = f"{API_SERVER_PROTOCOL.lower()}://{API_SERVER_DOMAIN}"

# Classes definition
class SMSGateController:
    # General property definition
    API_PATH: dict = {
        "SERVER_FULLPATH":API_SERVER_FULLPATH,
        "BASE":"/3rdparty/v1",
        "DEVICES":"/devices",
        "MESSAGES":"/messages",
    }
    
    def __init__(self,
        API_USERNAME: str,
        API_PASSWORD: str
    ) -> None:
        # Instance property assigment
        self.API_USERNAME = API_USERNAME
        self.API_PASSWORD = API_PASSWORD
        
        # Instance property definition
        self.API_TOKEN = base64.b64encode(f"{self.API_USERNAME}:{self.API_PASSWORD}".encode()).decode()
    
    def get_available_devices(self) -> List[Dict]:
        query_url = API_SERVER_FULLPATH + self.API_PATH["BASE"] + self.API_PATH["DEVICES"]
        
        query_headers = {
            "accept":"application/json",
            "Authorization":f"Basic {self.API_TOKEN}"
        }

        try:
            response = requests.get(query_url, headers=query_headers, timeout=10)
            
            if response.status_code != 200:
                raise ValueError(f"The response raise a error. Status code: {response.status_code}")
            
            device_list = []
            for device in response.json():
                device_list.append(
                    Device(
                        device.get("createdAt", None),
                        device.get("deletedAt", None),
                        device.get("id", None),
                        device.get("lastSeen", None),
                        device.get("name", None),
                        device.get("updatedAt", None)
                    )
                )
            
            return device_list
        except Exception as Error:
            raise Error
        
    def send_sms(self,
            device: Device,
            phone_number: str,
            message: str,
            sim: int = 1
        ) -> Dict:
        if not device or not phone_number or not message:
            return {
                "error":"Missing required parameters"
            }
        
        
        query_url = API_SERVER_FULLPATH + self.API_PATH["BASE"] + self.API_PATH["MESSAGES"]
        
        query_headers = {
            "accept":"application/json",
            "Authorization":f"Basic {self.API_TOKEN}",
            "Content-Type":"application/json"
        }
        
        query_body = {
            "device":device.id,
            "phoneNumbers":[phone_number],
            "message":message,
            "sim":sim
        }

        try:
            response = requests.post(
                query_url,
                headers=query_headers,
                json=query_body,
                timeout=10
            )

            response.raise_for_status()

            # Prepare SMSMessageSent object
            data_response = response.json()   
            sms_message = SMSMessageSent(
                self,
                data_response.get("id", None),
                data_response.get("deviceId", None),
                data_response.get("state", None),
                data_response.get("recipients", None),
                data_response.get("isHashed", None),
                data_response.get("isEncrypted", None)
            )
        
            # Si la API regresa info JSON estándar
            return sms_message

        except requests.exceptions.HTTPError as http_err:
            return {
                "error": "HTTPError",
                "status_code": response.status_code,
                "response_text": response.text,
                "detail": str(http_err)
            }
        except requests.exceptions.Timeout:
            return {"error": "Timeout", "detail": "The request timed out"}

        except Exception as err:
            return {"error": "Unknown error", "detail": str(err)}