# ============================================================================
# ➡️ Arrow Controller - 화살표 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from loguru import logger

from ..service.arrow_service import ArrowService
from ..schema.arrow_schema import (
    ArrowCreateRequest,
    ArrowUpdateRequest,
    ArrowResponse,
    ArrowListResponse,
    ArrowSearchRequest,
    ArrowStatsResponse,
    ArrowConnectionRequest,
    ArrowBatchCreateRequest
)

# 라우터 생성
arrow_router = APIRouter(tags=["arrows"])

# 서비스 의존성
def get_arrow_service() -> ArrowService:
    """ArrowService 의존성 주입"""
    return ArrowService()

# ============================================================================
# 🎯 CRUD 엔드포인트
# ============================================================================

@arrow_router.post("/", response_model=ArrowResponse, status_code=201)
async def create_arrow(
    request: ArrowCreateRequest,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """새 화살표를 생성합니다"""
    try:
        logger.info(f"➡️ 화살표 생성 요청: {request.type.value}")
        response = await arrow_service.create_arrow(request)
        logger.info(f"✅ 화살표 생성 완료: {response.id}")
        return response
    except Exception as e:
        logger.error(f"❌ 화살표 생성 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 생성 실패: {str(e)}")

@arrow_router.get("/{arrow_id}", response_model=ArrowResponse)
async def get_arrow(
    arrow_id: str,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """ID로 화살표를 조회합니다"""
    try:
        logger.info(f"🔍 화살표 조회 요청: {arrow_id}")
        response = await arrow_service.get_arrow(arrow_id)
        if not response:
            raise HTTPException(status_code=404, detail="화살표를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"화살표 조회 실패: {str(e)}")

@arrow_router.get("/", response_model=ArrowListResponse)
async def get_all_arrows(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """모든 화살표를 페이지네이션으로 조회합니다"""
    try:
        logger.info(f"📋 화살표 목록 조회 요청: 페이지 {page}, 크기 {size}")
        response = await arrow_service.get_all_arrows(page=page, size=size)
        return response
    except Exception as e:
        logger.error(f"❌ 화살표 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"화살표 목록 조회 실패: {str(e)}")

@arrow_router.put("/{arrow_id}", response_model=ArrowResponse)
async def update_arrow(
    arrow_id: str,
    request: ArrowUpdateRequest,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표를 수정합니다"""
    try:
        logger.info(f"✏️ 화살표 수정 요청: {arrow_id}")
        response = await arrow_service.update_arrow(arrow_id, request)
        if not response:
            raise HTTPException(status_code=404, detail="수정할 화살표를 찾을 수 없습니다")
        logger.info(f"✅ 화살표 수정 완료: {arrow_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 수정 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 수정 실패: {str(e)}")

@arrow_router.delete("/{arrow_id}", status_code=204)
async def delete_arrow(
    arrow_id: str,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표를 삭제합니다"""
    try:
        logger.info(f"🗑️ 화살표 삭제 요청: {arrow_id}")
        success = await arrow_service.delete_arrow(arrow_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 화살표를 찾을 수 없습니다")
        logger.info(f"✅ 화살표 삭제 완료: {arrow_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"화살표 삭제 실패: {str(e)}")

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@arrow_router.post("/search", response_model=ArrowListResponse)
async def search_arrows(
    request: ArrowSearchRequest,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """조건에 맞는 화살표를 검색합니다"""
    try:
        logger.info(f"🔍 화살표 검색 요청: {len(request.__dict__)}개 조건")
        response = await arrow_service.search_arrows(request)
        return response
    except Exception as e:
        logger.error(f"❌ 화살표 검색 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 검색 실패: {str(e)}")

# ============================================================================
# 🎨 화살표 조작 엔드포인트
# ============================================================================

@arrow_router.post("/{arrow_id}/move", response_model=ArrowResponse)
async def move_arrow(
    arrow_id: str,
    dx: float = Query(..., description="X축 이동 거리"),
    dy: float = Query(..., description="Y축 이동 거리"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표를 이동시킵니다"""
    try:
        logger.info(f"🚀 화살표 이동 요청: {arrow_id} (dx: {dx}, dy: {dy})")
        response = await arrow_service.move_arrow(arrow_id, dx, dy)
        if not response:
            raise HTTPException(status_code=404, detail="이동할 화살표를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 이동 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 이동 실패: {str(e)}")

@arrow_router.post("/{arrow_id}/resize", response_model=ArrowResponse)
async def resize_arrow(
    arrow_id: str,
    new_start_x: float = Query(..., description="새 시작점 X 좌표"),
    new_start_y: float = Query(..., description="새 시작점 Y 좌표"),
    new_end_x: float = Query(..., description="새 끝점 X 좌표"),
    new_end_y: float = Query(..., description="새 끝점 Y 좌표"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표의 크기와 위치를 변경합니다"""
    try:
        logger.info(f"📏 화살표 크기 변경 요청: {arrow_id}")
        response = await arrow_service.resize_arrow(
            arrow_id, new_start_x, new_start_y, new_end_x, new_end_y
        )
        if not response:
            raise HTTPException(status_code=404, detail="크기 변경할 화살표를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 크기 변경 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 크기 변경 실패: {str(e)}")

@arrow_router.post("/{arrow_id}/color", response_model=ArrowResponse)
async def change_arrow_color(
    arrow_id: str,
    new_color: str = Query(..., description="새 색상 (#RGB, #RRGGBB, #RRGGBBAA)"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표의 색상을 변경합니다"""
    try:
        logger.info(f"🎨 화살표 색상 변경 요청: {arrow_id} ({new_color})")
        response = await arrow_service.change_arrow_color(arrow_id, new_color)
        if not response:
            raise HTTPException(status_code=404, detail="색상 변경할 화살표를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 색상 변경 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 색상 변경 실패: {str(e)}")

@arrow_router.post("/{arrow_id}/dash-pattern", response_model=ArrowResponse)
async def set_arrow_dash_pattern(
    arrow_id: str,
    pattern: str = Query(..., description="점선 패턴 (예: '5,5' 또는 '10,5,5,5')"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표의 점선 패턴을 설정합니다"""
    try:
        # 문자열을 float 리스트로 변환
        dash_pattern = [float(x.strip()) for x in pattern.split(',')]
        logger.info(f"🔄 화살표 점선 패턴 설정 요청: {arrow_id} ({dash_pattern})")
        response = await arrow_service.set_arrow_dash_pattern(arrow_id, dash_pattern)
        if not response:
            raise HTTPException(status_code=404, detail="점선 패턴을 설정할 화살표를 찾을 수 없습니다")
        return response
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 점선 패턴 형식입니다")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 화살표 점선 패턴 설정 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 점선 패턴 설정 실패: {str(e)}")

@arrow_router.post("/{arrow_id}/control-point", response_model=ArrowResponse)
async def add_control_point(
    arrow_id: str,
    x: float = Query(..., description="제어점 X 좌표"),
    y: float = Query(..., description="제어점 Y 좌표"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """곡선 화살표에 제어점을 추가합니다"""
    try:
        logger.info(f"📍 제어점 추가 요청: {arrow_id} ({x}, {y})")
        response = await arrow_service.add_control_point(arrow_id, x, y)
        if not response:
            raise HTTPException(status_code=404, detail="제어점을 추가할 화살표를 찾을 수 없습니다")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제어점 추가 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"제어점 추가 실패: {str(e)}")

# ============================================================================
# 🎯 특수 기능 엔드포인트
# ============================================================================

@arrow_router.post("/connect", response_model=ArrowResponse)
async def connect_shapes(
    request: ArrowConnectionRequest,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """두 도형을 화살표로 연결합니다"""
    try:
        logger.info(f"🔗 도형 연결 요청: {request.from_shape_id} → {request.to_shape_id}")
        response = await arrow_service.connect_shapes(request)
        return response
    except Exception as e:
        logger.error(f"❌ 도형 연결 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"도형 연결 실패: {str(e)}")

@arrow_router.post("/batch", response_model=list[ArrowResponse])
async def create_batch_arrows(
    request: ArrowBatchCreateRequest,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """여러 화살표를 일괄 생성합니다"""
    try:
        logger.info(f"📦 화살표 일괄 생성 요청: {len(request.arrows)}개")
        response = await arrow_service.create_batch_arrows(request)
        return response
    except Exception as e:
        logger.error(f"❌ 화살표 일괄 생성 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=f"화살표 일괄 생성 실패: {str(e)}")

# ============================================================================
# 📊 통계 및 분석 엔드포인트
# ============================================================================

@arrow_router.get("/stats/overview", response_model=ArrowStatsResponse)
async def get_arrow_stats(
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """화살표 통계를 조회합니다"""
    try:
        logger.info("📊 화살표 통계 조회 요청")
        response = await arrow_service.get_arrow_stats()
        return response
    except Exception as e:
        logger.error(f"❌ 화살표 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"화살표 통계 조회 실패: {str(e)}")

# ============================================================================
# 🔧 유틸리티 엔드포인트
# ============================================================================

@arrow_router.get("/canvas/{canvas_id}", response_model=list[ArrowResponse])
async def get_arrows_by_canvas(
    canvas_id: str,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """특정 Canvas에 속한 화살표들을 조회합니다"""
    try:
        logger.info(f"🖼️ Canvas 화살표 조회 요청: {canvas_id}")
        response = await arrow_service.get_arrows_by_canvas(canvas_id)
        return response
    except Exception as e:
        logger.error(f"❌ Canvas 화살표 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 화살표 조회 실패: {str(e)}")

@arrow_router.delete("/canvas/{canvas_id}/clear", status_code=204)
async def clear_canvas_arrows(
    canvas_id: str,
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """특정 Canvas의 모든 화살표를 제거합니다"""
    try:
        logger.info(f"🧹 Canvas 화살표 제거 요청: {canvas_id}")
        removed_count = await arrow_service.clear_canvas_arrows(canvas_id)
        logger.info(f"✅ Canvas 화살표 제거 완료: {canvas_id} ({removed_count}개)")
        return None
    except Exception as e:
        logger.error(f"❌ Canvas 화살표 제거 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Canvas 화살표 제거 실패: {str(e)}")

@arrow_router.get("/at-point", response_model=list[ArrowResponse])
async def get_arrows_at_point(
    x: float = Query(..., description="X 좌표"),
    y: float = Query(..., description="Y 좌표"),
    threshold: float = Query(5.0, gt=0, description="검색 반경"),
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """주어진 점 근처의 화살표들을 찾습니다"""
    try:
        logger.info(f"📍 점 근처 화살표 조회 요청: ({x}, {y}), 반경 {threshold}")
        response = await arrow_service.get_arrows_at_point(x, y, threshold)
        return response
    except Exception as e:
        logger.error(f"❌ 점 근처 화살표 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"점 근처 화살표 조회 실패: {str(e)}")

# ============================================================================
# 🧪 테스트 및 개발용 엔드포인트
# ============================================================================

@arrow_router.get("/health/check")
async def health_check():
    """화살표 서비스 상태 확인"""
    return {"status": "healthy", "service": "arrow", "message": "화살표 서비스가 정상 작동 중입니다"}

@arrow_router.get("/debug/info")
async def debug_info(
    arrow_service: ArrowService = Depends(get_arrow_service)
):
    """디버그 정보 조회 (개발용)"""
    try:
        # 간단한 통계 정보 반환
        stats = await arrow_service.get_arrow_stats()
        return {
            "service": "arrow",
            "total_arrows": stats.total_arrows,
            "arrows_by_type": stats.arrows_by_type,
            "average_length": stats.average_length,
            "dashed_count": stats.dashed_count,
            "canvas_count": stats.canvas_count
        }
    except Exception as e:
        logger.error(f"❌ 디버그 정보 조회 실패: {str(e)}")
        return {"service": "arrow", "error": str(e)}
