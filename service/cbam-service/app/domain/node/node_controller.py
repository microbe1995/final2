# ============================================================================
# 🔵 Node Controller - ReactFlow 노드 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger

from app.domain.node.node_service import NodeService
from app.domain.node.node_repository import NodeRepository
from app.domain.node.node_schema import (
    NodeCreateRequest,
    NodeUpdateRequest,
    NodeResponse,
    ReactFlowNodeResponse,
    NodeListResponse,
    NodeStatsResponse,
    NodeSearchRequest,
    NodeBatchUpdateRequest
)

# 라우터 생성
node_router = APIRouter(tags=["nodes"])

# 서비스 의존성
def get_node_repository() -> NodeRepository:
    return NodeRepository(use_database=True)

def get_node_service() -> NodeService:
    repository = get_node_repository()
    return NodeService(repository=repository)

# ============================================================================
# 🔵 노드 기본 CRUD API
# ============================================================================

@node_router.post("/node", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    request: NodeCreateRequest,
    node_service: NodeService = Depends(get_node_service)
):
    """
    🔵 **노드 생성**
    
    ReactFlow 노드를 생성합니다.
    
    - **flow_id**: 플로우 ID (필수)
    - **type**: 노드 타입 (default, input, output, custom)
    - **position**: 노드 위치 {x, y}
    - **data**: 노드 데이터 {label, description, color, icon, metadata}
    """
    try:
        logger.info(f"🔵 노드 생성 API 호출: {request.data.label}")
        
        result = await node_service.create_node(request)
        
        logger.info(f"✅ 노드 생성 API 성공: {result.id}")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 노드 생성 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 노드 생성 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 생성 중 오류가 발생했습니다")

@node_router.get("/node/{node_id}", response_model=NodeResponse)
async def get_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service)
):
    """
    🔍 **노드 조회**
    
    노드 ID로 특정 노드를 조회합니다.
    """
    try:
        logger.info(f"🔍 노드 조회 API 호출: {node_id}")
        
        result = await node_service.get_node_by_id(node_id)
        
        if not result:
            logger.warning(f"⚠️ 노드를 찾을 수 없음: {node_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="노드를 찾을 수 없습니다")
        
        logger.info(f"✅ 노드 조회 API 성공: {node_id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 노드 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 조회 중 오류가 발생했습니다")

@node_router.get("/flow/{flow_id}/node", response_model=NodeListResponse)
async def get_nodes_by_flow(
    flow_id: str,
    node_service: NodeService = Depends(get_node_service)
):
    """
    📋 **플로우별 노드 목록 조회**
    
    특정 플로우에 속한 모든 노드를 ReactFlow 형식으로 반환합니다.
    프론트엔드에서 바로 사용할 수 있는 형태입니다.
    """
    try:
        logger.info(f"📋 플로우별 노드 조회 API 호출: {flow_id}")
        
        result = await node_service.get_nodes_by_flow_id(flow_id)
        
        logger.info(f"✅ 플로우별 노드 조회 API 성공: {len(result.nodes)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 플로우별 노드 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 목록 조회 중 오류가 발생했습니다")

@node_router.put("/node/{node_id}", response_model=NodeResponse)
async def update_node(
    node_id: str,
    request: NodeUpdateRequest,
    node_service: NodeService = Depends(get_node_service)
):
    """
    ✏️ **노드 수정**
    
    노드의 위치, 데이터, 스타일 등을 수정합니다.
    """
    try:
        logger.info(f"✏️ 노드 수정 API 호출: {node_id}")
        
        result = await node_service.update_node(node_id, request)
        
        if not result:
            logger.warning(f"⚠️ 수정할 노드를 찾을 수 없음: {node_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="노드를 찾을 수 없습니다")
        
        logger.info(f"✅ 노드 수정 API 성공: {node_id}")
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ 노드 수정 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 노드 수정 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 수정 중 오류가 발생했습니다")

@node_router.delete("/node/{node_id}")
async def delete_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service)
):
    """
    🗑️ **노드 삭제**
    
    노드를 삭제합니다.
    """
    try:
        logger.info(f"🗑️ 노드 삭제 API 호출: {node_id}")
        
        deleted = await node_service.delete_node(node_id)
        
        if not deleted:
            logger.warning(f"⚠️ 삭제할 노드를 찾을 수 없음: {node_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="노드를 찾을 수 없습니다")
        
        logger.info(f"✅ 노드 삭제 API 성공: {node_id}")
        return {"message": "노드가 성공적으로 삭제되었습니다", "deleted_id": node_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 노드 삭제 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 삭제 중 오류가 발생했습니다")

# ============================================================================
# 🔄 ReactFlow 이벤트 처리 API
# ============================================================================

@node_router.post("/node/batch-update", response_model=List[ReactFlowNodeResponse])
async def batch_update_nodes(
    request: NodeBatchUpdateRequest,
    node_service: NodeService = Depends(get_node_service)
):
    """
    🔄 **노드 일괄 수정**
    
    ReactFlow의 onNodesChange 이벤트에서 사용됩니다.
    여러 노드의 위치나 속성을 한 번에 변경할 때 사용합니다.
    
    **사용 예시:**
    ```javascript
    const onNodesChange = useCallback(
      (changes) => {
        // 백엔드에 변경사항 전송
        fetch('/api/nodes/batch-update', {
          method: 'POST',
          body: JSON.stringify({ nodes: changes })
        });
        
        // 프론트엔드 상태 업데이트
        setNodes((nds) => applyNodeChanges(changes, nds));
      },
      []
    );
    ```
    """
    try:
        logger.info(f"🔄 노드 일괄 수정 API 호출: {len(request.nodes)}개")
        
        result = await node_service.batch_update_nodes(request)
        
        logger.info(f"✅ 노드 일괄 수정 API 성공: {len(result)}개")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 노드 일괄 수정 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 노드 일괄 수정 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 일괄 수정 중 오류가 발생했습니다")

# ============================================================================
# 🔍 검색 및 통계 API
# ============================================================================

@node_router.get("/node/search", response_model=NodeListResponse)
async def search_nodes(
    flow_id: Optional[str] = Query(default=None, description="플로우 ID"),
    node_type: Optional[str] = Query(default=None, description="노드 타입"),
    label: Optional[str] = Query(default=None, description="노드 레이블 (부분 일치)"),
    node_service: NodeService = Depends(get_node_service)
):
    """
    🔍 **노드 검색**
    
    다양한 조건으로 노드를 검색합니다.
    """
    try:
        logger.info(f"🔍 노드 검색 API 호출: flow_id={flow_id}, type={node_type}, label={label}")
        
        search_request = NodeSearchRequest(
            flow_id=flow_id,
            node_type=node_type,
            label=label
        )
        
        result = await node_service.search_nodes(search_request)
        
        logger.info(f"✅ 노드 검색 API 성공: {len(result.nodes)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 노드 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 검색 중 오류가 발생했습니다")

@node_router.get("/node/stats", response_model=NodeStatsResponse)
async def get_node_stats(
    node_service: NodeService = Depends(get_node_service)
):
    """
    📊 **노드 통계**
    
    전체 노드 통계를 조회합니다.
    - 전체 노드 수
    - 타입별 노드 분포
    - 플로우별 평균 노드 수
    """
    try:
        logger.info(f"📊 노드 통계 API 호출")
        
        result = await node_service.get_node_stats()
        
        logger.info(f"✅ 노드 통계 API 성공: 총 {result.total_nodes}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 노드 통계 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 헬스체크 API
# ============================================================================

@node_router.get("/node/health")
async def node_health_check():
    """
    🏥 **노드 도메인 헬스체크**
    
    노드 도메인의 상태를 확인합니다.
    """
    try:
        # 간단한 연결 테스트
        service = get_node_service()
        
        return {
            "status": "healthy",
            "domain": "nodes",
            "message": "노드 도메인이 정상적으로 작동 중입니다",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 노드 도메인 헬스체크 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="노드 도메인 상태 확인 실패")

# ============================================================================
# 📖 예시 API
# ============================================================================

@node_router.get("/node/examples/basic")
async def get_basic_node_examples():
    """
    📖 **기본 노드 예시**
    
    ReactFlow에서 사용할 수 있는 기본 노드 예시를 반환합니다.
    """
    return {
        "examples": [
            {
                "id": "node_1",
                "type": "input",
                "position": {"x": 250, "y": 25},
                "data": {"label": "Input Node"}
            },
            {
                "id": "node_2",
                "type": "default",
                "position": {"x": 100, "y": 125},
                "data": {"label": "Default Node"}
            },
            {
                "id": "node_3",
                "type": "output",
                "position": {"x": 250, "y": 250},
                "data": {"label": "Output Node"}
            }
        ],
        "description": "ReactFlow 기본 노드 예시입니다. 프론트엔드에서 초기 데이터로 사용할 수 있습니다."
    }

@node_router.get("/node/examples/custom")
async def get_custom_node_examples():
    """
    📖 **커스텀 노드 예시**
    
    고급 기능을 포함한 커스텀 노드 예시를 반환합니다.
    """
    return {
        "examples": [
            {
                "id": "custom_1",
                "type": "custom",
                "position": {"x": 100, "y": 100},
                "data": {
                    "label": "Custom Node",
                    "description": "커스텀 노드 예시",
                    "color": "#ff6b6b",
                    "icon": "🔥",
                    "metadata": {
                        "category": "special",
                        "priority": "high"
                    }
                },
                "style": {
                    "background": "#ff6b6b",
                    "color": "white",
                    "border": "2px solid #ff5252",
                    "borderRadius": "10px"
                }
            }
        ],
        "description": "커스텀 스타일과 메타데이터를 포함한 노드 예시입니다."
    }
