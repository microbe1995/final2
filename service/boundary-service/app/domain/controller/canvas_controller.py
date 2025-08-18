# ============================================================================
# 🖼️ Canvas Controller - Canvas HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from loguru import logger

from ..service.canvas_service import CanvasService
from ..schema.canvas_schema import (
    CanvasCreateRequest,
    CanvasUpdateRequest,
    CanvasResponse,
    CanvasListResponse,
    CanvasSearchRequest,
    CanvasStatsResponse,
    CanvasExportRequest,
    CanvasImportRequest,
    CanvasDuplicateRequest,
    CanvasTemplateRequest
)

# 라우터 생성
canvas_router = APIRouter(tags=["canvas"])

# 서비스 의존성
def get_canvas_service() -> CanvasService:
    """CanvasService 의존성 주입"""
    return CanvasService()

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
