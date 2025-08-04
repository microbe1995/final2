"""
Service Type Enum
"""
from enum import Enum

class ServiceType(str, Enum):
    AUTH = "auth"
    USER = "user"
    CHATBOT = "chatbot"
    REPORT = "report"
    CBAM = "cbam"
    LCA = "lca"
    MESSAGE = "message" 