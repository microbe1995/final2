# ============================================================================
# 🔗 Edge Domain - 엣지 도메인 모듈
# ============================================================================

# Controller
from app.domain.edge.edge_controller import router

# Entity
from app.domain.edge.edge_entity import Edge

# Schema
from app.domain.edge.edge_schema import (
    EdgeCreateRequest, EdgeResponse, EdgeUpdateRequest
)

# Service
from app.domain.edge.edge_service import EdgeService

# Repository
from app.domain.edge.edge_repository import EdgeRepository

# ============================================================================
# 📦 외부 노출 인터페이스
# ============================================================================

edge_router = router
__all__ = ["router", "edge_router"]
