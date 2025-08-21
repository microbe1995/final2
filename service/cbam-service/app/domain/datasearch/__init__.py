# ============================================================================
# 🔍 DataSearch Domain Package
# ============================================================================

"""
CBAM 데이터 검색 도메인 패키지

이 패키지는 CBAM(Carbon Border Adjustment Mechanism) 데이터 검색과 관련된
모든 비즈니스 로직을 포함합니다.

주요 기능:
- HS코드 검색
- 국가 검색
- 연료 검색
- 원료 검색
- 전구물질 검색
- 검색 통계
"""

from .datasearch_entity import HSCode, CountryCode, FuelSearchData, MaterialSearchData, PrecursorSearchData
from .datasearch_schema import (
    HSCodeSearchResponse, CountrySearchRequest, CountrySearchResponse,
    FuelSearchResponse, MaterialSearchResponse, PrecursorSearchResponse,
    SearchStatsResponse, FuelData, MaterialData, PrecursorData, CountryData
)
from .datasearch_service import DataSearchService
from .datasearch_repository import DataSearchRepository
from .datasearch_controller import datasearch_router

__all__ = [
    # Entities
    "HSCode", "CountryCode", "FuelSearchData", "MaterialSearchData", "PrecursorSearchData",
    # Schemas
    "HSCodeSearchResponse", "CountrySearchRequest", "CountrySearchResponse",
    "FuelSearchResponse", "MaterialSearchResponse", "PrecursorSearchResponse",
    "SearchStatsResponse", "FuelData", "MaterialData", "PrecursorData", "CountryData",
    # Services
    "DataSearchService", "DataSearchRepository",
    # Router
    "datasearch_router"
]