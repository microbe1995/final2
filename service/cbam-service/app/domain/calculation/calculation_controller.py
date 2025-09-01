# ============================================================================
# 🏭 Calculation Controller - 계산 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List
import time

from app.domain.calculation.calculation_service import CalculationService
from app.domain.calculation.calculation_schema import (
    ProcessAttrdirEmissionCreateRequest, ProcessAttrdirEmissionResponse, ProcessAttrdirEmissionUpdateRequest,
    ProcessEmissionCalculationRequest, ProcessEmissionCalculationResponse,
    ProductEmissionCalculationRequest, ProductEmissionCalculationResponse,
    EmissionPropagationRequest, EmissionPropagationResponse,
    GraphRecalculationRequest, GraphRecalculationResponse
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Calculation"])

# 서비스 인스턴스 생성
calculation_service = CalculationService()

# ============================================================================
# 📊 배출량 계산 관련 엔드포인트
# ============================================================================

@router.post("/emission/process/calculate", response_model=ProcessEmissionCalculationResponse)
async def calculate_process_emission(request: ProcessEmissionCalculationRequest):
    """공정별 배출량 계산"""
    try:
        logger.info(f"🧮 공정별 배출량 계산 요청: 공정 ID {request.process_id}")
        result = await calculation_service.calculate_process_emission(request)
        logger.info(f"✅ 공정별 배출량 계산 성공: 공정 ID {request.process_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 공정별 배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.post("/emission/product/calculate", response_model=ProductEmissionCalculationResponse)
async def calculate_product_emission(request: ProductEmissionCalculationRequest):
    """제품별 배출량 계산"""
    try:
        logger.info(f"🧮 제품별 배출량 계산 요청: 제품 ID {request.product_id}")
        result = await calculation_service.calculate_product_emission(request)
        logger.info(f"✅ 제품별 배출량 계산 성공: 제품 ID {request.product_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품별 배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품별 배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.get("/emission/process/{process_id}/attrdir", response_model=ProcessAttrdirEmissionResponse)
async def get_process_attrdir_emission(process_id: int):
    """공정별 직접귀속배출량 조회"""
    try:
        logger.info(f"📊 공정별 직접귀속배출량 조회 요청: 공정 ID {process_id}")
        result = await calculation_service.get_process_attrdir_emission(process_id)
        if not result:
            raise HTTPException(status_code=404, detail="공정별 직접귀속배출량을 찾을 수 없습니다")
        logger.info(f"✅ 공정별 직접귀속배출량 조회 성공: 공정 ID {process_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 공정별 직접귀속배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 직접귀속배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/emission/process/attrdir/all", response_model=List[ProcessAttrdirEmissionResponse])
async def get_all_process_attrdir_emissions():
    """모든 공정별 직접귀속배출량 조회"""
    try:
        logger.info("📊 모든 공정별 직접귀속배출량 조회 요청")
        results = await calculation_service.get_all_process_attrdir_emissions()
        logger.info(f"✅ 모든 공정별 직접귀속배출량 조회 성공: {len(results)}개")
        return results
    except Exception as e:
        logger.error(f"❌ 모든 공정별 직접귀속배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"모든 공정별 직접귀속배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/emission/process/{process_id}/attrdir", response_model=ProcessAttrdirEmissionResponse)
async def create_process_attrdir_emission(process_id: int):
    """공정별 직접귀속배출량 계산 및 저장"""
    try:
        logger.info(f"📊 공정별 직접귀속배출량 계산 요청: 공정 ID {process_id}")
        result = await calculation_service.calculate_process_attrdir_emission(process_id)
        logger.info(f"✅ 공정별 직접귀속배출량 계산 성공: 공정 ID {process_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 공정별 직접귀속배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 직접귀속배출량 계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔄 공정 간 값 전파 관련 엔드포인트 (1단계 핵심 기능)
# ============================================================================

@router.post("/emission/propagate", response_model=EmissionPropagationResponse)
async def propagate_emissions(request: EmissionPropagationRequest):
    """공정 간 배출량 전파 계산 (핵심 API)"""
    try:
        logger.info(f"🔄 배출량 전파 요청: {request.source_process_id} → {request.target_process_id} ({request.edge_kind})")
        result = await calculation_service.propagate_emissions(request)
        logger.info(f"✅ 배출량 전파 성공: {result.propagated_amount} tCO2e 전파됨")
        return result
    except Exception as e:
        logger.error(f"❌ 배출량 전파 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"배출량 전파 중 오류가 발생했습니다: {str(e)}")

@router.post("/emission/graph/recalculate", response_model=GraphRecalculationResponse)
async def recalculate_entire_graph(request: GraphRecalculationRequest):
    """전체 그래프 재계산 (엣지 변경 시 호출)"""
    try:
        logger.info(f"🚀 전체 그래프 재계산 요청: trigger_edge_id={request.trigger_edge_id}")
        result = await calculation_service.recalculate_entire_graph(request)
        logger.info(f"✅ 전체 그래프 재계산 완료: {result.total_processes_calculated}개 공정, {result.total_emission_propagated} tCO2e 전파")
        return result
    except Exception as e:
        logger.error(f"❌ 전체 그래프 재계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"전체 그래프 재계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# calculation_router를 다른 모듈에서 import할 수 있도록 export
calculation_router = router
__all__ = ["router", "calculation_router"]