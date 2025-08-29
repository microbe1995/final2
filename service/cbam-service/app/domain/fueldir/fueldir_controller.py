# ============================================================================
# 🎯 FuelDir Controller - 연료직접배출량 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List
import time

from .fueldir_service import FuelDirService
from .fueldir_schema import (
    FuelDirCreateRequest, 
    FuelDirUpdateRequest, 
    FuelDirResponse,
    FuelDirCalculationRequest,
    FuelDirCalculationResponse,
    FuelMasterSearchRequest,
    FuelMasterResponse,
    FuelMasterListResponse,
    FuelMasterFactorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boundary", tags=["fueldir_em"])

# 서비스 인스턴스 생성
fueldir_service = FuelDirService()

# ============================================================================
# 📦 기존 FuelDir 관련 엔드포인트
# ============================================================================

@router.post("/fueldir", response_model=FuelDirResponse, status_code=201)
async def create_fueldir(fueldir_data: FuelDirCreateRequest):
    """연료직접배출량 데이터 생성"""
    try:
        logger.info(f"📝 연료직접배출량 생성 요청: {fueldir_data.dict()}")
        result = await fueldir_service.create_fueldir(fueldir_data)
        logger.info(f"✅ 연료직접배출량 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/fueldir", response_model=List[FuelDirResponse])
async def get_fueldirs(skip: int = 0, limit: int = 100):
    """모든 연료직접배출량 데이터 조회"""
    try:
        logger.info("📋 연료직접배출량 목록 조회 요청")
        fueldirs = await fueldir_service.get_fueldirs(skip, limit)
        logger.info(f"✅ 연료직접배출량 목록 조회 성공: {len(fueldirs)}개")
        return fueldirs
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/fueldir/process/{process_id}", response_model=List[FuelDirResponse])
async def get_fueldirs_by_process(process_id: int):
    """특정 공정의 연료직접배출량 데이터 조회"""
    try:
        logger.info(f"📋 공정별 연료직접배출량 조회 요청: Process ID {process_id}")
        fueldirs = await fueldir_service.get_fueldirs_by_process(process_id)
        logger.info(f"✅ 공정별 연료직접배출량 조회 성공: {len(fueldirs)}개")
        return fueldirs
    except Exception as e:
        logger.error(f"❌ 공정별 연료직접배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 연료직접배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/fueldir/{fueldir_id}", response_model=FuelDirResponse)
async def get_fueldir(fueldir_id: int):
    """특정 연료직접배출량 데이터 조회"""
    try:
        logger.info(f"📋 연료직접배출량 조회 요청: ID {fueldir_id}")
        fueldir = await fueldir_service.get_fueldir(fueldir_id)
        if not fueldir:
            raise HTTPException(status_code=404, detail="연료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 연료직접배출량 조회 성공: ID {fueldir_id}")
        return fueldir
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.put("/fueldir/{fueldir_id}", response_model=FuelDirResponse)
async def update_fueldir(fueldir_id: int, fueldir_data: FuelDirUpdateRequest):
    """연료직접배출량 데이터 수정"""
    try:
        logger.info(f"📝 연료직접배출량 수정 요청: ID {fueldir_id}")
        result = await fueldir_service.update_fueldir(fueldir_id, fueldir_data)
        if not result:
            raise HTTPException(status_code=404, detail="연료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 연료직접배출량 수정 성공: ID {fueldir_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/fueldir/{fueldir_id}")
async def delete_fueldir(fueldir_id: int):
    """연료직접배출량 데이터 삭제"""
    try:
        logger.info(f"🗑️ 연료직접배출량 삭제 요청: ID {fueldir_id}")
        success = await fueldir_service.delete_fueldir(fueldir_id)
        if not success:
            raise HTTPException(status_code=404, detail="연료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 연료직접배출량 삭제 성공: ID {fueldir_id}")
        return {"message": "연료직접배출량 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🧮 계산 관련 엔드포인트
# ============================================================================

@router.post("/fueldir/calculate", response_model=FuelDirCalculationResponse)
async def calculate_fueldir_emission(calculation_data: FuelDirCalculationRequest):
    """연료직접배출량 계산 (공식 포함)"""
    try:
        logger.info(f"🧮 연료직접배출량 계산 요청: {calculation_data.dict()}")
        result = fueldir_service.calculate_fueldir_emission_with_formula(calculation_data)
        logger.info(f"✅ 연료직접배출량 계산 성공: {result.fueldir_em}")
        return result
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.get("/fueldir/process/{process_id}/total")
async def get_total_fueldir_emission_by_process(process_id: int):
    """특정 공정의 총 연료직접배출량 계산"""
    try:
        logger.info(f"🧮 공정별 총 연료직접배출량 계산 요청: Process ID {process_id}")
        total_emission = await fueldir_service.get_total_fueldir_emission_by_process(process_id)
        logger.info(f"✅ 공정별 총 연료직접배출량 계산 성공: {total_emission}")
        return {"process_id": process_id, "total_fueldir_emission": float(total_emission)}
    except Exception as e:
        logger.error(f"❌ 공정별 총 연료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 총 연료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🏗️ Fuel Master 관련 엔드포인트 (새로 추가)
# ============================================================================

@router.get("/fuel-master", response_model=FuelMasterListResponse)
async def get_all_fuels():
    """모든 연료 마스터 데이터 조회"""
    try:
        logger.info("📋 모든 연료 마스터 데이터 조회 요청")
        result = await fueldir_service.get_all_fuels()
        logger.info(f"✅ 모든 연료 마스터 데이터 조회 성공: {result.total_count}개")
        return result
    except Exception as e:
        logger.error(f"❌ 모든 연료 마스터 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료 마스터 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/fuel-master/search/{fuel_name}", response_model=List[FuelMasterResponse])
async def search_fuels(fuel_name: str):
    """연료명으로 검색 (부분 검색)"""
    try:
        logger.info(f"🔍 연료 마스터 검색 요청: '{fuel_name}'")
        fuels = await fueldir_service.search_fuels(fuel_name)
        logger.info(f"✅ 연료 마스터 검색 성공: '{fuel_name}' → {len(fuels)}개 결과")
        return fuels
    except Exception as e:
        logger.error(f"❌ 연료 마스터 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료 마스터 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/fuel-master/factor/{fuel_name}", response_model=FuelMasterFactorResponse)
async def get_fuel_factor(fuel_name: str):
    """연료명으로 배출계수 조회 (자동 매핑 기능)"""
    try:
        logger.info(f"🔍 연료 배출계수 조회 요청: '{fuel_name}'")
        result = await fueldir_service.get_fuel_factor_by_name(fuel_name)
        if result.found:
            logger.info(f"✅ 연료 배출계수 조회 성공: '{fuel_name}' → {result.fuel_factor}")
        else:
            logger.warning(f"⚠️ 연료 배출계수를 찾을 수 없음: '{fuel_name}'")
        return result
    except Exception as e:
        logger.error(f"❌ 연료 배출계수 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료 배출계수 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/fueldir/auto-factor", response_model=FuelDirResponse, status_code=201)
async def create_fueldir_with_auto_factor(fueldir_data: FuelDirCreateRequest):
    """연료직접배출량 데이터 생성 (배출계수 자동 매핑)"""
    try:
        logger.info(f"📝 연료직접배출량 생성 요청 (자동 배출계수): {fueldir_data.dict()}")
        result = await fueldir_service.create_fueldir_with_auto_factor(fueldir_data)
        logger.info(f"✅ 연료직접배출량 생성 성공 (자동 배출계수): ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 생성 실패 (자동 배출계수): {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 생성 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🧮 계산 관련 엔드포인트
# ============================================================================

@router.post("/fueldir/calculate", response_model=FuelDirCalculationResponse)
async def calculate_fueldir_emission(calculation_data: FuelDirCalculationRequest):
    """연료직접배출량 계산 (공식 포함)"""
    try:
        logger.info(f"🧮 연료직접배출량 계산 요청: {calculation_data.dict()}")
        result = fueldir_service.calculate_fueldir_emission_with_formula(calculation_data)
        logger.info(f"✅ 연료직접배출량 계산 성공: {result.fueldir_em}")
        return result
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.get("/fueldir/process/{process_id}/total")
async def get_total_fueldir_emission_by_process(process_id: int):
    """특정 공정의 총 연료직접배출량 계산"""
    try:
        logger.info(f"🧮 공정별 총 연료직접배출량 계산 요청: Process ID {process_id}")
        total_emission = await fueldir_service.get_total_fueldir_emission_by_process(process_id)
        logger.info(f"✅ 공정별 총 연료직접배출량 계산 성공: {total_emission}")
        return {"process_id": process_id, "total_fueldir_emission": float(total_emission)}
    except Exception as e:
        logger.error(f"❌ 공정별 총 연료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 총 연료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📊 통계 및 요약 엔드포인트
# ============================================================================

@router.get("/fueldir/stats/summary")
async def get_fueldir_summary():
    """연료직접배출량 통계 요약"""
    try:
        logger.info("📊 연료직접배출량 통계 요약 요청")
        summary = await fueldir_service.get_fueldir_summary()
        logger.info(f"✅ 연료직접배출량 통계 요약 생성 성공: {summary}")
        return summary
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 통계 요약 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 통계 요약 생성 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔍 검색 및 필터링 엔드포인트
# ============================================================================

@router.get("/fueldir/search/fuel-name")
async def search_fueldirs_by_fuel_name(fuel_name: str, skip: int = 0, limit: int = 100):
    """연료명으로 연료직접배출량 검색"""
    try:
        logger.info(f"🔍 연료명으로 연료직접배출량 검색 요청: '{fuel_name}'")
        fueldirs = await fueldir_service.search_fueldirs_by_name(fuel_name, skip, limit)
        logger.info(f"✅ 연료명 검색 성공: {len(fueldirs)}개")
        return fueldirs
    except Exception as e:
        logger.error(f"❌ 연료명 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료명 검색 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 일괄 처리 엔드포인트
# ============================================================================

@router.post("/fueldir/bulk")
async def create_fueldirs_bulk(fueldirs_data: List[FuelDirCreateRequest]):
    """여러 연료직접배출량 데이터 일괄 생성"""
    try:
        logger.info(f"📦 연료직접배출량 일괄 생성 요청: {len(fueldirs_data)}개")
        results = []
        
        for fueldir_data in fueldirs_data:
            try:
                result = await fueldir_service.create_fueldir(fueldir_data)
                results.append(result)
            except Exception as e:
                logger.error(f"❌ 개별 연료직접배출량 생성 실패: {str(e)}")
                # 개별 실패는 전체 실패로 처리하지 않음
        
        logger.info(f"✅ 연료직접배출량 일괄 생성 완료: {len(results)}/{len(fueldirs_data)}개 성공")
        return {
            "message": f"일괄 생성 완료: {len(results)}/{len(fueldirs_data)}개 성공",
            "success_count": len(results),
            "total_count": len(fueldirs_data),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ 연료직접배출량 일괄 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"연료직접배출량 일괄 생성 중 오류가 발생했습니다: {str(e)}")
