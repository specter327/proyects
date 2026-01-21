# Library import
from ....contracts.operations.receive_sms import ReceiveSMS, ReceiveSMSOperationParameters, ReceiveSMSOperationResults
from .. import NAME as CONTROLLER_NAME
from .. import VERSION as CONTROLLER_VERSION
from ....contracts.data_classes.message import Message
import time
from typing import List

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
    
    # Private methods
    def _read_sms_at_index(self, index: int):
        at = self.controller.ATEngine
        at.send_at_command(f"AT+CMGR={index}")
        resp = at.read_at_response()
        
        # La respuesta de CMGR en modo texto es:
        # [b'+CMGR: "REC UNREAD","+52...",,"23/10/26,12:00:00+08"', b'Texto del mensaje', b'OK']
        if b"OK" in resp.content and len(resp.content) >= 2:
            # Aquí instanciarías tu clase Message con los datos parseados
            # ...
            message = Message(resp.content[-2].decode("UTF-8"), timestamp=time.time(), type=Message.TYPE_RECEIVED)

            return message
        return None

    def _read_all_stored_messages(self) -> List[Message]:
        at = self.controller.ATEngine
        messages: List[Message] = []
        
        # Consultamos todos los mensajes
        at.send_at_command('AT+CMGL="ALL"')
        
        try:
            # Aumentamos el timeout: la lectura de SIM puede ser muy lenta (I2C/SPI interno del módem)
            response = at.read_at_response(timeout_seconds=30)
            
            if not response or b"OK" not in response.content:
                return messages

            for i, line in enumerate(response.content):
                # Buscamos la cabecera: +CMGL: <index>,<stat>,<oa>,[<alpha>],[<scts>]
                if line.startswith(b"+CMGL:"):
                    try:
                        # Extraemos metadatos (opcional pero recomendado para Message)
                        # Ejemplo: b'+CMGL: 1,"REC READ","+5256...","","24/01/21,00:00:00+00"'
                        metadata = line.split(b',')
                        sender = metadata[2].replace(b'"', b'')
                        
                        # El cuerpo es la siguiente línea que NO sea otra cabecera ni OK
                        if i + 1 < len(response.content):
                            body = response.content[i + 1]
                            if not body.startswith(b"+CMGL:") and body != b"OK":
                                # Instanciamos con datos reales
                                msg = Message(
                                    message=body.decode("UTF-8"), 
                                    timestamp=time.time(), # Aquí podrías parsear el string de fecha del módem
                                    type=Message.TYPE_RECEIVED
                                )
                                # Agregamos una propiedad extra para de-duplicación por índice de SIM si lo deseas
                                msg.sim_index = int(metadata[0].split(b':')[1].strip())
                                messages.append(msg)
                    except Exception as e:
                        print(f"[ERROR] Parsing CMGL line {i}: {e}")
                            
        except TimeoutError:
            print("[ERROR] Timeout crítico en CMGL. El buffer no se llenó a tiempo.")
            
        return messages

    def _merge_messages(self, list_a: List[Message], list_b: List[Message]) -> List[Message]:
        merged = {}
        
        for msg in list_a + list_b:
            # Generamos una firma única (SHA-1 o simplemente concatenación)
            # Si el contenido es bytes, lo usamos directamente
            content_raw = msg.content.content if hasattr(msg.content, 'content') else msg.content
            
            # Firma: Hash del contenido para ahorrar memoria en el dict
            signature = hash(content_raw)
            
            if signature not in merged:
                merged[signature] = msg
                
        return list(merged.values())

    # Public methods
    def execute(self, parameters: ReceiveSMSOperationParameters) -> ReceiveSMSOperationResults:
        print("Executing ReadSMS Operation...")

        # Try the operation execution
        current_events = tuple(self.controller.ATEngine.events.keys())
        found_messages: list = []

        # Process and filter every event
        for event_index in current_events:
            event = self.controller.ATEngine.events.get(event_index)

            # Verify the event content
            if b"CMTI" in event.content:
                try:
                    # Parse the event data
                    parts = event.content.split(b",")
                    if len(parts) >= 2:
                        sms_index = int(parts[1].strip())

                        # Query the specific message data
                        message = self._read_sms_at_index(sms_index)

                        # Verify the query result
                        if message:
                            found_messages.append(message)
                        
                        # Mark the event like seen
                        event.mark_seen()
                except KeyboardInterrupt:
                    print(f"[{CONTROLLER_NAME}x{CONTROLLER_VERSION}:{ReceiveSMS().name}x{ReceiveSMS().version}] Unknown error: {Error.__class__}")
            
        # Query current existent messages (not captured like events)
        stored_messages: list = self._read_all_stored_messages()

        # Merge all the messages to get a complete output
        final_list = self._merge_messages(found_messages, stored_messages)

        # Return standard results
        return ReceiveSMSOperationResults(
            final_list,
            status_code=0
        )
