# ============================================================================
# 🏭 Material Directory Controller - 원료 디렉토리 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List, Dict, Any
import time

from app.domain.matdir.matdir_service import MatDirService
from app.domain.matdir.matdir_schema import (
    MatDirCreateRequest, 
    MatDirUpdateRequest, 
    MatDirResponse,
    MatDirCalculationRequest,
    MatDirCalculationResponse
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Material Directory"])

# 서비스 인스턴스 생성
matdir_service = MatDirService()

# ============================================================================
# 📦 1. 기존 MatDir 관련 엔드포인트 (원료직접배출량 데이터 관리)
# ============================================================================

@router.post("/create", response_model=MatDirResponse, status_code=201)
async def create_matdir(matdir_data: MatDirCreateRequest):
    """원료직접배출량 데이터 생성"""
    try:
        logger.info(f"📝 원료직접배출량 생성 요청: {matdir_data.dict()}")
        result = await matdir_service.create_matdir(matdir_data)
        logger.info(f"✅ 원료직접배출량 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/list", response_model=List[MatDirResponse])
async def get_matdirs(skip: int = 0, limit: int = 100):
    """모든 원료직접배출량 데이터 조회"""
    try:
        logger.info("📋 원료직접배출량 목록 조회 요청")
        matdirs = await matdir_service.get_matdirs(skip, limit)
        logger.info(f"✅ 원료직접배출량 목록 조회 성공: {len(matdirs)}개")
        return matdirs
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/process/{process_id}", response_model=List[MatDirResponse])
async def get_matdirs_by_process(process_id: int):
    """특정 공정의 원료직접배출량 데이터 조회"""
    try:
        logger.info(f"📋 공정별 원료직접배출량 조회 요청: Process ID {process_id}")
        matdirs = await matdir_service.get_matdirs_by_process(process_id)
        logger.info(f"✅ 공정별 원료직접배출량 조회 성공: {len(matdirs)}개")
        return matdirs
    except Exception as e:
        logger.error(f"❌ 공정별 원료직접배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 원료직접배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{matdir_id}", response_model=MatDirResponse)
async def get_matdir(matdir_id: int):
    """특정 원료직접배출량 데이터 조회"""
    try:
        logger.info(f"📋 원료직접배출량 조회 요청: ID {matdir_id}")
        matdir = await matdir_service.get_matdir(matdir_id)
        if not matdir:
            raise HTTPException(status_code=404, detail="원료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 원료직접배출량 조회 성공: ID {matdir_id}")
        return matdir
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 조회 중 오류가 발생했습니다: {str(e)}")

@router.put("/{matdir_id}", response_model=MatDirResponse)
async def update_matdir(matdir_id: int, matdir_data: MatDirUpdateRequest):
    """원료직접배출량 데이터 수정"""
    try:
        logger.info(f"📝 원료직접배출량 수정 요청: ID {matdir_id}")
        result = await matdir_service.update_matdir(matdir_id, matdir_data)
        if not result:
            raise HTTPException(status_code=404, detail="원료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 원료직접배출량 수정 성공: ID {matdir_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{matdir_id}")
async def delete_matdir(matdir_id: int):
    """원료직접배출량 데이터 삭제"""
    try:
        logger.info(f"🗑️ 원료직접배출량 삭제 요청: ID {matdir_id}")
        success = await matdir_service.delete_matdir(matdir_id)
        if not success:
            raise HTTPException(status_code=404, detail="원료직접배출량 데이터를 찾을 수 없습니다")
        
        logger.info(f"✅ 원료직접배출량 삭제 성공: ID {matdir_id}")
        return {"message": "원료직접배출량 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🧮 2. 계산 관련 엔드포인트
# ============================================================================

@router.post("/calculate", response_model=MatDirCalculationResponse)
async def calculate_matdir_emission(calculation_data: MatDirCalculationRequest):
    """원료직접배출량 계산 (공식 포함)"""
    try:
        logger.info(f"🧮 원료직접배출량 계산 요청: {calculation_data.dict()}")
        result = matdir_service.calculate_matdir_emission_with_formula(calculation_data)
        logger.info(f"✅ 원료직접배출량 계산 성공: {result.matdir_em}")
        return result
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

@router.get("/process/{process_id}/total")
async def get_total_matdir_emission_by_process(process_id: int):
    """특정 공정의 총 원료직접배출량 계산"""
    try:
        logger.info(f"🧮 공정별 총 원료직접배출량 계산 요청: Process ID {process_id}")
        total_emission = await matdir_service.get_total_matdir_emission_by_process(process_id)
        logger.info(f"✅ 공정별 총 원료직접배출량 계산 성공: {total_emission}")
        return {"process_id": process_id, "total_matdir_emission": float(total_emission)}
    except Exception as e:
        logger.error(f"❌ 공정별 총 원료직접배출량 계산 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 총 원료직접배출량 계산 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🏗️ Material Master 관련 엔드포인트 (fueldir과 동일한 패턴)
# ============================================================================

@router.get("/material-master", response_model=Dict[str, Any])
async def get_all_materials():
    """모든 원료 마스터 데이터 조회 - Railway DB의 materials 테이블 사용"""
    try:
        logger.info("📋 모든 원료 마스터 데이터 조회 요청")
        result = await matdir_service.get_all_materials()
        logger.info(f"✅ 모든 원료 마스터 데이터 조회 성공: {result['total_count']}개")
        return result
    except Exception as e:
        logger.error(f"❌ 모든 원료 마스터 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 마스터 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/material-master/search/{mat_name}", response_model=List[Dict[str, Any]])
async def search_materials(mat_name: str):
    """원료명으로 검색 (부분 검색) - Railway DB의 materials 테이블 사용"""
    try:
        logger.info(f"🔍 원료 마스터 검색 요청: '{mat_name}'")
        materials = await matdir_service.search_materials(mat_name)
        logger.info(f"✅ 원료 마스터 검색 성공: '{mat_name}' → {len(materials)}개 결과")
        return materials
    except Exception as e:
        logger.error(f"❌ 원료 마스터 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 마스터 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/material-master/factor/{mat_name}", response_model=Dict[str, Any])
async def get_material_factor(mat_name: str):
    """원료명으로 배출계수 조회 (자동 매핑 기능) - Railway DB의 materials 테이블 사용"""
    try:
        logger.info(f"🔍 원료 배출계수 조회 요청: '{mat_name}'")
        result = await matdir_service.get_material_factor_by_name(mat_name)
        if result.get('found'):
            logger.info(f"✅ 원료 배출계수 조회 성공: '{mat_name}' → {result['mat_factor']}")
        else:
            logger.warning(f"⚠️ 원료 배출계수를 찾을 수 없음: '{mat_name}'")
        return result
    except Exception as e:
        logger.error(f"❌ 원료 배출계수 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 배출계수 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/auto-factor", response_model=MatDirResponse, status_code=201)
async def create_matdir_with_auto_factor(matdir_data: MatDirCreateRequest):
    """원료직접배출량 데이터 생성 (배출계수 자동 매핑) - Railway DB의 materials 테이블 사용"""
    try:
        logger.info(f"📝 원료직접배출량 생성 요청 (자동 배출계수): {matdir_data.dict()}")
        result = await matdir_service.create_matdir_with_auto_factor(matdir_data)
        logger.info(f"✅ 원료직접배출량 생성 성공 (자동 배출계수): ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 원료직접배출량 생성 실패 (자동 배출계수): {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료직접배출량 생성 중 오류가 발생했습니다: {str(e)}")
