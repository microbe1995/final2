# ============================================================================
# 🔗 Edge Controller - ReactFlow 엣지 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger
import uuid
from datetime import datetime

from app.domain.edge.edge_service import EdgeService
from app.domain.edge.edge_repository import EdgeRepository
from app.domain.edge.edge_schema import (
    EdgeCreateRequest,
    EdgeUpdateRequest,
    EdgeResponse,
    EdgeListResponse,
    EdgeStatsResponse,
    EdgeSearchRequest,
    EdgeBatchUpdateRequest,
    ConnectionRequest,
    ConnectionResponse,
    EdgeChangesRequest,
    EdgeChangesResponse
)

# 라우터 생성
edge_router = APIRouter(tags=["edges"])

# 서비스 의존성
def get_edge_repository() -> EdgeRepository:
    return EdgeRepository(use_database=True)

def get_edge_service() -> EdgeService:
    repository = get_edge_repository()
    return EdgeService(repository=repository)

# ============================================================================
# 🔗 엣지 기본 CRUD API
# ============================================================================

@edge_router.post("/edge", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_edge(
    request: EdgeCreateRequest,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🔗 **엣지 생성**
    
    새로운 ReactFlow 엣지를 생성합니다.
    
    - **flow_id**: 플로우 ID (필수)
    - **source**: 시작 노드 ID (필수)
    - **target**: 끝 노드 ID (필수)
    - **type**: 엣지 타입 (default, straight, step, smoothstep, bezier, processEdge)
    - **data**: 엣지 데이터 (label, processType 등)
    - **style**: 엣지 스타일
    - **animated**: 애니메이션 여부
    - **hidden**: 숨김 여부
    - **deletable**: 삭제 가능 여부
    """
    try:
        logger.info(f"🔗 엣지 생성 API 호출: {request.source} -> {request.target}")
        
        result = await edge_service.create_edge(request)
        
        logger.info(f"✅ 엣지 생성 API 성공: {result.id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 엣지 생성 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 엣지 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 생성 중 오류가 발생했습니다")

@edge_router.get("/edge/{edge_id}", response_model=EdgeResponse)
async def get_edge(
    edge_id: str,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🔍 **엣지 조회**
    
    ID로 특정 엣지를 조회합니다.
    """
    try:
        logger.info(f"🔍 엣지 조회 API 호출: {edge_id}")
        
        result = await edge_service.get_edge_by_id(edge_id)
        
        if not result:
            logger.warning(f"⚠️ 엣지를 찾을 수 없음: {edge_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 조회 API 성공: {edge_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 엣지 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 조회 중 오류가 발생했습니다")

@edge_router.get("/flow/{flow_id}/edge", response_model=EdgeListResponse)
async def get_edges_by_flow(
    flow_id: str,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    📋 **플로우별 엣지 목록 조회**
    
    특정 플로우의 모든 엣지를 조회합니다.
    """
    try:
        logger.info(f"📋 플로우별 엣지 목록 조회 API 호출: {flow_id}")
        
        result = await edge_service.get_edges_by_flow_id(flow_id)
        
        logger.info(f"✅ 플로우별 엣지 목록 조회 API 성공: {len(result.edges)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 플로우별 엣지 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우별 엣지 목록 조회 중 오류가 발생했습니다")

@edge_router.put("/edge/{edge_id}", response_model=EdgeResponse)
async def update_edge(
    edge_id: str,
    request: EdgeUpdateRequest,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    ✏️ **엣지 수정**
    
    기존 엣지의 정보를 수정합니다.
    """
    try:
        logger.info(f"✏️ 엣지 수정 API 호출: {edge_id}")
        
        result = await edge_service.update_edge(edge_id, request)
        
        if not result:
            logger.warning(f"⚠️ 수정할 엣지를 찾을 수 없음: {edge_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="수정할 엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 수정 API 성공: {edge_id}")
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ 엣지 수정 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 엣지 수정 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 수정 중 오류가 발생했습니다")

@edge_router.delete("/edge/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    edge_id: str,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🗑️ **엣지 삭제**
    
    기존 엣지를 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 엣지 삭제 API 호출: {edge_id}")
        
        deleted = await edge_service.delete_edge(edge_id)
        
        if not deleted:
            logger.warning(f"⚠️ 삭제할 엣지를 찾을 수 없음: {edge_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="삭제할 엣지를 찾을 수 없습니다")
        
        logger.info(f"✅ 엣지 삭제 API 성공: {edge_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 엣지 삭제 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 삭제 중 오류가 발생했습니다")

# ============================================================================
# 🔗 ReactFlow 연결 API (onConnect 핸들러 지원)
# ============================================================================

@edge_router.post("/flow/{flow_id}/connect", response_model=ConnectionResponse, status_code=status.HTTP_201_CREATED)
async def create_connection(
    flow_id: str,
    request: ConnectionRequest,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🔗 **ReactFlow 연결 생성 (onConnect 핸들러)**
    
    ReactFlow의 onConnect 이벤트를 처리하여 새로운 엣지를 생성합니다.
    
    - **source**: 시작 노드 ID (필수)
    - **target**: 끝 노드 ID (필수)
    - **sourceHandle**: 시작 핸들 ID (선택)
    - **targetHandle**: 끝 핸들 ID (선택)
    """
    try:
        logger.info(f"🔗 ReactFlow 연결 생성 API 호출: {request.source} -> {request.target}")
        
        result = await edge_service.create_connection(flow_id, request)
        
        logger.info(f"✅ ReactFlow 연결 생성 API 성공: {result.edge.id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ ReactFlow 연결 생성 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ ReactFlow 연결 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="연결 생성 중 오류가 발생했습니다")

# ============================================================================
# 🔄 엣지 변경사항 API (onEdgesChange 핸들러 지원)
# ============================================================================

@edge_router.post("/flow/{flow_id}/edge/changes", response_model=EdgeChangesResponse)
async def process_edge_changes(
    flow_id: str,
    request: EdgeChangesRequest,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🔄 **엣지 변경사항 처리 (onEdgesChange 핸들러)**
    
    ReactFlow의 onEdgesChange 이벤트를 처리합니다.
    
    - **changes**: 변경사항 목록 (add, remove, select 등)
    """
    try:
        logger.info(f"🔄 엣지 변경사항 처리 API 호출: {len(request.changes)}개")
        
        result = await edge_service.process_edge_changes(flow_id, request)
        
        logger.info(f"✅ 엣지 변경사항 처리 API 성공: {result.processed_changes}개")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 엣지 변경사항 처리 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 엣지 변경사항 처리 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 변경사항 처리 중 오류가 발생했습니다")

# ============================================================================
# 📊 엣지 일괄 처리 및 고급 기능 API
# ============================================================================

@edge_router.post("/edge/batch-update", response_model=EdgeListResponse)
async def batch_update_edges(
    request: EdgeBatchUpdateRequest,
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    📊 **엣지 일괄 수정**
    
    여러 엣지를 한 번에 수정합니다.
    """
    try:
        logger.info(f"📊 엣지 일괄 수정 API 호출: {len(request.edges)}개")
        
        result = await edge_service.batch_update_edges(request)
        
        logger.info(f"✅ 엣지 일괄 수정 API 성공: {len(result.edges)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 엣지 일괄 수정 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 일괄 수정 중 오류가 발생했습니다")

@edge_router.get("/edge/search", response_model=EdgeListResponse)
async def search_edges(
    flow_id: Optional[str] = Query(None, description="플로우 ID"),
    source: Optional[str] = Query(None, description="시작 노드 ID"),
    target: Optional[str] = Query(None, description="끝 노드 ID"),
    type: Optional[str] = Query(None, description="엣지 타입"),
    animated: Optional[bool] = Query(None, description="애니메이션 여부"),
    hidden: Optional[bool] = Query(None, description="숨김 여부"),
    edge_service: EdgeService = Depends(get_edge_service)
):
    """
    🔍 **엣지 검색**
    
    다양한 조건으로 엣지를 검색합니다.
    """
    try:
        logger.info(f"🔍 엣지 검색 API 호출")
        
        search_request = EdgeSearchRequest(
            flow_id=flow_id,
            source=source,
            target=target,
            type=type,
            animated=animated,
            hidden=hidden
        )
        
        result = await edge_service.search_edges(search_request)
        
        logger.info(f"✅ 엣지 검색 API 성공: {len(result.edges)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 엣지 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 검색 중 오류가 발생했습니다")

@edge_router.get("/edge/stats", response_model=EdgeStatsResponse)
async def get_edge_stats(edge_service: EdgeService = Depends(get_edge_service)):
    """
    📊 **엣지 통계 조회**
    
    엣지 관련 통계 정보를 조회합니다.
    """
    try:
        logger.info(f"📊 엣지 통계 조회 API 호출")
        
        result = await edge_service.get_edge_stats()
        
        logger.info(f"✅ 엣지 통계 조회 API 성공")
        return result
        
    except Exception as e:
        logger.error(f"❌ 엣지 통계 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="엣지 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 헬스체크 및 예제 API
# ============================================================================

@edge_router.get("/edge/health")
async def edge_health_check():
    """엣지 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "ReactFlow Edge Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@edge_router.get("/edge/examples/basic")
async def get_basic_edge_example():
    """기본 엣지 예제"""
    return {
        "example_edge": {
            "id": "edge-1",
            "source": "node-1",
            "target": "node-2",
            "type": "default",
            "data": {
                "label": "연결",
                "processType": "standard"
            }
        },
        "usage": "이 예제를 참고하여 엣지를 생성하세요"
    }

@edge_router.get("/edge/examples/onconnect")
async def get_onconnect_example():
    """onConnect 핸들러 예제"""
    return {
        "frontend_usage": {
            "onConnect": "useCallback((params) => { /* API 호출 */ }, [])",
            "api_endpoint": "POST /flow/{flow_id}/connect",
            "request_body": {
                "source": "node-1",
                "target": "node-2",
                "sourceHandle": "handle-1",
                "targetHandle": "handle-2"
            }
        },
        "description": "ReactFlow onConnect 핸들러 사용 예제"
    }
