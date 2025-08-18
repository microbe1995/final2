# ============================================================================
# 🔧 Cal_boundary Common Package
# ============================================================================

"""
공통 기능 패키지

데이터베이스, 유틸리티 등 공통으로 사용되는 기능들을 포함합니다.
"""

from .database import DatabaseConfig, DatabaseConnection, db_connection, Base
from .utility import *

__all__ = [
    # Database
    "DatabaseConfig",
    "DatabaseConnection",
    "db_connection",
    "Base",
    
    # Utility
    "validate_color",
    "validate_coordinates", 
    "validate_dimensions",
    "generate_uuid",
    "format_timestamp",
    "sanitize_filename",
    "DEFAULT_COLORS",
    "MAX_DIMENSIONS",
    "SUPPORTED_FORMATS"
]
