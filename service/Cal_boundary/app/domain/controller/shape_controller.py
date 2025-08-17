# ============================================================================
# 🎨 Shape Controller - 도형 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from loguru import logger

from ..service.shape_service import ShapeService
from ..schema.shape_schema import (
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse,
    ShapeSearchRequest,
    ShapeStatsResponse
)

# 라우터 생성
shape_router = APIRouter(prefix="/shapes", tags=["shapes"])

# 서비스 의존성
def get_shape_service() -> ShapeService:
    """ShapeService 의존성 주입"""
    return ShapeService()

# ============================================================================
# 🎯 CRUD 엔드포인트
# ============================================================================

@shape_router.post("/", response_model=ShapeResponse, status_code=201)
async def create_shape(
    request: ShapeCreateRequest,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """새 도형을 생성합니다"""
    try:
        logger.info(f"🎨 도형 생성 요청: {request.type.value}")
        response = await shape_service.create_shape(request)
        logger.info(f"✅ 도형 생성 완료: {response.id}")
        return response
    except Exception as e:
        logger.error(f"❌ 도형 생성 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 생성 실패: {str(e)}")

@shape_router.get("/{shape_id}", response_model=ShapeResponse)
async def get_shape(
    shape_id: str,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """ID로 도형을 조회합니다"""
    try:
        logger.info(f"🔍 도형 조회 요청: {shape_id}")
        response = await shape_service.get_shape(shape_id)
        if not response:
            raise HTTPException(status_code=404, detail="도형을 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"도형 조회 실패: {str(e)}")

@shape_router.get("/", response_model=ShapeListResponse)
async def get_all_shapes(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    shape_service: ShapeService = Depends(get_shape_service)
):
    """모든 도형을 페이지네이션으로 조회합니다"""
    try:
        logger.info(f"📋 도형 목록 조회 요청: 페이지 {page}, 크기 {size}")
        response = await shape_service.get_all_shapes(page=page, size=size)
        return response
    except Exception as e:
        logger.error(f"❌ 도형 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"도형 목록 조회 실패: {str(e)}")

@shape_router.put("/{shape_id}", response_model=ShapeResponse)
async def update_shape(
    shape_id: str,
    request: ShapeUpdateRequest,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형을 수정합니다"""
    try:
        logger.info(f"✏️ 도형 수정 요청: {shape_id}")
        response = await shape_service.update_shape(shape_id, request)
        if not response:
            raise HTTPException(status_code=404, detail="수정할 도형을 찾을 수 없습니다")
        logger.info(f"✅ 도형 수정 완료: {shape_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 수정 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 수정 실패: {str(e)}")

@shape_router.delete("/{shape_id}", status_code=204)
async def delete_shape(
    shape_id: str,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형을 삭제합니다"""
    try:
        logger.info(f"🗑️ 도형 삭제 요청: {shape_id}")
        success = await shape_service.delete_shape(shape_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 도형을 찾을 수 없습니다")
        logger.info(f"✅ 도형 삭제 완료: {shape_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"도형 삭제 실패: {str(e)}")

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@shape_router.post("/search", response_model=ShapeListResponse)
async def search_shapes(
    request: ShapeSearchRequest,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """조건에 맞는 도형을 검색합니다"""
    try:
        logger.info(f"🔍 도형 검색 요청: {len(request.__dict__)}개 조건")
        response = await shape_service.search_shapes(request)
        return response
    except Exception as e:
        logger.error(f"❌ 도형 검색 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 검색 실패: {str(e)}")

# ============================================================================
# 🎨 도형 조작 엔드포인트
# ============================================================================

@shape_router.post("/{shape_id}/move", response_model=ShapeResponse)
async def move_shape(
    shape_id: str,
    dx: float = Query(..., description="X축 이동 거리"),
    dy: float = Query(..., description="Y축 이동 거리"),
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형을 이동시킵니다"""
    try:
        logger.info(f"🚀 도형 이동 요청: {shape_id} (dx: {dx}, dy: {dy})")
        response = await shape_service.move_shape(shape_id, dx, dy)
        if not response:
            raise HTTPException(status_code=404, detail="이동할 도형을 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 이동 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 이동 실패: {str(e)}")

@shape_router.post("/{shape_id}/resize", response_model=ShapeResponse)
async def resize_shape(
    shape_id: str,
    new_width: float = Query(..., gt=0, description="새 너비"),
    new_height: float = Query(..., gt=0, description="새 높이"),
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형의 크기를 변경합니다"""
    try:
        logger.info(f"📏 도형 크기 변경 요청: {shape_id} ({new_width}x{new_height})")
        response = await shape_service.resize_shape(shape_id, new_width, new_height)
        if not response:
            raise HTTPException(status_code=404, detail="크기 변경할 도형을 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 크기 변경 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 크기 변경 실패: {str(e)}")

@shape_router.post("/{shape_id}/rotate", response_model=ShapeResponse)
async def rotate_shape(
    shape_id: str,
    angle: float = Query(..., description="회전 각도 (도)"),
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형을 회전시킵니다"""
    try:
        logger.info(f"🔄 도형 회전 요청: {shape_id} ({angle}도)")
        response = await shape_service.rotate_shape(shape_id, angle)
        if not response:
            raise HTTPException(status_code=404, detail="회전할 도형을 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 회전 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 회전 실패: {str(e)}")

@shape_router.post("/{shape_id}/color", response_model=ShapeResponse)
async def change_shape_color(
    shape_id: str,
    new_color: str = Query(..., description="새 색상 (#RGB, #RRGGBB, #RRGGBBAA)"),
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형의 색상을 변경합니다"""
    try:
        logger.info(f"🎨 도형 색상 변경 요청: {shape_id} ({new_color})")
        response = await shape_service.change_shape_color(shape_id, new_color)
        if not response:
            raise HTTPException(status_code=404, detail="색상 변경할 도형을 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 도형 색상 변경 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 색상 변경 실패: {str(e)}")

# ============================================================================
# 📊 통계 및 분석 엔드포인트
# ============================================================================

@shape_router.get("/stats/overview", response_model=ShapeStatsResponse)
async def get_shape_stats(
    shape_service: ShapeService = Depends(get_shape_service)
):
    """도형 통계를 조회합니다"""
    try:
        logger.info("📊 도형 통계 조회 요청")
        response = await shape_service.get_shape_stats()
        return response
    except Exception as e:
        logger.error(f"❌ 도형 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"도형 통계 조회 실패: {str(e)}")

# ============================================================================
# 🔧 유틸리티 엔드포인트
# ============================================================================

@shape_router.get("/canvas/{canvas_id}", response_model=list[ShapeResponse])
async def get_shapes_by_canvas(
    canvas_id: str,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """특정 Canvas에 속한 도형들을 조회합니다"""
    try:
        logger.info(f"🖼️ Canvas 도형 조회 요청: {canvas_id}")
        response = await shape_service.get_shapes_by_canvas(canvas_id)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 도형 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 도형 조회 실패: {str(e)}")

@shape_router.delete("/canvas/{canvas_id}/clear", status_code=204)
async def clear_canvas_shapes(
    canvas_id: str,
    shape_service: ShapeService = Depends(get_shape_service)
):
    """특정 Canvas의 모든 도형을 제거합니다"""
    try:
        logger.info(f"🧹 Canvas 도형 제거 요청: {canvas_id}")
        removed_count = await shape_service.clear_canvas_shapes(canvas_id)
        logger.info(f"✅ Canvas 도형 제거 완료: {canvas_id} ({removed_count}개)")
        return None
    except Exception as e:
        logger.error(f"❌ Canvas 도형 제거 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 도형 제거 실패: {str(e)}")

# ============================================================================
# 🧪 테스트 및 개발용 엔드포인트
# ============================================================================

@shape_router.get("/health/check")
async def health_check():
    """도형 서비스 상태 확인"""
    return {"status": "healthy", "service": "shape", "message": "도형 서비스가 정상 작동 중입니다"}

@shape_router.get("/debug/info")
async def debug_info(
    shape_service: ShapeService = Depends(get_shape_service)
):
    """디버그 정보 조회 (개발용)"""
    try:
        # 간단한 통계 정보 반환
        stats = await shape_service.get_shape_stats()
        return {
            "service": "shape",
            "total_shapes": stats.total_shapes,
            "shapes_by_type": stats.shapes_by_type,
            "canvas_count": stats.canvas_count
        }
    except Exception as e:
        logger.error(f"❌ 디버그 정보 조회 실패: {str(e)}")
        return {"service": "shape", "error": str(e)}
