# Library import
from datavalue import PrimitiveData

# Phone number validation
print("="*10)
print("Validating phone number...")
phone_number = PrimitiveData(
  data_type=str,
  value="+34600111222",
  minimum_length=7, # Minimum character length
  maximum_length=15, # Maximum character length
  minimum_size=None, # Not validate the minimum number
  maximum_size=None, # Not validate the maximum number,
  possible_values=None, # Not specify obligatory possible values
  regular_expression=r"^\+[1-9]\d{6,14}$"
)

print("Phone number validated sucessfully:", phone_number.value)

# Connection port validation
print("="*10)
print("Validating connection port...")
connection_port = PrimitiveData(
  data_type=int,
  value=45321,
  minimum_length=1, # Maximum digits
  maximum_length=5, # Minimum digits
  minimum_size=1, # Minimum numerical value
  maximum_size=65535, # Maximum numerical value
  possible_values=None, # Possible options
  regular_expression=None # Regular expression applied
)
print("Connection port validated:", connection_port.value)

# Transport protocol validation
print("="*10)
print("Validating transport protocol...")
transport_protocol = PrimitiveData(
  data_type=str,
  value="TCP",
  maximum_length=None,
  minimum_length=None,
  minimum_size=None,
  maximum_size=None,
  possible_values=("TCP", "UDP"),
  regular_expression=None
)
print("Transport protocol validated:", transport_protocol.value)

# Validating IPv4 address
print("="*10)
print("Validating IPv4 address...")
ip_address = PrimitiveData(
  data_type=str,
  value="192.168.0.1",
  maximum_length=15,
  minimum_length=7,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
print("IPv4 address validated:", ip_address.value)