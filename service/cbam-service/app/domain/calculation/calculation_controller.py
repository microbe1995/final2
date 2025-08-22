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
    PrecursorCalculationRequest,
    PrecursorCalculationResponse,
    PrecursorListRequest,
    PrecursorListResponse,
    PrecursorSaveResponse,
    ElectricityCalculationRequest,
    ElectricityCalculationResponse,
    ProductionProcess,
    CBAmCalculationRequest,
    CBAMCalculationResponse,
    CalculationStatsResponse,
    BoundaryCreateRequest,
    BoundaryResponse,
    ProductCreateRequest,
    ProductResponse,
    OperationCreateRequest,
    OperationResponse,
    NodeCreateRequest,
    NodeResponse,
    EdgeCreateRequest,
    EdgeResponse,
    ProductionEmissionCreateRequest,
    ProductionEmissionResponse
)

# 라우터 생성
calculation_router = APIRouter(tags=["calculation"])

# 서비스 의존성
def get_calculation_repository() -> CalculationRepository:
    return CalculationRepository(use_database=False)  # 메모리 사용

def get_calculation_service() -> CalculationService:
    repository = get_calculation_repository()
    return CalculationService(repository=repository)

# 전역 서비스 인스턴스 (새로운 테이블 API용)
calculation_service = CalculationService(repository=CalculationRepository(use_database=False))

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
# 🔗 전구물질 계산 및 관리 API
# ============================================================================

@calculation_router.post("/calc/precursor/calculate", response_model=PrecursorCalculationResponse)
async def calculate_precursor_emission(
    request: PrecursorCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    🔬 **전구물질 배출량 계산**
    
    전구물질의 배출량을 계산합니다.
    
    - **precursor_name**: 전구물질명 (필수)
    - **precursor_amount**: 전구물질 사용량 (톤, 필수)
    - **direct**: 직접 배출계수 (tCO2/톤, 필수)
    - **indirect**: 간접 배출계수 (tCO2/톤, 선택)
    
    **계산 공식**: 전구물질량(톤) × (직접배출계수 + 간접배출계수)
    """
    try:
        logger.info(f"🔬 전구물질 배출량 계산 API 호출: {request.precursor_name} ({request.precursor_amount}톤)")
        
        result = await calc_service.calculate_precursor_emission(request)
        
        logger.info(f"✅ 전구물질 배출량 계산 API 성공: {result.emission} tCO2")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 전구물질 배출량 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 전구물질 배출량 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전구물질 배출량 계산 중 오류가 발생했습니다")

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
# ⚡ 전력 사용 배출량 계산 API
# ============================================================================

@calculation_router.post("/calc/electricity/calculate", response_model=ElectricityCalculationResponse)
async def calculate_electricity_emission(
    request: ElectricityCalculationRequest,
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    ⚡ **전력 사용 배출량 계산**
    
    전력 사용량에 따른 배출량을 계산합니다.
    
    - **power_usage**: 전력 사용량 (MWh, 필수)
    - **emission_factor**: 전력 배출계수 (tCO2/MWh, 기본값: 0.4567)
    
    **계산 공식**: 전력사용량(MWh) × 배출계수(tCO2/MWh)
    
    **참고**: 전력배출계수는 2014~2016 연평균 기본값을 사용함 (0.4567 tCO2/MWh)
    """
    try:
        logger.info(f"⚡ 전력 사용 배출량 계산 API 호출: {request.power_usage} MWh")
        
        result = await calc_service.calculate_electricity_emission(request)
        
        logger.info(f"✅ 전력 사용 배출량 계산 API 성공: {result.emission} tCO2")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 전력 사용 배출량 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 전력 사용 배출량 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전력 사용 배출량 계산 중 오류가 발생했습니다")

# ============================================================================
# 🏭 생산 공정 관리 API
# ============================================================================

@calculation_router.post("/calc/process/calculate")
async def calculate_process_emissions(
    processes: List[ProductionProcess],
    calc_service: CalculationService = Depends(get_calculation_service)
):
    """
    🏭 **생산 공정별 배출량 계산**
    
    여러 생산 공정의 배출량을 계산합니다.
    
    각 공정별로:
    - 직접 배출량 (연료, 원료)
    - 간접 배출량 (전력)
    - 전구물질 배출량 (복합제품의 경우)
    """
    try:
        logger.info(f"🏭 생산 공정별 배출량 계산 API 호출: {len(processes)}개 공정")
        
        result = await calc_service.calculate_process_emissions(processes)
        
        logger.info(f"✅ 생산 공정별 배출량 계산 API 성공")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 생산 공정별 배출량 계산 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 생산 공정별 배출량 계산 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="생산 공정별 배출량 계산 중 오류가 발생했습니다")

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
            "fuel_emfactor": 56.1,
            "net_calory": 48.0,
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
            "material_amount": 1000.0
        },
        "example_response": {
            "emission": 24.0,
            "material_name": "철광석",
            "em_factor": 0.024,
            "calculation_formula": "원료량(톤) × 직접배출계수"
        },
        "usage": "이 예제를 참고하여 원료 배출량을 계산하세요"
    }

# ============================================================================
# 🗄️ 새로운 테이블 API 엔드포인트들
# ============================================================================

@calculation_router.post("/boundary", response_model=BoundaryResponse, tags=["Boundary"])
async def create_boundary(request: BoundaryCreateRequest):
    """경계 생성"""
    try:
        result = await calculation_service.create_boundary(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/boundary", response_model=List[BoundaryResponse], tags=["Boundary"])
async def get_boundaries():
    """경계 목록 조회"""
    try:
        result = await calculation_service.get_boundaries()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.post("/product", response_model=ProductResponse, tags=["Product"])
async def create_product(request: ProductCreateRequest):
    """제품 생성"""
    try:
        result = await calculation_service.create_product(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/product", response_model=List[ProductResponse], tags=["Product"])
async def get_products():
    """제품 목록 조회"""
    try:
        result = await calculation_service.get_products()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.post("/operation", response_model=OperationResponse, tags=["Operation"])
async def create_operation(request: OperationCreateRequest):
    """공정 생성"""
    try:
        result = await calculation_service.create_operation(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/operation", response_model=List[OperationResponse], tags=["Operation"])
async def get_operations():
    """공정 목록 조회"""
    try:
        result = await calculation_service.get_operations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.post("/node", response_model=NodeResponse, tags=["Node"])
async def create_node(request: NodeCreateRequest):
    """노드 생성"""
    try:
        result = await calculation_service.create_node(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/node", response_model=List[NodeResponse], tags=["Node"])
async def get_nodes():
    """노드 목록 조회"""
    try:
        result = await calculation_service.get_nodes()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.post("/edge", response_model=EdgeResponse, tags=["Edge"])
async def create_edge(request: EdgeCreateRequest):
    """엣지 생성"""
    try:
        result = await calculation_service.create_edge(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/edge", response_model=List[EdgeResponse], tags=["Edge"])
async def get_edges():
    """엣지 목록 조회"""
    try:
        result = await calculation_service.get_edges()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.post("/production-emission", response_model=ProductionEmissionResponse, tags=["Production Emission"])
async def create_production_emission(request: ProductionEmissionCreateRequest):
    """생산 배출량 생성"""
    try:
        result = await calculation_service.create_production_emission(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@calculation_router.get("/production-emission", response_model=List[ProductionEmissionResponse], tags=["Production Emission"])
async def get_production_emissions():
    """생산 배출량 목록 조회"""
    try:
        result = await calculation_service.get_production_emissions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))