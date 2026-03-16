# Library import
from securefilehandler import SecureFileHandler, VirtualFileHandler

# Test execution
# Create the virtual file
print("[*] Creating the virtual file...")
virtual_file = VirtualFileHandler()

# Create the secure file handler instance
secure_file = SecureFileHandler(
    file_handler=virtual_file,
    password="SecureFilePASSWORD"
)

# Open the virtual file
print("[*] Opening the virtual file...")
secure_file.open()

# Write data to the file
print("[*] Writing data to the secure file...")
secure_file.write(b"Hello")

# Dump the file raw content
print("==========")
print("Raw content:")
print(secure_file._file_handler._buffer.getvalue())

# Read from the file
print("Reading from the file...")
data = secure_file.read()
print("==========")
print("Readed data:")
print(data)

# Close the secure file
print("Closing the secure file...")
secure_file.close()

print("Test finished")