# Library import
import threading
from typing import List, Dict
from dataclasses import dataclass
import time

# Classes definition
@dataclass
class Response:
    def __init__(self,
        timestamp: int,
        content: list
    ) -> None:
        # Instance properties assignment
        self.timestamp = timestamp
        self.content = content
        
        # Instance properties definition
        self.status_seen: bool = False
    
    # Public methods
    def mark_seen(self) -> bool: self.status_seen = True; return True
    
    def compact(self, encoded=False) -> list:
        if encoded:
            compacted_content = ""
            for line in self.content:
                compacted_content += f"{line.decode('UTF-8')}\r\n"
            
            return compacted_content
        else:
            return b"\r\n".join(self.content)
 
@dataclass
class Event:
    def __init__(self,
        timestamp: int,
        content: list
    ) -> None:
        # Instance properties assignment
        self.timestamp = timestamp
        self.content = content
        
        # Instance properties definition
        self.status_seen: bool = False
    
    # Public methods
    def mark_seen(self) -> bool: self.status_seen = True; return True

    def compact(self, encoded=False) -> list:
        if encoded:
            compacted_content = ""
            for line in self.content:
                compacted_content += f"{line.decode('UTF-8')}\r\n"
            
            return compacted_content
        else:
            return b"\r\n".join(self.content)

class ATEngine:
    def __init__(self,
        transport_layer: object
    ) -> None:
        # Instance properties assignment
        self.transport_layer = transport_layer
        
        # Instance properties definition
        self.status: bool = False
        self._read_bytes_buffer: bytes = b""
        self._read_lines_buffer: List[bytes] = []
        self.events: Dict[int, List[Event]] = {}
        self.responses: Dict[int, List[Response]] = {}
        self._routines: list = [
            self._read_routine,
            self._process_routine,
            self._analize_routine
        ]

    @property
    def responses_counter(self) -> int: return len(self.responses.keys())
    
    @property
    def events_counter(self) -> int: return len(self.events.keys())
    
    @property
    def last_unseen_response(self) -> Response:
        unseen_responses: list = []
        for response_index in self.responses:
            response = self.responses.get(response_index)
            
            if not response.status_seen: unseen_responses.append(response)
        
        if not unseen_responses: return None
        else: return unseen_responses[-1]
    
    @property
    def last_unseen_event(self) -> Event:
        unseen_events: list = []
        for event_index in self.events:
            event = self.events.get(event_index)
            
            if not event.status_seen: unseen_events.append(event)
        
        if not unseen_events: return None
        else: return unseen_events[-1]
    
    @property
    def total_unseen_responses(self) -> int:
        unseen_responses: int = 0
        for response_index in self.responses:
            response = self.responses.get(response_index)
            
            if not response.status_seen: unseen_responses += 1
        
        return unseen_responses

    @property
    def total_unseen_events(self) -> int:
        unseen_events: int = 0
        
        for event_index in self.events:
            event = self.events.get(event_index)
            
            if not event.status_seen: unseen_events += 1
    
        return unseen_events
    
    # Private methods
    def _set_status_active(self) -> bool: self.status = True; return True
    
    def _set_status_inactive(self) -> bool: self.status = False; return True
    
    def _read_routine(self) -> None:
        while self.status:
            # Execution temporizer
            #time.sleep(0.3)

            # Read from the transport layer
            try:
                character_readed = self.transport_layer.read(amount=1)
            except TypeError:
                print(f"[ATEngine] There was an error reading a character on the read routine: TypeError")
                
                # Restablish the character
                pass

            except Exception as Error:
                print(f"[ATEngine] There was an error reading a character on the read routine: {type(Error)}")
                pass

            # Append the new character readed
            self._read_bytes_buffer += character_readed

    
    def _clear_whitespaces(self, content: list) -> list:
        new_list: list = []
        
        for element in content:
            # 1. Verificamos si es un tipo de dato con longitud (str o bytes)
            if isinstance(element, (bytes, str)):
                # 2. Solo agregamos si NO está vacío
                if len(element) > 0:
                    new_list.append(element)
            else:
                # 3. Si es otro tipo (int, float, etc.), lo mantenemos según tu lógica original
                new_list.append(element)
                
        return new_list
    
    def _process_routine(self) -> None:
        while self.status:
            # Execution temporizer
            time.sleep(0.8)

            # Split the current buffer content by lines
            if b"\r\n" not in self._read_bytes_buffer: continue

            new_buffer_lines = self._read_bytes_buffer.split(b"\r\n")

            # Clear the white spaces on the new lines
            new_buffer_lines = self._clear_whitespaces(new_buffer_lines)
            
            # Empty the bytes read buffer, and save the new buffer lines
            self._read_bytes_buffer = bytes()

            for line in new_buffer_lines:
                print("New line:", line)
                self._read_lines_buffer.append(line)            
    
    def _identify_end_response(self, line: bytes) -> bool:
        DELIMITERS: tuple = (
            b"OK", b"ERROR", b"CME ERROR", 
            b"CMS ERROR", b"BUSY", b"NO DIALTONE", 
            b">")
        
        for delimiter_pattern in DELIMITERS:
            if delimiter_pattern in line: return True
        
        return False
    
    def _identify_event_urc(self, line: bytes) -> bool:
        EVENTS: tuple = (
            b"CMTI", b"CMT", b"CDS", 
            b"RING", b"CLIP", b"CREG", 
            b"CGREG", b"CTZV", b"UGNSINF", 
            b"RDY", b"Call Ready", b"SMS Ready", 
            b"UNDER-VOLTAGE", b"OVER-VOLTAGE", b"NORMAL POWER DOWN")
        
        for event_pattern in EVENTS:
            if event_pattern in line: return True
        
        return False
    
    def _analize_routine(self) -> None:
        while self.status:
            # Execution temporizer
            #time.sleep(1.5)

            # Process every line in the read lines buffer until find a end-response delimiter
            if not self._read_lines_buffer: time.sleep(0.5); continue
        
            print("ATEngine: Readlines buffer:", self._read_lines_buffer)
            print("All entries:", len(self._read_lines_buffer))
            
            for line_number in tuple(range(len(self._read_lines_buffer))):
                print("Line number:", line_number)
                print("ATEngine: New Readlines buffer:", self._read_lines_buffer)
                
                # Identify and capture URC events
                if self._identify_event_urc(self._read_lines_buffer[line_number]):
                    # Cut the current content
                    response_line = self._read_lines_buffer[line_number]
                    
                    print("New URC code:", response_line)
                    
                    # Save the new event in a Event dataclass object in the Events structure
                    self.events[self.events_counter] = Event(
                        timestamp=time.time(),
                        content=response_line
                    )
                    
                    # Delete the processed line from the buffer
                    del self._read_lines_buffer[line_number]
                    
                    print("New event:", self.events)
                    break

                if self._identify_end_response(self._read_lines_buffer[line_number]):
                    # Cut the current content
                    response_lines = self._read_lines_buffer[0:line_number+1]
                    
                    print("New response:", response_lines)
                    
                    # Save the new response in a Response dataclass object in the Responses structure
                    self.responses[self.responses_counter] = Response(
                        timestamp=time.time(),
                        content=response_lines
                    )
                    
                    # Delete the processes lines from the buffer
                    del self._read_lines_buffer[0:line_number+1]
                    
                    print("New structured response:", self.responses)
                    structured_response = self.responses.get(self.responses_counter-1)
                    
                    print("Timestamp:", structured_response.timestamp),
                    print("Content:", structured_response.content)
                    
                    break
    
    # Public methods
    def start(self) -> bool:
        self._set_status_active()
        
        # Launch the support routines
        for routine in self._routines:
            routine_thread = threading.Thread(
                target=routine,
                args=[],
                daemon=True
            )
            
            routine_thread.start()
        
        # Return results
        return True
    
    def stop(self) -> bool:
        # Set status inactive
        self._set_status_inactive()
        
        # Return results
        return True
        
    def send_at_command(self, command: str, append_newline: bool = True) -> bool:
        decoded_command = f"{command}".encode("UTF-8")
        
        if append_newline:
            decoded_command += "\r\n".encode("UTF-8")
        
        return self.transport_layer.write(decoded_command)
    
    def read_at_response(self, timeout_seconds: float = 30.0) -> Response:
            start_timestamp = time.monotonic()
            
            # Bucle de sondeo (polling) con guarda de tiempo
            while self.last_unseen_response is None:
                # Verificamos si hemos excedido el tiempo de gracia
                if (time.monotonic() - start_timestamp) > timeout_seconds:
                    raise TimeoutError(f"ATEngine: Timeout excedido ({timeout_seconds}s) esperando respuesta.")
                
                # El sleep de 0.05s reduce la carga de CPU, manteniendo una 
                # latencia de respuesta aceptable para aplicaciones industriales.
                time.sleep(0.05)
            
            # Extracción atómica (local) del objeto antes de marcarlo
            response_to_return = self.last_unseen_response
            response_to_return.mark_seen()
            
            return response_to_return
      
    def mark_all_responses(self) -> int:
        all_marked: int = 0
        for response_index in self.responses:
            response = self.responses.get(response_index)
            
            if not response.status_seen: response.mark_seen(); all_marked += 1
        
        return all_marked