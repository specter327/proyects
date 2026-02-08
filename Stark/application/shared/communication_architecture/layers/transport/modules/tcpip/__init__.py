# Library import
from ... import TransportModuleInterface
from configurations import Configurations, Setting
from datavalue import PrimitiveData, ComplexData
import socket
from typing import Optional
import threading
import traceback

# Constants definition
IPv4Address = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=15, minimum_length=7,
    maximum_size=None, minimum_size=None,
    possible_values=None,
    regular_expression=r"^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$",
    data_class=True
)

IPv6Address = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=40, minimum_length=2,
    maximum_size=None, minimum_size=None,
    possible_values=None,
    regular_expression=r"^(?:([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,7}:|([0-9A-Fa-f]{1,4}:){1,6}:[0-9A-Fa-f]{1,4}|([0-9A-Fa-f]{1,4}:){1,5}(:[0-9A-Fa-f]{1,4}){1,2}|([0-9A-Fa-f]{1,4}:){1,4}(:[0-9A-Fa-f]{1,4}){1,3}|([0-9A-Fa-f]{1,4}:){1,3}(:[0-9A-Fa-f]{1,4}){1,4}|([0-9A-Fa-f]{1,4}:){1,2}(:[0-9A-Fa-f]{1,4}){1,5}|[0-9A-Fa-f]{1,4}:((:[0-9A-Fa-f]{1,4}){1,6})|:((:[0-9A-Fa-f]{1,4}){1,7}|:))$",
    data_class=True
)

IPAddress = PrimitiveData(
    data_type=str,
    value=None,
    maximum_length=None, minimum_length=None,
    maximum_size=None, minimum_size=None,
    possible_values=(IPv4Address, IPv6Address),
    regular_expression=None,
    data_class=True
)

ConnectionPort = PrimitiveData(
    data_type=int,
    value=None,
    maximum_length=None, minimum_length=None,
    maximum_size=65535, minimum_size=1,
    possible_values=None,
    regular_expression=None,
    data_class=True
)

RemoteAddress = Setting(
    value=IPAddress,
    system_name="REMOTE_ADDRESS",
    symbolic_name="Remote address",
    description="Remote address of the device to connect",
    optional=True
)
LocalAddress = Setting(
    value=IPAddress,
    system_name="LOCAL_ADDRESS",
    symbolic_name="Local address",
    description="Local address to listen for connections",
    optional=True
)
LocalPort = Setting(
    value=ConnectionPort,
    system_name="LOCAL_PORT",
    symbolic_name="Local connection port",
    description="Local connection port to receive connections",
    optional=True
)
RemotePort = Setting(
    value=ConnectionPort,
    system_name="REMOTE_PORT",
    symbolic_name="Remote connection port",
    description="Remote connection port to open connections",
    optional=True
)

ModuleConfigurations = Configurations()
ModuleConfigurations.add_setting(RemoteAddress)
ModuleConfigurations.add_setting(LocalAddress)
ModuleConfigurations.add_setting(LocalPort)
ModuleConfigurations.add_setting(RemotePort)


# Classes definition
class TransportModule(TransportModuleInterface):
    # Class definition properties
    MODULE_NAME: str = "TRANSPORT_TCP_IP"
    CONFIGURATIONS: Configurations = ModuleConfigurations

    def __init__(self, layer: object) -> None:
        # Constructor hereditance
        super().__init__(layer)

        # Instance properties definition
        self._socket: Optional[socket.socket] = None
        self._reception_data_buffer: bytearray = bytearray()
        self._active: bool = False
        self._is_connected: bool = False
        self._status = self.CONNECTION_STATUS_CLOSED
        self._lock = threading.Lock()

        self.configurations = self.CONFIGURATIONS

        # Concurrent work
        self._receiver_data_thread: Optional[threading.Thread] = None
        self._listener_connections_thread: Optional[threading.Thread] = None
    
    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def is_connected(self) -> bool:
        return self._status == self.CONNECTION_STATUS_ESTABLISHED
    
    @property
    def connection_status(self) -> str:
        return self._status
    
    @property
    def reception_buffer(self) -> bytes:
        with self._lock:
            return bytes(self._reception_data_buffer)
    
    @property
    def connection_controller(self) -> Optional[socket.socket]:
        return self._socket

    # Public methods
    def start(self) -> bool:
        if self._active:
            return True
        
        self._active = True
        self._status = self.CONNECTION_STATUS_CLOSED
        return True
    
    def stop(self) -> bool:
        self._active = False
        self.disconnect()
        return True
    
    def configure(self, configurations: Configurations) -> bool:
        self.configurations = configurations
        return True
    
    def connect(self) -> bool:
        if not self._active: return False

        remote_address = self.configurations.query_setting("REMOTE_ADDRESS").value
        remote_port = self.configurations.query_setting("REMOTE_PORT").value

        # Validate the configurations
        if not remote_address.validate(remote_address.value):
            raise ValueError(f"The specified remote address is invalid: {remote_address.value}")
    
        if not remote_port.validate(remote_port.value):
            raise ValueError(f"The specified remote port is invalid: {remote_port.value}")
        
        # Determine the socket type (IPv4/IPv6)
        ip_type = socket.AF_INET6 if ":" in remote_address.value else socket.AF_INET

        # Create the connection controller
        self._socket = socket.socket(ip_type, socket.SOCK_STREAM) # IPv4/IPv6 - TCP

        # Establish the connection
        try:
            self._socket.connect((remote_address.value, remote_port.value))

            # Update the current status
            self._status = self.CONNECTION_STATUS_ESTABLISHED
            self._is_connected = True
        except:
            print("Error en la conexion")
            traceback.print_exc()
            return False
        
        # Launch the support routines
        self._start_data_receiver()
        return True
    
    def write(self, data: bytes) -> bool:
        if not self._is_connected or not self._socket:
            return False
        
        try:
            self._socket.sendall(data)
            return True
        except (socket.error, BrokenPipeError):
            self._status = self.CONNECTION_STATUS_LOST
            return False
    
    def read(self, limit: int = None, timeout: int = None) -> bytes:
        with self._lock:
            if not self._reception_data_buffer:
                return b""
            
            length = limit if limit is not None else len(self._reception_data_buffer)
            readed_data = bytes(self._reception_data_buffer[:length])
            
            # Delete the readed data
            del self._reception_data_buffer[:length]

            return readed_data

    def disconnect(self) -> bool:
        self._status = self.CONNECTION_STATUS_CLOSED
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            except:
                pass
        
        return True
    
    def receive_connection(self) -> bool:
        if not self._active or self._listener_connections_thread: return False

        self._listener_connections_thread = threading.Thread(
            target=self._listener_connections_routine,
            daemon=True
        )
        self._listener_connections_thread.start()
        return True
    
    # Private methods
    def _start_data_receiver(self) -> bool:
        self._receiver_data_thread = threading.Thread(
            target=self._receiver_data_routine,
            daemon=True
        )
        self._receiver_data_thread.start()
        return True
    
    def _receiver_data_routine(self) -> None:
        while self._is_connected and self._socket:
            try:
                new_data = self._socket.recv(4096)
                if not new_data: break
                with self._lock:
                    self._reception_data_buffer.extend(new_data)
            except:
                break
        self._status = self.CONNECTION_STATUS_CLOSED
    
    def _listener_connections_routine(self) -> None:
        local_address = self.configurations.query_setting("LOCAL_ADDRESS").value
        local_port = self.configurations.query_setting("LOCAL_PORT").value

        # Validate the data
        if not local_address.validate(local_address.value):
            raise ValueError(f"The local address: {local_address.value}, is invalid")
    
        if not local_port.validate(local_port.value):
            raise ValueError(f"The local port: {local_port.value}, is invalid")
        
        ip_type = socket.AF_INET6 if ":" in local_address.value else socket.AF_INET

        # Try to create the server
        server_socket = socket.socket(ip_type, socket.SOCK_STREAM)

        # Configure the server
        try:
            server_socket.bind((local_address.value, local_port.value))
        except:
            return False
        
        server_socket.listen(1)
        server_socket.settimeout(1)

        # Update the local status
        self._status = self.CONNECTION_STATUS_LISTENING

        while self._active:
            try:
                new_connection, remote_address = server_socket.accept()
            except socket.timeout:
                continue

            with self._lock:
                if self._is_connected:
                    new_connection.close()
                    continue
                
                # Update the connection received
                self._socket = new_connection 
            
                # Update the connection status
                self._status = self.CONNECTION_STATUS_ESTABLISHED
                self._is_connected = True

            # Start the data receiver routine
            self._start_data_receiver()
