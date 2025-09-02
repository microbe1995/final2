# ============================================================================
# 🎭 Dummy Domain - Dummy 데이터 도메인 모듈
# ============================================================================

# Controller
from app.domain.dummy.dummy_controller import router

# Entity
from app.domain.dummy.dummy_entity import DummyData

# Schema
from app.domain.dummy.dummy_schema import (
    DummyDataCreateRequest, DummyDataResponse, DummyDataUpdateRequest, DummyDataListResponse
)

# Service
from app.domain.dummy.dummy_service import DummyService

# Repository
from app.domain.dummy.dummy_repository import DummyRepository

# ============================================================================
# 📦 외부 노출 인터페이스
# ============================================================================

dummy_router = router
__all__ = ["router", "dummy_router"]
