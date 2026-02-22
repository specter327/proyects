# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
import os
import sys

# Configure the module resolution path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Start the application
import system

StarkLinkSystem = system.System()
StarkLinkSystem.start()