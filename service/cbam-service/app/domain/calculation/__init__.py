# ============================================================================
# 🧮 Calculation Domain Package
# ============================================================================

"""
CBAM 계산 도메인 패키지

이 패키지는 CBAM(Carbon Border Adjustment Mechanism) 계산과 관련된
모든 비즈니스 로직을 포함합니다.

주요 기능:
- 사업장 관리 (Install)
- 제품 관리 (Product)
- 프로세스 관리 (Process)
- 엣지 관리 (Edge)
- CBAM 종합 계산
- 계산 통계
"""

from .calculation_entity import Install, Product, Process, Edge
from .calculation_schema import (
    ProductCreateRequest, ProductResponse, ProductUpdateRequest,
    ProcessCreateRequest, ProcessResponse, ProcessUpdateRequest
)
from .calculation_service import CalculationService
from .calculation_repository import CalculationRepository
from .calculation_controller import router as calculation_router

__all__ = [
    # Entities
    "Install", "Product", "Process", "Edge",
    # Schemas
    "ProductCreateRequest", "ProductResponse", "ProductUpdateRequest",
    "ProcessCreateRequest", "ProcessResponse", "ProcessUpdateRequest",
    # Services
    "CalculationService", "CalculationRepository",
    # Router
    "calculation_router"
]