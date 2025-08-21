# ============================================================================
# 🧮 Calculation Controller - CBAM 계산 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List, Dict, Any
from loguru import logger
from datetime import datetime

from .calculation_service import CalculationService
from .calculation_repository import CalculationRepository
from .calculation_schema import (
    FuelCalculationRequest,
    FuelCalculationResponse,
    MaterialCalculationRequest,
    MaterialCalculationResponse,
    PrecursorListRequest,
    PrecursorListResponse,
    PrecursorSaveResponse,
    CBAmCalculationRequest,
    CBAMCalculationResponse,
    CalculationStatsResponse
)

# 라우터 생성
calculation_router = APIRouter(tags=["calculation"])

# 서비스 의존성
def get_calculation_repository() -> CalculationRepository:
    return CalculationRepository(use_database=False)  # 메모리 사용

def get_calculation_service() -> CalculationService:
    repository = get_calculation_repository()
    return CalculationService(repository=repository)

# ============================================================================
# 🔥 연료 계산 API
# ============================================================================

@calculation_router.post("/calc/fuel/calculate", response_model=FuelCalculationResponse)
async def calculate_fuel_emission(
    request: FuelCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    🔥 **연료 배출량 계산**
    
    연료의 배출량을 계산합니다.
    
    - **fuel_name**: 연료명 (필수)
    - **fuel_amount**: 연료량 (톤, 필수)
    
    **계산 공식**: 연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3
    """
    try:
        logger.info(f"🔥 연료 배출량 계산 API 호출: {request.fuel_name} ({request.fuel_amount}톤)")
        
        result = await calc_service.calculate_fuel_emission(request)
        
        logger.info(f"✅ 연료 배출량 계산 API 성공: {result.emission} tCO2")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 연료 배출량 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 연료 배출량 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="연료 배출량 계산 중 오류가 발생했습니다")

@calculation_router.get("/calc/fuel/list")
async def get_fuel_list(
    search: str = Query("", description="검색어"),
    limit: int = Query(50, ge=1, le=100, description="결과 제한"),
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """🔍 **연료 목록 조회** - 사용 가능한 연료 목록을 조회합니다."""
    try:
        logger.info(f"🔍 연료 목록 조회 API 호출: '{search}'")
        
        fuels = await calc_service.search_fuels(search, limit)
        
        logger.info(f"✅ 연료 목록 조회 API 성공: {len(fuels)}개")
        return {"fuels": fuels, "total": len(fuels)}
        
    except Exception as e:
        logger.error(f"❌ 연료 목록 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="연료 목록 조회 중 오류가 발생했습니다")

# ============================================================================
# 🧱 원료 계산 API
# ============================================================================

@calculation_router.post("/calc/material/calculate", response_model=MaterialCalculationResponse)
async def calculate_material_emission(
    request: MaterialCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    🧱 **원료 배출량 계산**
    
    원료의 배출량을 계산합니다.
    
    - **material_name**: 원료명 (필수)
    - **material_amount**: 원료량 (톤, 필수)
    
    **계산 공식**: 원료량(톤) × 직접배출계수
    """
    try:
        logger.info(f"🧱 원료 배출량 계산 API 호출: {request.material_name} ({request.material_amount}톤)")
        
        result = await calc_service.calculate_material_emission(request)
        
        logger.info(f"✅ 원료 배출량 계산 API 성공: {result.emission} tCO2")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 원료 배출량 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 원료 배출량 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="원료 배출량 계산 중 오류가 발생했습니다")

@calculation_router.get("/calc/material/list")
async def get_material_list(
    search: str = Query("", description="검색어"),
    limit: int = Query(50, ge=1, le=100, description="결과 제한"),
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """🔍 **원료 목록 조회** - 사용 가능한 원료 목록을 조회합니다."""
    try:
        logger.info(f"🔍 원료 목록 조회 API 호출: '{search}'")
        
        materials = await calc_service.search_materials(search, limit)
        
        logger.info(f"✅ 원료 목록 조회 API 성공: {len(materials)}개")
        return {"materials": materials, "total": len(materials)}
        
    except Exception as e:
        logger.error(f"❌ 원료 목록 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="원료 목록 조회 중 오류가 발생했습니다")

# ============================================================================
# 🔗 전구물질 관리 API
# ============================================================================

@calculation_router.get("/calc/precursor/user/{user_id}", response_model=PrecursorListResponse)
async def get_user_precursors(
    user_id: str,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """📋 **사용자 전구물질 목록 조회** - 특정 사용자의 전구물질 목록을 조회합니다."""
    try:
        logger.info(f"📋 사용자 전구물질 목록 조회 API 호출: {user_id}")
        
        result = await calc_service.get_user_precursors(user_id)
        
        logger.info(f"✅ 사용자 전구물질 목록 조회 API 성공: {len(result.precursors)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 사용자 전구물질 목록 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="사용자 전구물질 목록 조회 중 오류가 발생했습니다")

@calculation_router.post("/calc/precursor/save-batch", response_model=PrecursorSaveResponse)
async def save_precursors_batch(
    request: PrecursorListRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """📊 **전구물질 일괄 저장** - 여러 전구물질을 한 번에 저장합니다."""
    try:
        logger.info(f"📊 전구물질 일괄 저장 API 호출: {len(request.precursors)}개")
        
        result = await calc_service.save_precursors_batch(request)
        
        logger.info(f"✅ 전구물질 일괄 저장 API 성공: {result.inserted_count}개")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 전구물질 일괄 저장 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 전구물질 일괄 저장 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전구물질 일괄 저장 중 오류가 발생했습니다")

@calculation_router.delete("/calc/precursor/{precursor_id}")
async def delete_precursor(
    precursor_id: int,
    user_id: str = Query(..., description="사용자 ID"),
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """🗑️ **전구물질 삭제** - 기존 전구물질을 삭제합니다."""
    try:
        logger.info(f"🗑️ 전구물질 삭제 API 호출: {precursor_id}")
        
        deleted = await calc_service.delete_precursor(precursor_id, user_id)
        
        if not deleted:
            logger.warning(f"⚠️ 삭제할 전구물질을 찾을 수 없음: {precursor_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="삭제할 전구물질을 찾을 수 없습니다")
        
        logger.info(f"✅ 전구물질 삭제 API 성공: {precursor_id}")
        return {"message": "전구물질이 성공적으로 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 전구물질 삭제 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전구물질 삭제 중 오류가 발생했습니다")

# ============================================================================
# 🎯 CBAM 종합 계산 API
# ============================================================================

@calculation_router.post("/calc/cbam", response_model=CBAMCalculationResponse)
async def calculate_cbam_total(
    request: CBAmCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    🎯 **CBAM 종합 배출량 계산**
    
    제품의 전체 CBAM 배출량을 계산합니다.
    
    - **연료 배출량**: 연료 사용량 기반 계산
    - **원료 배출량**: 원료 사용량 기반 계산
    - **전력 배출량**: 전력 사용량 및 배출계수 기반 계산
    - **전구물질 배출량**: 복합제품의 경우 전구물질 기반 계산
    
    **총 배출량 = 직접배출량 + 간접배출량 + 전구물질배출량**
    """
    try:
        logger.info(f"🎯 CBAM 종합 계산 API 호출: {request.product_name}")
        
        result = await calc_service.calculate_cbam_total(request)
        
        logger.info(f"✅ CBAM 종합 계산 API 성공: {result.total_emission} tCO2")
        return result
        
    except ValueError as e:
        logger.error(f"❌ CBAM 종합 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ CBAM 종합 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CBAM 종합 계산 중 오류가 발생했습니다")

# ============================================================================
# 📊 통계 및 관리 API
# ============================================================================

@calculation_router.get("/calc/stats", response_model=CalculationStatsResponse)
async def get_calculation_stats(calc_service: CalculationService = Depends(get_calculation_service)):
    """📊 **계산 통계 조회** - 계산 관련 통계 정보를 조회합니다."""
    try:
        logger.info(f"📊 계산 통계 조회 API 호출")
        
        result = await calc_service.get_calculation_stats()
        
        logger.info(f"✅ 계산 통계 조회 API 성공")
        return result
        
    except Exception as e:
        logger.error(f"❌ 계산 통계 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="계산 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 헬스체크 API
# ============================================================================

@calculation_router.get("/health")
async def calculation_health_check():
    """계산 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "CBAM Calculation Domain",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# 📝 예제 API
# ============================================================================

@calculation_router.get("/calc/examples/fuel")
async def get_fuel_calculation_example():
    """연료 계산 예제"""
    return {
        "example_request": {
            "fuel_name": "천연가스",
            "fuel_amount": 10.5
        },
        "example_response": {
            "emission": 28.728,
            "fuel_name": "천연가스",
            "emission_factor": 56.1,
            "net_calorific_value": 48.0,
            "calculation_formula": "연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3"
        },
        "usage": "이 예제를 참고하여 연료 배출량을 계산하세요"
    }

@calculation_router.get("/calc/examples/material")
async def get_material_calculation_example():
    """원료 계산 예제"""
    return {
        "example_request": {
            "material_name": "철광석",
            "material_amount": 100.0
        },
        "example_response": {
            "emission": 2.4,
            "material_name": "철광석",
            "direct_factor": 0.024,
            "calculation_formula": "원료량(톤) × 직접배출계수"
        },
        "usage": "이 예제를 참고하여 원료 배출량을 계산하세요"
    }