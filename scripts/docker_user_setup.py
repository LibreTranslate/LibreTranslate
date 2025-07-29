#!/usr/bin/env python3
# scripts/docker_user_setup.py
"""Docker user setup utility for LibreTranslate containers"""

import os
import sys
import subprocess
from pathlib import Path

# Import constants from centralized location
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from const.docker_constants import DockerConstants


class DockerUserManager:
    """Manages user creation and permissions in Docker containers"""
    
    def __init__(self):
        self.constants = DockerConstants
    
    def create_user_commands(self) -> list[str]:
        """Generate shell commands for creating the libretranslate user"""
        return [
            f"addgroup --system --gid {self.constants.USER_GID} {self.constants.USER_NAME}",
            f"adduser --system --uid {self.constants.USER_UID} --gid {self.constants.USER_GID} {self.constants.USER_NAME}",
            f"mkdir -p {self.constants.USER_LOCAL_DIR}",
            f"chown -R {self.constants.USER_NAME}:{self.constants.USER_NAME} {self.constants.USER_LOCAL_DIR}"
        ]
    
    def get_ownership_string(self) -> str:
        """Get ownership string for COPY commands"""
        return f"{self.constants.USER_UID}:{self.constants.USER_GID}"
    
    def generate_dockerfile_user_section(self) -> str:
        """Generate Dockerfile section for user creation"""
        commands = self.create_user_commands()
        return f"""# Create the {self.constants.USER_NAME} user and group
RUN {' && \\\\\\n    '.join(commands)}

# Switch to the {self.constants.USER_NAME} user
USER {self.constants.USER_NAME}"""


if __name__ == "__main__":
    # This can be used to output the user section for Dockerfiles
    manager = DockerUserManager()
    print(manager.generate_dockerfile_user_section())
