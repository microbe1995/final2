# ============================================================================
# 🔘 Handle Controller - ReactFlow 핸들 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger
import uuid
from datetime import datetime

from app.domain.handle.handle_service import HandleService
from app.domain.handle.handle_repository import HandleRepository
from app.domain.handle.handle_schema import (
    HandleCreateRequest,
    HandleUpdateRequest,
    HandleResponse,
    HandleListResponse,
    HandleStatsResponse,
    ReactFlowHandleResponse,
    HandleConnectionRequest,
    HandleConnectionResponse
)

# 라우터 생성
handle_router = APIRouter(tags=["handles"])

# 서비스 의존성
def get_handle_repository() -> HandleRepository:
    return HandleRepository(use_database=True)

def get_handle_service() -> HandleService:
    repository = get_handle_repository()
    return HandleService(repository=repository)

# ============================================================================
# 🔘 핸들 기본 CRUD API
# ============================================================================

@handle_router.post("/handle", response_model=HandleResponse, status_code=status.HTTP_201_CREATED)
async def create_handle(
    request: HandleCreateRequest,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🔘 **핸들 생성**
    
    새로운 ReactFlow 핸들을 생성합니다.
    
    - **node_id**: 노드 ID (필수)
    - **flow_id**: 플로우 ID (필수)
    - **type**: 핸들 타입 (source, target, default)
    - **position**: 핸들 위치 (left, right, top, bottom)
    - **style**: 핸들 스타일
    - **data**: 핸들 데이터
    - **is_connectable**: 연결 가능 여부
    - **is_valid_connection**: 유효한 연결 여부
    """
    try:
        logger.info(f"🔘 핸들 생성 API 호출: {request.node_id} -> {request.type.value}")
        
        result = await handle_service.create_handle(request)
        
        logger.info(f"✅ 핸들 생성 API 성공: {result.id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 핸들 생성 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 핸들 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 생성 중 오류가 발생했습니다")

@handle_router.get("/handle/{handle_id}", response_model=HandleResponse)
async def get_handle(
    handle_id: str,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🔍 **핸들 조회**
    
    핸들 ID로 특정 핸들을 조회합니다.
    """
    try:
        logger.info(f"🔍 핸들 조회 API 호출: {handle_id}")
        
        result = await handle_service.get_handle_by_id(handle_id)
        
        if not result:
            logger.warning(f"⚠️ 핸들을 찾을 수 없음: {handle_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="핸들을 찾을 수 없습니다")
        
        logger.info(f"✅ 핸들 조회 API 성공: {handle_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 핸들 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 조회 중 오류가 발생했습니다")

@handle_router.get("/node/{node_id}/handle", response_model=List[HandleResponse])
async def get_handles_by_node(
    node_id: str,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    📋 **노드별 핸들 목록 조회**
    
    특정 노드에 속한 모든 핸들을 조회합니다.
    """
    try:
        logger.info(f"📋 노드별 핸들 목록 조회 API 호출: {node_id}")
        
        result = await handle_service.get_handles_by_node_id(node_id)
        
        logger.info(f"✅ 노드별 핸들 목록 조회 API 성공: {node_id}에 {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 노드별 핸들 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드별 핸들 목록 조회 중 오류가 발생했습니다")

@handle_router.get("/flow/{flow_id}/handle", response_model=List[HandleResponse])
async def get_handles_by_flow(
    flow_id: str,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    📋 **플로우별 핸들 목록 조회**
    
    특정 플로우에 속한 모든 핸들을 조회합니다.
    """
    try:
        logger.info(f"📋 플로우별 핸들 목록 조회 API 호출: {flow_id}")
        
        result = await handle_service.get_handles_by_flow_id(flow_id)
        
        logger.info(f"✅ 플로우별 핸들 목록 조회 API 성공: {flow_id}에 {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 플로우별 핸들 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우별 핸들 목록 조회 중 오류가 발생했습니다")

@handle_router.put("/handle/{handle_id}", response_model=HandleResponse)
async def update_handle(
    handle_id: str,
    request: HandleUpdateRequest,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    ✏️ **핸들 수정**
    
    핸들 정보를 수정합니다.
    """
    try:
        logger.info(f"✏️ 핸들 수정 API 호출: {handle_id}")
        
        result = await handle_service.update_handle(handle_id, request)
        
        if not result:
            logger.warning(f"⚠️ 수정할 핸들을 찾을 수 없음: {handle_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="핸들을 찾을 수 없습니다")
        
        logger.info(f"✅ 핸들 수정 API 성공: {handle_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 핸들 수정 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 수정 중 오류가 발생했습니다")

@handle_router.delete("/handle/{handle_id}")
async def delete_handle(
    handle_id: str,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🗑️ **핸들 삭제**
    
    핸들을 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 핸들 삭제 API 호출: {handle_id}")
        
        result = await handle_service.delete_handle(handle_id)
        
        if result:
            logger.info(f"✅ 핸들 삭제 API 성공: {handle_id}")
            return {"message": "핸들이 성공적으로 삭제되었습니다", "deleted_id": handle_id}
        else:
            logger.warning(f"⚠️ 삭제할 핸들을 찾을 수 없음: {handle_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="핸들을 찾을 수 없습니다")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 핸들 삭제 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 삭제 중 오류가 발생했습니다")

@handle_router.get("/handle", response_model=List[HandleResponse])
async def get_all_handles(
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    📋 **전체 핸들 목록 조회**
    
    모든 핸들 목록을 조회합니다.
    """
    try:
        logger.info(f"📋 전체 핸들 목록 조회 API 호출")
        
        result = await handle_service.get_all_handles()
        
        logger.info(f"✅ 전체 핸들 목록 조회 API 성공: {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 전체 핸들 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전체 핸들 목록 조회 중 오류가 발생했습니다")

# ============================================================================
# 🔗 핸들 연결 관련 API
# ============================================================================

@handle_router.post("/handle/validate-connection")
async def validate_handle_connection(
    request: HandleConnectionRequest,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🔗 **핸들 연결 유효성 검증**
    
    두 핸들 간의 연결이 유효한지 검증합니다.
    """
    try:
        logger.info(f"🔗 핸들 연결 유효성 검증 API 호출: {request.source_handle_id} -> {request.target_handle_id}")
        
        is_valid = await handle_service.validate_connection(
            request.source_handle_id,
            request.target_handle_id
        )
        
        if is_valid:
            logger.info(f"✅ 핸들 연결 유효성 검증 성공: {request.source_handle_id} -> {request.target_handle_id}")
            return HandleConnectionResponse(
                success=True,
                message="핸들 연결이 유효합니다",
                connection_id=f"conn-{uuid.uuid4().hex[:8]}"
            )
        else:
            logger.warning(f"⚠️ 핸들 연결 유효성 검증 실패: {request.source_handle_id} -> {request.target_handle_id}")
            return HandleConnectionResponse(
                success=False,
                message="핸들 연결이 유효하지 않습니다",
                error_details="연결 조건을 만족하지 않습니다"
            )
        
    except Exception as e:
        logger.error(f"❌ 핸들 연결 유효성 검증 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 연결 유효성 검증 중 오류가 발생했습니다")

@handle_router.get("/flow/{flow_id}/connectable-handles", response_model=List[ReactFlowHandleResponse])
async def get_connectable_handles(
    flow_id: str,
    exclude_node_id: Optional[str] = Query(None, description="제외할 노드 ID"),
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🔗 **연결 가능한 핸들들 조회**
    
    특정 플로우에서 연결 가능한 핸들들을 조회합니다.
    """
    try:
        logger.info(f"🔗 연결 가능한 핸들들 조회 API 호출: {flow_id}")
        
        result = await handle_service.get_connectable_handles(flow_id, exclude_node_id)
        
        logger.info(f"✅ 연결 가능한 핸들들 조회 API 성공: {flow_id}에 {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 연결 가능한 핸들들 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="연결 가능한 핸들들 조회 중 오류가 발생했습니다")

# ============================================================================
# 📊 핸들 통계 API
# ============================================================================

@handle_router.get("/handle/stats", response_model=HandleStatsResponse)
async def get_handle_stats(
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    📊 **핸들 통계 조회**
    
    핸들 관련 통계 정보를 조회합니다.
    """
    try:
        logger.info(f"📊 핸들 통계 조회 API 호출")
        
        result = await handle_service.get_handle_stats()
        
        logger.info(f"✅ 핸들 통계 조회 API 성공: 총 {result.total_handles}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 핸들 통계 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🎯 ReactFlow 전용 API
# ============================================================================

@handle_router.post("/node/{node_id}/reactflow-handles", response_model=List[ReactFlowHandleResponse])
async def create_reactflow_handles_for_node(
    node_id: str,
    flow_id: str = Query(..., description="플로우 ID"),
    handle_configs: List[Dict[str, Any]] = None,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🎯 **노드에 ReactFlow 핸들들 자동 생성**
    
    노드에 ReactFlow에서 사용할 핸들들을 자동으로 생성합니다.
    """
    try:
        logger.info(f"🎯 ReactFlow 핸들 자동 생성 API 호출: {node_id}")
        
        # 기본 핸들 설정 (입력/출력)
        if not handle_configs:
            handle_configs = [
                {"type": "target", "position": "left", "is_connectable": True},
                {"type": "source", "position": "right", "is_connectable": True}
            ]
        
        result = await handle_service.create_reactflow_handles_for_node(
            node_id, flow_id, handle_configs
        )
        
        logger.info(f"✅ ReactFlow 핸들 자동 생성 API 성공: {node_id}에 {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 핸들 자동 생성 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ReactFlow 핸들 자동 생성 중 오류가 발생했습니다")

@handle_router.get("/node/{node_id}/reactflow-handles", response_model=List[ReactFlowHandleResponse])
async def get_reactflow_handles_for_node(
    node_id: str,
    handle_service: HandleService = Depends(get_handle_service)
):
    """
    🎯 **노드의 ReactFlow 핸들들 조회**
    
    노드에 속한 ReactFlow 핸들들을 조회합니다.
    """
    try:
        logger.info(f"🎯 ReactFlow 핸들 조회 API 호출: {node_id}")
        
        result = await handle_service.get_reactflow_handles_for_node(node_id)
        
        logger.info(f"✅ ReactFlow 핸들 조회 API 성공: {node_id}에 {len(result)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 핸들 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ReactFlow 핸들 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 핸들 도메인 상태 API
# ============================================================================

@handle_router.get("/handle/status")
async def handle_status_check():
    """
    📊 **핸들 도메인 상태**
    
    핸들 도메인의 현재 상태를 확인합니다.
    """
    try:
        return {
            "status": "active",
            "domain": "handles",
            "message": "핸들 도메인이 정상적으로 작동 중입니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 핸들 도메인 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="핸들 도메인 상태 확인 실패")
