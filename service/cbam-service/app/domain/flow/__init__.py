# ============================================================================
# 🌊 Flow Domain Package
# ============================================================================

"""
ReactFlow 플로우 관리 도메인

플로우 생성, 수정, 삭제 등을 관리하는 도메인입니다.
뷰포트 관련 기능은 Viewport 도메인으로 분리되었습니다.
"""

# ============================================================================
# 📦 주요 클래스 및 함수 export
# ============================================================================

from .flow_entity import Flow
from .flow_schema import (
    FlowCreateRequest,
    FlowUpdateRequest,
    FlowResponse,
    FlowListResponse,
    FlowStateResponse,
    FlowSearchRequest,
    FlowStatsResponse
)
from .flow_repository import FlowRepository, FlowDatabaseConnection
from .flow_service import FlowService
from .flow_controller import flow_router

# ============================================================================
# 🎯 주요 export 목록
# ============================================================================

__all__ = [
    # 엔티티
    "Flow",
    
    # 스키마
    "FlowCreateRequest",
    "FlowUpdateRequest",
    "FlowResponse",
    "FlowListResponse",
    "FlowStateResponse",
    "FlowSearchRequest",
    "FlowStatsResponse",
    
    # 저장소
    "FlowRepository",
    "FlowDatabaseConnection",
    
    # 서비스
    "FlowService",
    
    # 컨트롤러
    "flow_router",
]

# ============================================================================
# 📊 도메인 정보
# ============================================================================

__version__ = "1.0.0"
__author__ = "Cal_boundary Team"
__description__ = "ReactFlow 플로우 관리 도메인 (뷰포트 기능은 Viewport 도메인으로 분리됨)"
