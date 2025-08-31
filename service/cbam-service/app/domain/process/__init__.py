# ============================================================================
# 📦 Process Domain Package
# ============================================================================
"""
Process 도메인 패키지
공정(Process) 관련 기능을 제공합니다:
- 공정 생성, 조회, 수정, 삭제
- 제품과의 다대다 관계 관리
- 비동기 데이터베이스 연결 및 관리
"""
from app.domain.process.process_entity import Process
from app.domain.process.process_schema import (
    ProcessCreateRequest, ProcessResponse, ProcessUpdateRequest
)
from app.domain.process.process_repository import ProcessRepository
from app.domain.process.process_service import ProcessService
from app.domain.process.process_controller import router as process_router

__all__ = [
    "Process",
    "ProcessCreateRequest", "ProcessResponse", "ProcessUpdateRequest",
    "ProcessRepository",
    "ProcessService",
    "process_router",
]
