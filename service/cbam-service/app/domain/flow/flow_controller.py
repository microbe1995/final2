# ============================================================================
# 🌊 Flow Controller - ReactFlow 플로우 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger
import uuid
from datetime import datetime

from app.domain.flow.flow_service import FlowService
from app.domain.flow.flow_repository import FlowRepository
from app.domain.flow.flow_schema import (
    FlowCreateRequest,
    FlowUpdateRequest,
    # FlowViewportUpdateRequest,  # Viewport 도메인으로 분리됨
    FlowResponse,
    FlowListResponse,
    ReactFlowStateResponse,
    FlowSearchRequest,
    FlowStatsResponse
)

# 라우터 생성
flow_router = APIRouter(tags=["flows"])

# 서비스 의존성
def get_flow_repository() -> FlowRepository:
    return FlowRepository(use_database=True)

def get_flow_service() -> FlowService:
    repository = get_flow_repository()
    return FlowService(repository=repository)

# 임시 메모리 저장소 (테스트용)
flows_storage = {}

# ============================================================================
# 🌊 플로우 기본 CRUD API
# ============================================================================

@flow_router.post("/flow", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    request: FlowCreateRequest,
    flow_service: FlowService = Depends(get_flow_service)
):
    """
    🌊 **플로우 생성**
    
    새로운 ReactFlow 플로우를 생성합니다.
    
    - **name**: 플로우 이름 (필수)
    - **description**: 플로우 설명
    - **viewport**: 초기 뷰포트 상태 {x, y, zoom}
    - **settings**: 플로우 설정
    - **metadata**: 플로우 메타데이터
    """
    try:
        logger.info(f"🌊 플로우 생성 API 호출: {request.name}")
        
        result = await flow_service.create_flow(request)
        
        logger.info(f"✅ 플로우 생성 API 성공: {result.id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 플로우 생성 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 플로우 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 생성 중 오류가 발생했습니다")

@flow_router.get("/flow/{flow_id}", response_model=FlowResponse)
async def get_flow(flow_id: str):
    """
    🔍 **플로우 조회**
    
    플로우 ID로 특정 플로우를 조회합니다.
    """
    try:
        logger.info(f"🔍 플로우 조회 API 호출: {flow_id}")
        
        if flow_id not in flows_storage:
            logger.warning(f"⚠️ 플로우를 찾을 수 없음: {flow_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우를 찾을 수 없습니다")
        
        flow_data = flows_storage[flow_id]
        
        logger.info(f"✅ 플로우 조회 성공: {flow_id}")
        return FlowResponse(**flow_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 플로우 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 조회 중 오류가 발생했습니다")

@flow_router.get("/flow", response_model=FlowListResponse)
async def get_flows(flow_service: FlowService = Depends(get_flow_service)):
    """
    📋 **플로우 목록 조회**
    
    모든 플로우 목록을 조회합니다.
    """
    try:
        logger.info(f"📋 플로우 목록 조회 API 호출")
        
        result = await flow_service.get_all_flows()
        
        logger.info(f"✅ 플로우 목록 조회 API 성공: {len(result.flows)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 플로우 목록 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 목록 조회 중 오류가 발생했습니다")

@flow_router.put("/flow/{flow_id}", response_model=FlowResponse)
async def update_flow(flow_id: str, request: FlowUpdateRequest):
    """
    ✏️ **플로우 수정**
    
    플로우 정보를 수정합니다.
    """
    try:
        logger.info(f"✏️ 플로우 수정 API 호출: {flow_id}")
        
        if flow_id not in flows_storage:
            logger.warning(f"⚠️ 수정할 플로우를 찾을 수 없음: {flow_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우를 찾을 수 없습니다")
        
        flow_data = flows_storage[flow_id]
        
        # 수정할 필드 업데이트
        if request.name is not None:
            flow_data["name"] = request.name
        
        if request.description is not None:
            flow_data["description"] = request.description
        
        if request.viewport is not None:
            flow_data["viewport"] = {
                "x": request.viewport.x,
                "y": request.viewport.y,
                "zoom": request.viewport.zoom
            }
        
        if request.settings is not None:
            flow_data["settings"] = request.settings
        
        if request.metadata is not None:
            flow_data["flow_metadata"] = request.metadata
        
        flow_data["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"✅ 플로우 수정 성공: {flow_id}")
        return FlowResponse(**flow_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 플로우 수정 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 수정 중 오류가 발생했습니다")

@flow_router.delete("/flow/{flow_id}")
async def delete_flow(flow_id: str):
    """
    🗑️ **플로우 삭제**
    
    플로우를 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 플로우 삭제 API 호출: {flow_id}")
        
        if flow_id not in flows_storage:
            logger.warning(f"⚠️ 삭제할 플로우를 찾을 수 없음: {flow_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우를 찾을 수 없습니다")
        
        del flows_storage[flow_id]
        
        logger.info(f"✅ 플로우 삭제 성공: {flow_id}")
        return {"message": "플로우가 성공적으로 삭제되었습니다", "deleted_id": flow_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 플로우 삭제 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 삭제 중 오류가 발생했습니다")

# ============================================================================
# 📱 뷰포트 관리 API (Viewport 도메인으로 분리됨)
# ============================================================================

# ============================================================================
# 🎯 ReactFlow 전체 상태 API
# ============================================================================

@flow_router.get("/flow/{flow_id}/state", response_model=ReactFlowStateResponse)
async def get_flow_state(flow_id: str):
    """
    🎯 **ReactFlow 전체 상태 조회**
    
    플로우, 노드, 엣지를 포함한 전체 ReactFlow 상태를 반환합니다.
    프론트엔드에서 ReactFlow 초기화 시 사용됩니다.
    
    **사용 예시:**
    ```javascript
    useEffect(() => {
      const loadFlowState = async () => {
        const response = await fetch(`/api/flows/${flowId}/state`);
        const { flow, nodes, edges } = await response.json();
        
        setNodes(nodes);
        setEdges(edges);
        setViewport(flow.viewport);
      };
      
      loadFlowState();
    }, [flowId]);
    ```
    """
    try:
        logger.info(f"🎯 ReactFlow 전체 상태 조회 API 호출: {flow_id}")
        
        if flow_id not in flows_storage:
            logger.warning(f"⚠️ 플로우를 찾을 수 없음: {flow_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="플로우를 찾을 수 없습니다")
        
        flow_data = flows_storage[flow_id]
        
        # 임시로 빈 노드/엣지 반환 (실제로는 Node/Edge 서비스에서 조회)
        response = ReactFlowStateResponse(
            flow=FlowResponse(**flow_data),
            nodes=[],  # 실제로는 node_service.get_nodes_by_flow_id(flow_id) 호출
            edges=[]   # 실제로는 edge_service.get_edges_by_flow_id(flow_id) 호출
        )
        
        logger.info(f"✅ ReactFlow 전체 상태 조회 성공: {flow_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ReactFlow 전체 상태 조회 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 상태 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 플로우 도메인 상태 API
# ============================================================================

@flow_router.get("/flow/status")
async def flow_status_check():
    """
    📊 **플로우 도메인 상태**
    
    플로우 도메인의 현재 상태를 확인합니다.
    """
    try:
        return {
            "status": "active",
            "domain": "flows",
            "message": "플로우 도메인이 정상적으로 작동 중입니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 플로우 도메인 상태 확인 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="플로우 도메인 상태 확인 실패")

# ============================================================================
# 📖 예시 API
# ============================================================================

@flow_router.get("/flow/examples/basic")
async def get_basic_flow_examples():
    """
    📖 **기본 플로우 예시**
    
    ReactFlow에서 사용할 수 있는 기본 플로우 예시를 반환합니다.
    """
    return {
        "examples": [
            {
                "id": "example_flow_1",
                "name": "Basic Flow",
                "description": "기본 ReactFlow 예시",
                "viewport": {"x": 0, "y": 0, "zoom": 1.0},
                "settings": {
                    "panOnDrag": True,
                    "zoomOnScroll": True,
                    "fitView": True
                },
                "metadata": {
                    "category": "basic",
                    "template": True
                }
            }
        ],
        "description": "ReactFlow 기본 플로우 예시입니다. 프론트엔드에서 템플릿으로 사용할 수 있습니다."
    }

@flow_router.post("/flow/examples/create-sample")
async def create_sample_flow():
    """
    📖 **샘플 플로우 생성**
    
    테스트용 샘플 플로우를 자동 생성합니다.
    """
    try:
        sample_request = FlowCreateRequest(
            name="Sample Flow",
            description="ReactFlow 테스트용 샘플 플로우",
            viewport={"x": 0, "y": 0, "zoom": 1.0},
            settings={"panOnDrag": True, "zoomOnScroll": True},
            metadata={"sample": True, "auto_generated": True}
        )
        
        return await create_flow(sample_request)
        
    except Exception as e:
        logger.error(f"❌ 샘플 플로우 생성 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="샘플 플로우 생성 중 오류가 발생했습니다")
