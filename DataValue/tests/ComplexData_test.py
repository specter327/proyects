# Library import
from ..datavalue import ComplexData

# Execute validations
print("="*5)
print("Validating list of allowed values...")
values_validation = ComplexData(
  data_type=list,
  value=["A", "B", "D"],
  possible_values=["A", "B", "D", "C"]
)
values_validation.validate()
print("Validation completed successfully")

print("="+5)
print("Validating list of IPv4 and IPv6 addresses...")
# IPv4 schema definition
ipv4_schema = PrimitiveData(
  data_type=str,
  value=None,
  maximum_length=15, minimum_length=7,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",

  data_class=True
)

# IPv6 schema definition
ipv6_schema = PrimitiveData(
  data_type=str,
  value=None,
  maximum_length=39, minimum_length=2,
  maximum_size=None, minimum_size=None,
  possible_values=None,
  regular_expression=r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:))$',

  data_class=True
)

ip_address_set = ComplexData(
  data_type=list,
  value=["192.168.0.1", "::1"],
  maximum_length=None, minimum_length=None,
  possible_values=(ipv4_schema, ipv6_schema)
)

ip_address_set.validate()
print("Validation completed successfully")

print("="*5)
print("Validating user profile table...")
user_profile_validator = ComplexData(
  data_type=dict,
  value={
    "USERNAME":"Specter",
    "PASSWORD":"Password123",
    "AGE":19,
  },
  maximum_length=None, minimum_length=None,
  possible_values=([str], [str, int])
)

user_profile_validator.validate()
print("Validation completed successfully")

print("="*5)
print("Validating phone numbers set...")
# Phone number schema definition
phone_number_schema = PrimitiveData(
  data_type=str,
  value=None,
  minimum_length=7, maximum_length=15,
  minimum_size=None, maximum_size=None,
  possible_values=None,
  regular_expression=r"^\+[1-9]\d{6,14}$",
  
  data_class=True
)

# Set of phone numbers definition
phone_numbers_set = ComplexData(
  data_type=list,
  value=["+521240769928", "+79273463798", "+499896239706"],
  maximum_length=None, minimum_length=None,
  possible_values=(phone_number_schema, )
)

phone_numbers_set.validate()

print("Validation completed successfully")