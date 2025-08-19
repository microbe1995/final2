# ============================================================================
# 🖱️ Viewport Controller - ReactFlow 뷰포트 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger
import uuid
from datetime import datetime

from app.domain.Viewport.Viewport_service import ViewportService
from app.domain.Viewport.Viewport_repository import ViewportRepository
from app.domain.Viewport.Viewport_schema import (
    ViewportCreateRequest,
    ViewportUpdateRequest,
    ViewportStateUpdateRequest,
    ViewportSettingsUpdateRequest,
    ViewportResponse,
    ViewportListResponse,
    ViewportStateResponse,
    ViewportSearchRequest,
    ViewportStatsResponse,
    ViewportModeResponse
)

viewport_router = APIRouter(tags=["viewports"])

# ============================================================================
# 🔧 의존성 주입
# ============================================================================

def get_viewport_repository() -> ViewportRepository:
    return ViewportRepository(use_database=True)

def get_viewport_service() -> ViewportService:
    repository = get_viewport_repository()
    return ViewportService(repository=repository)

# ============================================================================
# 🖱️ 뷰포트 기본 CRUD API
# ============================================================================

@viewport_router.post("/viewport", response_model=ViewportResponse, status_code=status.HTTP_201_CREATED)
async def create_viewport(
    request: ViewportCreateRequest,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🖱️ **뷰포트 생성**
    
    새로운 뷰포트를 생성합니다.
    
    - **flow_id**: 플로우 ID (필수)
    - **viewport**: 초기 뷰포트 상태 {x, y, zoom}
    - **settings**: 뷰포트 설정 (선택)
    - **metadata**: 뷰포트 메타데이터 (선택)
    """
    try:
        logger.info(f"🖱️ 뷰포트 생성 요청: {request.flow_id}")
        
        viewport = await viewport_service.create_viewport(request)
        
        logger.info(f"✅ 뷰포트 생성 성공: {viewport.id}")
        return viewport
        
    except ValueError as e:
        logger.warning(f"⚠️ 뷰포트 생성 검증 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 뷰포트 생성 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 생성 중 오류가 발생했습니다")

@viewport_router.get("/viewport/{viewport_id}", response_model=ViewportResponse)
async def get_viewport(
    viewport_id: str,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🔍 **뷰포트 조회**
    
    뷰포트 ID로 뷰포트를 조회합니다.
    """
    try:
        logger.info(f"🔍 뷰포트 조회: {viewport_id}")
        
        viewport = await viewport_service.get_viewport_by_id(viewport_id)
        if not viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 조회 성공: {viewport_id}")
        return viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 조회 중 오류가 발생했습니다")

@viewport_router.get("/flow/{flow_id}/viewport", response_model=ViewportResponse)
async def get_viewport_by_flow_id(
    flow_id: str,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🔍 **플로우 뷰포트 조회**
    
    플로우 ID로 뷰포트를 조회합니다.
    """
    try:
        logger.info(f"🔍 플로우 뷰포트 조회: {flow_id}")
        
        viewport = await viewport_service.get_viewport_by_flow_id(flow_id)
        if not viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 플로우 뷰포트 조회 성공: {flow_id}")
        return viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 플로우 뷰포트 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 뷰포트 조회 중 오류가 발생했습니다")

@viewport_router.put("/viewport/{viewport_id}", response_model=ViewportResponse)
async def update_viewport(
    viewport_id: str,
    request: ViewportUpdateRequest,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    ✏️ **뷰포트 수정**
    
    뷰포트 정보를 수정합니다.
    """
    try:
        logger.info(f"✏️ 뷰포트 수정: {viewport_id}")
        
        updated_viewport = await viewport_service.update_viewport(viewport_id, request)
        if not updated_viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수정할 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 수정 성공: {viewport_id}")
        return updated_viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 수정 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 수정 중 오류가 발생했습니다")

@viewport_router.delete("/viewport/{viewport_id}")
async def delete_viewport(
    viewport_id: str,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🗑️ **뷰포트 삭제**
    
    뷰포트를 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 뷰포트 삭제: {viewport_id}")
        
        success = await viewport_service.delete_viewport(viewport_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="삭제할 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 삭제 성공: {viewport_id}")
        return {"message": "뷰포트가 성공적으로 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 삭제 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 삭제 중 오류가 발생했습니다")

@viewport_router.get("/viewport", response_model=ViewportListResponse)
async def get_all_viewports(
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    📋 **모든 뷰포트 조회**
    
    모든 뷰포트 목록을 조회합니다.
    """
    try:
        logger.info(f"📋 모든 뷰포트 조회")
        
        viewports = await viewport_service.get_all_viewports()
        
        logger.info(f"✅ 모든 뷰포트 조회 성공: {viewports.total}개")
        return viewports
        
    except Exception as e:
        logger.error(f"❌ 모든 뷰포트 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 목록 조회 중 오류가 발생했습니다")

# ============================================================================
# 🖱️ 뷰포트 상태 및 설정 관리 API
# ============================================================================

@viewport_router.put("/flow/{flow_id}/viewport/state", response_model=ViewportStateResponse)
async def update_viewport_state(
    flow_id: str,
    request: ViewportStateUpdateRequest,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🔄 **뷰포트 상태 업데이트**
    
    플로우의 뷰포트 상태를 업데이트합니다.
    ReactFlow의 onViewportChange 이벤트에서 사용됩니다.
    
    ```javascript
    const onViewportChange = useCallback(
      (viewport) => {
        fetch(`/api/flows/${flowId}/viewport/state`, {
          method: 'PUT',
          body: JSON.stringify({ viewport })
        });
      },
      [flowId]
    );
    ```
    """
    try:
        logger.info(f"🔄 뷰포트 상태 업데이트: {flow_id}")
        
        updated_viewport = await viewport_service.update_viewport_state(flow_id, request)
        if not updated_viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 상태 업데이트 성공: {flow_id}")
        return updated_viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 상태 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 상태 업데이트 중 오류가 발생했습니다")

@viewport_router.put("/flow/{flow_id}/viewport/settings", response_model=ViewportResponse)
async def update_viewport_settings(
    flow_id: str,
    request: ViewportSettingsUpdateRequest,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    ⚙️ **뷰포트 설정 업데이트**
    
    플로우의 뷰포트 설정을 업데이트합니다.
    """
    try:
        logger.info(f"⚙️ 뷰포트 설정 업데이트: {flow_id}")
        
        updated_viewport = await viewport_service.update_viewport_settings(flow_id, request)
        if not updated_viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 설정 업데이트 성공: {flow_id}")
        return updated_viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 설정 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 설정 업데이트 중 오류가 발생했습니다")

# ============================================================================
# 🔍 뷰포트 검색 및 통계 API
# ============================================================================

@viewport_router.post("/viewport/search", response_model=ViewportListResponse)
async def search_viewports(
    request: ViewportSearchRequest,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🔍 **뷰포트 검색**
    
    조건에 맞는 뷰포트를 검색합니다.
    """
    try:
        logger.info(f"🔍 뷰포트 검색: {request}")
        
        viewports = await viewport_service.search_viewports(request)
        
        logger.info(f"✅ 뷰포트 검색 성공: {viewports.total}개")
        return viewports
        
    except Exception as e:
        logger.error(f"❌ 뷰포트 검색 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 검색 중 오류가 발생했습니다")

@viewport_router.get("/viewport/stats", response_model=ViewportStatsResponse)
async def get_viewport_stats(
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    📊 **뷰포트 통계**
    
    뷰포트 사용 통계를 조회합니다.
    """
    try:
        logger.info(f"📊 뷰포트 통계 조회")
        
        stats = await viewport_service.get_viewport_stats()
        
        logger.info(f"✅ 뷰포트 통계 조회 성공")
        return stats
        
    except Exception as e:
        logger.error(f"❌ 뷰포트 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🎯 뷰포트 모드 관리 API
# ============================================================================

@viewport_router.get("/flow/{flow_id}/viewport/modes", response_model=ViewportModeResponse)
async def get_viewport_modes(
    flow_id: str,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🎯 **뷰포트 모드 조회**
    
    플로우의 사용 가능한 뷰포트 모드와 현재 모드를 조회합니다.
    """
    try:
        logger.info(f"🎯 뷰포트 모드 조회: {flow_id}")
        
        modes = await viewport_service.get_viewport_modes(flow_id)
        
        logger.info(f"✅ 뷰포트 모드 조회 성공: {flow_id}")
        return modes
        
    except Exception as e:
        logger.error(f"❌ 뷰포트 모드 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 모드 조회 중 오류가 발생했습니다")

@viewport_router.post("/flow/{flow_id}/viewport/mode/{mode}", response_model=ViewportResponse)
async def set_viewport_mode(
    flow_id: str,
    mode: str,
    viewport_service: ViewportService = Depends(get_viewport_service)
):
    """
    🎯 **뷰포트 모드 설정**
    
    플로우의 뷰포트 모드를 설정합니다.
    """
    try:
        logger.info(f"🎯 뷰포트 모드 설정: {flow_id} -> {mode}")
        
        # 유효한 모드 검증
        valid_modes = ["default", "design", "map", "presentation"]
        if mode not in valid_modes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"유효하지 않은 모드입니다. 사용 가능한 모드: {', '.join(valid_modes)}")
        
        updated_viewport = await viewport_service.set_viewport_mode(flow_id, mode)
        if not updated_viewport:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우 뷰포트를 찾을 수 없습니다")
        
        logger.info(f"✅ 뷰포트 모드 설정 성공: {flow_id} -> {mode}")
        return updated_viewport
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 뷰포트 모드 설정 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 모드 설정 중 오류가 발생했습니다")

# ============================================================================
# 📊 뷰포트 상태 확인 API
# ============================================================================

@viewport_router.get("/viewport/status")
async def viewport_status_check():
    """
    📊 **뷰포트 도메인 상태**
    
    뷰포트 도메인의 현재 상태를 확인합니다.
    """
    try:
        return {
            "status": "active",
            "domain": "viewports",
            "message": "뷰포트 도메인이 정상적으로 작동 중입니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 뷰포트 도메인 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="뷰포트 도메인 상태 확인 실패")
