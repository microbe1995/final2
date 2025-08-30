# ============================================================================
# 🎯 Calculation Controller - CBAM 계산 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List
import time

from .calculation_service import CalculationService
from .calculation_schema import (
    ProductProcessResponse, ProductProcessCreateRequest,
    ProcessAttrdirEmissionCreateRequest, ProcessAttrdirEmissionResponse, ProcessAttrdirEmissionUpdateRequest,
    ProcessEmissionCalculationRequest, ProcessEmissionCalculationResponse,
    ProductEmissionCalculationRequest, ProductEmissionCalculationResponse,
    EdgeResponse, EdgeCreateRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boundary", tags=["Calculation"])

# 서비스 인스턴스 생성
calculation_service = CalculationService()



# ============================================================================
# 🔗 ProductProcess 관련 엔드포인트 (다대다 관계)
# ============================================================================

@router.post("/product-process", response_model=ProductProcessResponse)
async def create_product_process(request: ProductProcessCreateRequest):
    """제품-공정 관계 생성"""
    try:
        logger.info(f"🔄 제품-공정 관계 생성 요청: 제품 ID {request.product_id}, 공정 ID {request.process_id}")
        result = await calculation_service.create_product_process(request)
        logger.info(f"✅ 제품-공정 관계 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 생성 중 오류가 발생했습니다: {str(e)}")

@router.delete("/product-process/{product_id}/{process_id}")
async def delete_product_process(product_id: int, process_id: int):
    """제품-공정 관계 삭제"""
    try:
        logger.info(f"🗑️ 제품-공정 관계 삭제 요청: 제품 ID {product_id}, 공정 ID {process_id}")
        success = await calculation_service.delete_product_process(product_id, process_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품-공정 관계를 찾을 수 없습니다")
        logger.info(f"✅ 제품-공정 관계 삭제 성공")
        return {"message": "제품-공정 관계가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 삭제 중 오류가 발생했습니다: {str(e)}")



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
# 🔗 Edge 관련 엔드포인트
# ============================================================================

@router.post("/edge", response_model=EdgeResponse, status_code=201)
async def create_edge(edge_data: EdgeCreateRequest):
    """Edge 생성 및 자동 통합 그룹 탐지"""
    try:
        logger.info(f"🔗 Edge 생성 요청: {edge_data.source_id} -> {edge_data.target_id} ({edge_data.edge_kind})")
        result = await calculation_service.create_edge(edge_data)
        logger.info(f"✅ Edge 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ Edge 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Edge 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/edge", response_model=List[EdgeResponse])
async def get_edges():
    """모든 Edge 목록 조회"""
    try:
        logger.info("📋 Edge 목록 조회 요청")
        edges = await calculation_service.get_edges()
        logger.info(f"✅ Edge 목록 조회 성공: {len(edges)}개")
        return edges
    except Exception as e:
        logger.error(f"❌ Edge 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Edge 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.delete("/edge/{edge_id}")
async def delete_edge(edge_id: int):
    """Edge 삭제"""
    try:
        logger.info(f"🗑️ Edge 삭제 요청: ID {edge_id}")
        success = await calculation_service.delete_edge(edge_id)
        if not success:
            raise HTTPException(status_code=404, detail="Edge를 찾을 수 없습니다")
        logger.info(f"✅ Edge 삭제 성공: ID {edge_id}")
        return {"message": "Edge가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Edge 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Edge 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# calculation_router를 다른 모듈에서 import할 수 있도록 export
calculation_router = router
__all__ = ["router", "calculation_router"]