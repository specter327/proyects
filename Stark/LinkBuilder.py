#!/bin/python3
# Library import
import os
import shutil
import sys

# Classes definition
class LinkBuilder:
    def __init__(self,
        target_platform: str
    ) -> None:
        # Instance properties assignment
        self.target_platform = target_platform.upper()
        self.root_directory = os.path.dirname(os.path.abspath(__file__))
        self.distribution_directory = os.path.join(self.root_directory, "distribution_link")
    
    # Public methods
    def build(self) -> bool:
        print(f"[*] Starting Stark-Link build for platform: {self.target_platform}...")

        # Verify the distribution directory existence
        if os.path.exists(self.distribution_directory):
            shutil.rmtree(self.distribution_directory)
        
        # Create the distribution directory
        os.makedirs(self.distribution_directory)

        # Copy the core system
        shutil.copytree(
            os.path.join(self.root_directory, "application/link/system"),
            os.path.join(self.distribution_directory, "system")
        )

        # Copy the shared elements
        shutil.copytree(
            os.path.join(self.root_directory, "application/shared"),
            os.path.join(self.distribution_directory, "shared")
        )

        # Copy the principal script
        shutil.copy2(
            os.path.join(self.root_directory, "application/link/Stark-Link.py"),
            self.distribution_directory
        )

        shutil.copy2(
            os.path.join(self.root_directory, "application/link/__init__.py"),
            self.distribution_directory
        )


        # Finish process
        print(f"[*] Build complete in: {self.distribution_directory}")

        # Return results
        return True

# Execute the software
if __name__ == "__main__":
    link_builder = LinkBuilder("LINUX")
    link_builder.build()