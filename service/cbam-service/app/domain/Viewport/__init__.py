# ============================================================================
# 🖱️ Viewport Domain Package
# ============================================================================

"""
ReactFlow 뷰포트 관리 도메인

뷰포트 상태, 설정, 모드 등을 관리하는 독립적인 도메인입니다.
"""

# ============================================================================
# 📦 주요 클래스 및 함수 export
# ============================================================================

from .Viewport_entity import Viewport
from .Viewport_schema import (
    ViewportState,
    ViewportSettings,
    ViewportCreateRequest,
    ViewportUpdateRequest,
    ViewportStateUpdateRequest,
    ViewportSettingsUpdateRequest,
    ViewportResponse,
    ViewportListResponse,
    ViewportStateResponse,
    ViewportSearchRequest,
    ViewportStatsResponse,
    ViewportMode,
    ViewportModeResponse
)
from .Viewport_repository import ViewportRepository, ViewportDatabaseConnection
from .Viewport_service import ViewportService
from .Viewport_controller import viewport_router

# ============================================================================
# 🎯 주요 export 목록
# ============================================================================

__all__ = [
    # 엔티티
    "Viewport",
    
    # 스키마
    "ViewportState",
    "ViewportSettings",
    "ViewportCreateRequest",
    "ViewportUpdateRequest",
    "ViewportStateUpdateRequest",
    "ViewportSettingsUpdateRequest",
    "ViewportResponse",
    "ViewportListResponse",
    "ViewportStateResponse",
    "ViewportSearchRequest",
    "ViewportStatsResponse",
    "ViewportMode",
    "ViewportModeResponse",
    
    # 저장소
    "ViewportRepository",
    "ViewportDatabaseConnection",
    
    # 서비스
    "ViewportService",
    
    # 컨트롤러
    "viewport_router",
]

# ============================================================================
# 📊 도메인 정보
# ============================================================================

__version__ = "1.0.0"
__author__ = "Cal_boundary Team"
__description__ = "ReactFlow 뷰포트 관리 도메인"
