# ============================================================================
# 📦 Calculation Domain - CBAM 계산 도메인
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

from .calculation_entity import (
    Install,
    Product,
    Process,
    ProductProcess,  # 새로운 중간 테이블 엔티티
)

from .calculation_schema import (
    # Install 관련 스키마
    InstallCreateRequest,
    InstallResponse,
    InstallUpdateRequest,
    InstallNameResponse,
    
    # Product 관련 스키마
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    ProductNameResponse,
    
    # Process 관련 스키마
    ProcessCreateRequest,
    ProcessResponse,
    ProcessUpdateRequest,
    
    # ProductProcess 관련 스키마
    ProductProcessCreateRequest,
    ProductProcessResponse,
)

from .calculation_repository import CalculationRepository
from .calculation_service import CalculationService
from .calculation_controller import calculation_router

__all__ = [
    # 엔티티
    "Install",
    "Product", 
    "Process",
    "ProductProcess",
    
    # 스키마
    "InstallCreateRequest",
    "InstallResponse", 
    "InstallUpdateRequest",
    "InstallNameResponse",
    "ProductCreateRequest",
    "ProductResponse",
    "ProductUpdateRequest", 
    "ProductNameResponse",
    "ProcessCreateRequest",
    "ProcessResponse",
    "ProcessUpdateRequest",
    "ProductProcessCreateRequest",
    "ProductProcessResponse",
    
    # 서비스 및 컨트롤러
    "CalculationRepository",
    "CalculationService", 
    "calculation_router",
]