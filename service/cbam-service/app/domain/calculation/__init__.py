# ============================================================================
# 🧮 Calculation Domain Package
# ============================================================================

"""
CBAM 계산 도메인 패키지

이 패키지는 CBAM(Carbon Border Adjustment Mechanism) 계산과 관련된
모든 비즈니스 로직을 포함합니다.

주요 기능:
- 연료 배출량 계산
- 원료 배출량 계산  
- 전구물질 관리
- CBAM 종합 계산
- 계산 통계
"""

from .calculation_entity import Fuel, Material, Precursor, CalculationResult
from .calculation_schema import (
    ProductCreateRequest, ProductResponse
)
from .calculation_service import CalculationService
from .calculation_repository import CalculationRepository
from .calculation_controller import router as calculation_router

__all__ = [
    # Entities
    "Fuel", "Material", "Precursor", "CalculationResult",
    # Schemas
    "ProductCreateRequest", "ProductResponse",
    # Services
    "CalculationService", "CalculationRepository",
    # Router
    "calculation_router"
]