# Library import
from abc import ABC, abstractmethod

# Classes definition
class TransportLayerInterface(ABC):
    "This class represents a TransportLayer for a abstract connection and communication"

    def __init__(self) -> None:
        # Instance property definition
        self._connection_controller: object = None
    
    @property
    def raw(self) -> object:
        return self._connection_controller
    
    # Public methods
    @abstractmethod
    def connect(self) -> bool:
        """This method open a connection with the specified device.
            Raise a exception if there is a exception

            Returns:
                bool: true (success)/false (Error)
        """
        raise NotImplementedError
    
    @abstractmethod
    def disconnect(self) -> bool:
        """This method closes a current connection with the specified device
            Raise a exception if theres a error

            Returns:
                bool: true (success)/false (error)
        """
        raise NotImplementedError
    
    @abstractmethod
    def write(self, data: bytes) -> bool:
        """This method write data to the connection.
            Raise a exception if theres a error
            
            Returns:
                bool: true (success)/false (error)
        """
        raise NotImplementedError
    
    @abstractmethod
    def read(self, amount: int = -1) -> bytes:
        """This method read a definied amount of data (or all if specified: -1) of the connection
            Raise exception if theres a error

            Returns:
                bytes
        """

