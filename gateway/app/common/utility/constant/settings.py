"""
Settings
"""
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.service_port: int = int(os.getenv("SERVICE_PORT", "8080"))
        self.jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30")) 