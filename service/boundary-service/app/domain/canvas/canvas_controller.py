# ============================================================================
# 🖼️ Canvas Controller - Canvas HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from loguru import logger

from app.domain.canvas.canvas_service import CanvasService
from app.domain.canvas.canvas_repository import CanvasRepository
from app.domain.canvas.canvas_schema import (
    CanvasCreateRequest,
    CanvasUpdateRequest,
    CanvasResponse,
    CanvasListResponse,
    CanvasSearchRequest,
    CanvasStatsResponse,
    CanvasExportRequest,
    CanvasImportRequest,
    CanvasDuplicateRequest,
    CanvasTemplateRequest,
    # ReactFlow 관련 스키마
    ReactFlowNode,
    ReactFlowEdge,
    ReactFlowState,
    ReactFlowUpdateRequest,
    NodeChangeEvent,
    EdgeChangeEvent,
    ReactFlowPosition,
    ReactFlowNodeData,
    ReactFlowViewport,
    # Connection 관련 스키마
    ConnectionParams,
    ConnectionEvent,
    ConnectionRequest
)

# 라우터 생성
canvas_router = APIRouter(tags=["canvas"])

# 서비스 의존성
def get_canvas_repository() -> CanvasRepository:
    return CanvasRepository(use_database=True)

def get_canvas_service() -> CanvasService:
    """CanvasService 의존성 주입"""
    repo = get_canvas_repository()
    return CanvasService(repository=repo)

# ============================================================================
# 🎯 CRUD 엔드포인트
# ============================================================================

@canvas_router.post("/", response_model=CanvasResponse, status_code=201)
async def create_canvas(
    request: CanvasCreateRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """새 Canvas를 생성합니다"""
    try:
        logger.info(f"🖼️ Canvas 생성 요청: {request.name}")
        response = await canvas_service.create_canvas(request)
        logger.info(f"✅ Canvas 생성 완료: {response.id}")
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 생성 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 생성 실패: {str(e)}")

@canvas_router.get("/{canvas_id}", response_model=CanvasResponse)
async def get_canvas(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ID로 Canvas를 조회합니다"""
    try:
        logger.info(f"🔍 Canvas 조회 요청: {canvas_id}")
        response = await canvas_service.get_canvas(canvas_id)
        if not response:
            raise HTTPException(status_code=404, detail="Canvas를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 조회 실패: {str(e)}")

@canvas_router.get("/", response_model=CanvasListResponse)
async def get_all_canvases(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """모든 Canvas를 페이지네이션으로 조회합니다"""
    try:
        logger.info(f"📋 Canvas 목록 조회 요청: 페이지 {page}, 크기 {size}")
        response = await canvas_service.get_all_canvases(page=page, size=size)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 목록 조회 실패: {str(e)}")

@canvas_router.put("/{canvas_id}", response_model=CanvasResponse)
async def update_canvas(
    canvas_id: str,
    request: CanvasUpdateRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 수정합니다"""
    try:
        logger.info(f"✏️ Canvas 수정 요청: {canvas_id}")
        response = await canvas_service.update_canvas(canvas_id, request)
        if not response:
            raise HTTPException(status_code=404, detail="수정할 Canvas를 찾을 수 없습니다")
        logger.info(f"✅ Canvas 수정 완료: {canvas_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 수정 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 수정 실패: {str(e)}")

@canvas_router.delete("/{canvas_id}", status_code=204)
async def delete_canvas(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 삭제합니다"""
    try:
        logger.info(f"🗑️ Canvas 삭제 요청: {canvas_id}")
        success = await canvas_service.delete_canvas(canvas_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 Canvas를 찾을 수 없습니다")
        logger.info(f"✅ Canvas 삭제 완료: {canvas_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 삭제 실패: {str(e)}")

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@canvas_router.post("/search", response_model=CanvasListResponse)
async def search_canvases(
    request: CanvasSearchRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """조건에 맞는 Canvas를 검색합니다"""
    try:
        logger.info(f"🔍 Canvas 검색 요청: {len(request.__dict__)}개 조건")
        response = await canvas_service.search_canvases(request)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 검색 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 검색 실패: {str(e)}")

# ============================================================================
# 🎨 Canvas 조작 엔드포인트
# ============================================================================

@canvas_router.post("/{canvas_id}/resize", response_model=CanvasResponse)
async def resize_canvas(
    canvas_id: str,
    new_width: float = Query(..., gt=0, description="새 너비"),
    new_height: float = Query(..., gt=0, description="새 높이"),
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas의 크기를 변경합니다"""
    try:
        logger.info(f"📏 Canvas 크기 변경 요청: {canvas_id} ({new_width}x{new_height})")
        response = await canvas_service.resize_canvas(canvas_id, new_width, new_height)
        if not response:
            raise HTTPException(status_code=404, detail="크기 변경할 Canvas를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 크기 변경 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 크기 변경 실패: {str(e)}")

@canvas_router.post("/{canvas_id}/zoom", response_model=CanvasResponse)
async def set_canvas_zoom(
    canvas_id: str,
    zoom_level: float = Query(..., ge=0.1, le=5.0, description="확대/축소 레벨 (0.1x ~ 5.0x)"),
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas의 확대/축소 레벨을 설정합니다"""
    try:
        logger.info(f"🔍 Canvas 확대/축소 요청: {canvas_id} ({zoom_level}x)")
        response = await canvas_service.set_canvas_zoom(canvas_id, zoom_level)
        if not response:
            raise HTTPException(status_code=404, detail="확대/축소할 Canvas를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 확대/축소 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 확대/축소 실패: {str(e)}")

@canvas_router.post("/{canvas_id}/pan", response_model=CanvasResponse)
async def pan_canvas(
    canvas_id: str,
    dx: float = Query(..., description="X축 이동 거리"),
    dy: float = Query(..., description="Y축 이동 거리"),
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 이동시킵니다"""
    try:
        logger.info(f"🚀 Canvas 이동 요청: {canvas_id} (dx: {dx}, dy: {dy})")
        response = await canvas_service.pan_canvas(canvas_id, dx, dy)
        if not response:
            raise HTTPException(status_code=404, detail="이동할 Canvas를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 이동 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 이동 실패: {str(e)}")

@canvas_router.post("/{canvas_id}/clear", response_model=CanvasResponse)
async def clear_canvas(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas의 모든 요소를 제거합니다"""
    try:
        logger.info(f"🧹 Canvas 초기화 요청: {canvas_id}")
        response = await canvas_service.clear_canvas(canvas_id)
        if not response:
            raise HTTPException(status_code=404, detail="초기화할 Canvas를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Canvas 초기화 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 초기화 실패: {str(e)}")

# ============================================================================
# 🎯 특수 기능 엔드포인트
# ============================================================================

@canvas_router.post("/duplicate", response_model=CanvasResponse)
async def duplicate_canvas(
    request: CanvasDuplicateRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 복제합니다"""
    try:
        logger.info(f"📋 Canvas 복제 요청: {request.new_name}")
        response = await canvas_service.duplicate_canvas(request)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 복제 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 복제 실패: {str(e)}")

@canvas_router.post("/{canvas_id}/export")
async def export_canvas(
    canvas_id: str,
    request: CanvasExportRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 내보냅니다"""
    try:
        logger.info(f"📤 Canvas 내보내기 요청: {canvas_id} ({request.format})")
        response = await canvas_service.export_canvas(canvas_id, request)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 내보내기 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 내보내기 실패: {str(e)}")

@canvas_router.post("/import", response_model=CanvasResponse)
async def import_canvas(
    request: CanvasImportRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas를 가져옵니다"""
    try:
        logger.info(f"📥 Canvas 가져오기 요청")
        response = await canvas_service.import_canvas(request)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 가져오기 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 가져오기 실패: {str(e)}")

@canvas_router.post("/template", response_model=CanvasResponse)
async def create_canvas_template(
    request: CanvasTemplateRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas 템플릿을 생성합니다"""
    try:
        logger.info(f"📋 Canvas 템플릿 생성 요청: {request.template_type}")
        response = await canvas_service.create_canvas_template(request)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 템플릿 생성 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Canvas 템플릿 생성 실패: {str(e)}")

# ============================================================================
# 📊 통계 및 분석 엔드포인트
# ============================================================================

@canvas_router.get("/stats/overview", response_model=CanvasStatsResponse)
async def get_canvas_stats(
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas 통계를 조회합니다"""
    try:
        logger.info("📊 Canvas 통계 조회 요청")
        response = await canvas_service.get_canvas_stats()
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 통계 조회 실패: {str(e)}")

# ============================================================================
# 🔧 유틸리티 엔드포인트
# ============================================================================

@canvas_router.get("/{canvas_id}/bounds")
async def get_canvas_bounds(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """Canvas의 경계를 계산합니다"""
    try:
        logger.info(f"📐 Canvas 경계 계산 요청: {canvas_id}")
        response = await canvas_service.get_canvas_bounds(canvas_id)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 경계 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 경계 계산 실패: {str(e)}")

@canvas_router.get("/{canvas_id}/elements-at-point")
async def get_elements_at_point(
    canvas_id: str,
    x: float = Query(..., description="X 좌표"),
    y: float = Query(..., description="Y 좌표"),
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """주어진 점에 있는 모든 요소를 반환합니다"""
    try:
        logger.info(f"📍 점 근처 요소 조회 요청: {canvas_id} ({x}, {y})")
        response = await canvas_service.get_elements_at_point(canvas_id, x, y)
        return response
    except Exception as e:
        logger.error(f"❌ 점 근처 요소 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"점 근처 요소 조회 실패: {str(e)}")

# ============================================================================
# 🧪 테스트 및 개발용 엔드포인트
# ============================================================================

@canvas_router.get("/health/check")
async def health_check():
    """Canvas 서비스 상태 확인"""
    return {"status": "healthy", "service": "canvas", "message": "Canvas 서비스가 정상 작동 중입니다"}

@canvas_router.get("/debug/info")
async def debug_info(
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """디버그 정보 조회 (개발용)"""
    try:
        # 간단한 통계 정보 반환
        stats = await canvas_service.get_canvas_stats()
        return {
            "service": "canvas",
            "total_canvases": stats.total_canvases,
            "total_shapes": stats.total_shapes,
            "total_arrows": stats.total_arrows,
            "average_canvas_size": stats.average_canvas_size,
            "canvas_usage_stats": stats.canvas_usage_stats
        }
    except Exception as e:
        logger.error(f"❌ 디버그 정보 조회 실패: {str(e)}")
        return {"service": "canvas", "error": str(e)}

# ============================================================================
# 🔄 ReactFlow 전용 API 엔드포인트
# ============================================================================

@canvas_router.post("/reactflow/initialize", response_model=Dict[str, Any])
async def initialize_reactflow_canvas(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 캔버스 초기화 - 기본 노드와 엣지 설정"""
    try:
        logger.info(f"🔄 ReactFlow 캔버스 초기화: {canvas_id}")
        
        # 기본 노드 생성 (요청 사항에 따라)
        initial_nodes = [
            ReactFlowNode(
                id="n1",
                position=ReactFlowPosition(x=0, y=0),
                data=ReactFlowNodeData(label="Node 1"),
                type="input"
            ),
            ReactFlowNode(
                id="n2", 
                position=ReactFlowPosition(x=100, y=100),
                data=ReactFlowNodeData(label="Node 2"),
                type="default"
            )
        ]
        
        # 기본 엣지 생성
        initial_edges = [
            ReactFlowEdge(
                id="n1-n2",
                source="n1",
                target="n2"
            )
        ]
        
        # 캔버스 업데이트
        update_request = ReactFlowUpdateRequest(
            canvas_id=canvas_id,
            nodes=initial_nodes,
            edges=initial_edges,
            viewport=ReactFlowViewport(x=0, y=0, zoom=1)
        )
        
        response = await canvas_service.update_reactflow_state(update_request)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "message": "ReactFlow 캔버스가 초기화되었습니다",
            "initial_state": {
                "nodes": [node.dict() for node in initial_nodes],
                "edges": [edge.dict() for edge in initial_edges],
                "viewport": ReactFlowViewport().dict()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 초기화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ReactFlow 초기화 실패: {str(e)}")

@canvas_router.get("/reactflow/{canvas_id}/state", response_model=ReactFlowState)
async def get_reactflow_state(
    canvas_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 상태 조회"""
    try:
        logger.info(f"📊 ReactFlow 상태 조회: {canvas_id}")
        
        canvas = await canvas_service.get_canvas(canvas_id)
        if not canvas:
            raise HTTPException(status_code=404, detail="Canvas를 찾을 수 없습니다")
        
        # Canvas에서 ReactFlow 상태 추출
        reactflow_state = ReactFlowState(
            nodes=canvas.nodes,
            edges=canvas.edges,
            viewport=canvas.viewport
        )
        
        return reactflow_state
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ReactFlow 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ReactFlow 상태 조회 실패: {str(e)}")

@canvas_router.put("/reactflow/{canvas_id}/state", response_model=Dict[str, Any])
async def update_reactflow_state(
    canvas_id: str,
    state: ReactFlowState,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 상태 업데이트"""
    try:
        logger.info(f"📝 ReactFlow 상태 업데이트: {canvas_id}")
        
        update_request = ReactFlowUpdateRequest(
            canvas_id=canvas_id,
            nodes=state.nodes,
            edges=state.edges,
            viewport=state.viewport
        )
        
        response = await canvas_service.update_reactflow_state(update_request)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "message": "ReactFlow 상태가 업데이트되었습니다",
            "updated_at": response.updated_at
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 상태 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"ReactFlow 상태 업데이트 실패: {str(e)}")

@canvas_router.post("/reactflow/{canvas_id}/nodes", response_model=Dict[str, Any])
async def add_reactflow_node(
    canvas_id: str,
    node: ReactFlowNode,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 노드 추가"""
    try:
        logger.info(f"➕ ReactFlow 노드 추가: {canvas_id} - {node.id}")
        
        response = await canvas_service.add_reactflow_node(canvas_id, node)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "node_id": node.id,
            "message": f"노드 '{node.id}'가 추가되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 노드 추가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노드 추가 실패: {str(e)}")

@canvas_router.delete("/reactflow/{canvas_id}/nodes/{node_id}", response_model=Dict[str, Any])
async def remove_reactflow_node(
    canvas_id: str,
    node_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 노드 제거"""
    try:
        logger.info(f"➖ ReactFlow 노드 제거: {canvas_id} - {node_id}")
        
        response = await canvas_service.remove_reactflow_node(canvas_id, node_id)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "node_id": node_id,
            "message": f"노드 '{node_id}'가 제거되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 노드 제거 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노드 제거 실패: {str(e)}")

@canvas_router.post("/reactflow/{canvas_id}/edges", response_model=Dict[str, Any])
async def add_reactflow_edge(
    canvas_id: str,
    edge: ReactFlowEdge,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 엣지 추가"""
    try:
        logger.info(f"🔗 ReactFlow 엣지 추가: {canvas_id} - {edge.id}")
        
        response = await canvas_service.add_reactflow_edge(canvas_id, edge)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "edge_id": edge.id,
            "message": f"엣지 '{edge.id}'가 추가되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 엣지 추가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 추가 실패: {str(e)}")

@canvas_router.delete("/reactflow/{canvas_id}/edges/{edge_id}", response_model=Dict[str, Any])
async def remove_reactflow_edge(
    canvas_id: str,
    edge_id: str,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 엣지 제거"""
    try:
        logger.info(f"🔗❌ ReactFlow 엣지 제거: {canvas_id} - {edge_id}")
        
        response = await canvas_service.remove_reactflow_edge(canvas_id, edge_id)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "edge_id": edge_id,
            "message": f"엣지 '{edge_id}'가 제거되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 엣지 제거 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 제거 실패: {str(e)}")

@canvas_router.post("/reactflow/{canvas_id}/changes/nodes", response_model=Dict[str, Any])
async def apply_node_changes(
    canvas_id: str,
    changes: List[NodeChangeEvent],
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 노드 변경사항 적용 (이벤트 핸들러)"""
    try:
        logger.info(f"🔄 ReactFlow 노드 변경사항 적용: {canvas_id} - {len(changes)}개 변경")
        
        response = await canvas_service.apply_node_changes(canvas_id, changes)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "changes_applied": len(changes),
            "message": f"{len(changes)}개의 노드 변경사항이 적용되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 노드 변경사항 적용 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"노드 변경사항 적용 실패: {str(e)}")

@canvas_router.post("/reactflow/{canvas_id}/changes/edges", response_model=Dict[str, Any])
async def apply_edge_changes(
    canvas_id: str,
    changes: List[EdgeChangeEvent],
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 엣지 변경사항 적용 (이벤트 핸들러)"""
    try:
        logger.info(f"🔄 ReactFlow 엣지 변경사항 적용: {canvas_id} - {len(changes)}개 변경")
        
        response = await canvas_service.apply_edge_changes(canvas_id, changes)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "changes_applied": len(changes),
            "message": f"{len(changes)}개의 엣지 변경사항이 적용되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 엣지 변경사항 적용 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"엣지 변경사항 적용 실패: {str(e)}")

@canvas_router.get("/reactflow/examples/initial", response_model=Dict[str, Any])
async def get_initial_reactflow_example():
    """ReactFlow 초기 예제 노드/엣지 반환"""
    try:
        logger.info("📝 ReactFlow 초기 예제 반환")
        
        # 요청사항에 맞는 초기 노드/엣지 예제
        initial_nodes = [
            {
                "id": "n1",
                "position": {"x": 0, "y": 0},
                "data": {"label": "Node 1"},
                "type": "input"
            },
            {
                "id": "n2",
                "position": {"x": 100, "y": 100},
                "data": {"label": "Node 2"}
            }
        ]
        
        initial_edges = [
            {
                "id": "n1-n2",
                "source": "n1",
                "target": "n2"
            }
        ]
        
        return {
            "success": True,
            "message": "ReactFlow 초기 예제",
            "initialNodes": initial_nodes,
            "initialEdges": initial_edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1},
            "usage": {
                "description": "이 데이터를 사용하여 ReactFlow를 초기화할 수 있습니다",
                "example_code": {
                    "react": "const [nodes, setNodes] = useState(initialNodes); const [edges, setEdges] = useState(initialEdges);"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 예제 반환 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"예제 반환 실패: {str(e)}")

# ============================================================================
# 🔗 Connection 관련 API 엔드포인트
# ============================================================================

@canvas_router.post("/reactflow/{canvas_id}/connect", response_model=Dict[str, Any])
async def handle_connection(
    canvas_id: str,
    connection_request: ConnectionRequest,
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow onConnect 핸들러 - 새로운 연결 생성"""
    try:
        logger.info(f"🔗 ReactFlow 연결 생성: {canvas_id} - {connection_request.connection.source} → {connection_request.connection.target}")
        
        # 연결을 엣지로 변환하여 추가
        new_edge = await canvas_service.handle_connection(canvas_id, connection_request)
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "edge_id": new_edge.id,
            "connection": {
                "source": connection_request.connection.source,
                "target": connection_request.connection.target,
                "sourceHandle": connection_request.connection.sourceHandle,
                "targetHandle": connection_request.connection.targetHandle
            },
            "message": f"연결이 생성되었습니다: {connection_request.connection.source} → {connection_request.connection.target}"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 연결 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연결 생성 실패: {str(e)}")

@canvas_router.post("/reactflow/{canvas_id}/connection-events", response_model=Dict[str, Any])
async def handle_connection_events(
    canvas_id: str,
    events: List[ConnectionEvent],
    canvas_service: CanvasService = Depends(get_canvas_service)
):
    """ReactFlow 연결 이벤트 배치 처리"""
    try:
        logger.info(f"🔗📦 ReactFlow 연결 이벤트 배치 처리: {canvas_id} - {len(events)}개 이벤트")
        
        results = []
        for event in events:
            try:
                connection_request = ConnectionRequest(
                    canvas_id=canvas_id,
                    connection=event.params
                )
                new_edge = await canvas_service.handle_connection(canvas_id, connection_request)
                results.append({
                    "success": True,
                    "edge_id": new_edge.id,
                    "connection": event.params.dict()
                })
            except Exception as event_error:
                logger.error(f"❌ 개별 연결 이벤트 처리 실패: {str(event_error)}")
                results.append({
                    "success": False,
                    "error": str(event_error),
                    "connection": event.params.dict()
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "canvas_id": canvas_id,
            "total_events": len(events),
            "success_count": success_count,
            "failed_count": len(events) - success_count,
            "results": results,
            "message": f"{success_count}/{len(events)}개의 연결 이벤트가 처리되었습니다"
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow 연결 이벤트 배치 처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연결 이벤트 처리 실패: {str(e)}")

@canvas_router.get("/reactflow/examples/onconnect", response_model=Dict[str, Any])
async def get_onconnect_example():
    """ReactFlow onConnect 핸들러 사용 예제 반환"""
    try:
        logger.info("📝 ReactFlow onConnect 예제 반환")
        
        return {
            "success": True,
            "message": "ReactFlow onConnect 핸들러 예제",
            "example_code": {
                "import": "import { addEdge } from '@xyflow/react';",
                "handler": """const onConnect = useCallback(
  (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
  [],
);""",
                "usage": """<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  fitView
>
  <Background />
  <Controls />
</ReactFlow>""",
                "backend_sync": """// 백엔드와 동기화
const onConnect = useCallback(
  async (params) => {
    // 로컬 상태 업데이트
    setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot));
    
    // 백엔드 동기화
    try {
      await fetch(`/canvas/reactflow/${canvasId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          canvas_id: canvasId,
          connection: params,
          edge_options: { 
            animated: false, 
            style: { stroke: '#b1b1b7' } 
          }
        })
      });
    } catch (error) {
      console.error('연결 저장 실패:', error);
    }
  },
  [canvasId],
);"""
            },
            "api_endpoints": {
                "create_connection": "POST /canvas/reactflow/{canvas_id}/connect",
                "batch_events": "POST /canvas/reactflow/{canvas_id}/connection-events",
                "examples": "GET /canvas/reactflow/examples/onconnect"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ ReactFlow onConnect 예제 반환 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"onConnect 예제 반환 실패: {str(e)}")
