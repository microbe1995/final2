# ============================================================================
# 📦 Mapping Domain - HS-CN 매핑 도메인
# ============================================================================

"""
HS-CN 매핑 도메인 패키지

이 패키지는 HS 코드와 CN 코드 간의 매핑과 관련된
모든 비즈니스 로직을 포함합니다.

주요 기능:
- HS 코드 조회
- CN 코드 매핑
- 제품 분류 정보 관리
- 매핑 통계
"""

from app.domain.mapping.mapping_entity import HSCNMapping

from app.domain.mapping.mapping_schema import (
    # HS-CN 매핑 관련 스키마
    HSCNMappingCreateRequest,
    HSCNMappingResponse,
    HSCNMappingUpdateRequest,
    HSCNMappingFullResponse,
    HSCNMappingBatchCreateRequest,
    HSCNMappingBatchResponse,
    MappingStatsResponse,
)

from app.domain.mapping.mapping_repository import HSCNMappingRepository
from app.domain.mapping.mapping_service import HSCNMappingService
from app.domain.mapping.mapping_controller import mapping_router

__all__ = [
    # 엔티티
    "HSCNMapping",
    
    # 스키마
    "HSCNMappingCreateRequest",
    "HSCNMappingResponse",
    "HSCNMappingUpdateRequest",
    "HSCNMappingFullResponse",
    "HSCNMappingBatchCreateRequest",
    "HSCNMappingBatchResponse",
    "MappingStatsResponse",
    
    # 서비스 및 컨트롤러
    "HSCNMappingRepository",
    "HSCNMappingService", 
    "mapping_router",
]