# ============================================================================
# 🎯 MatDir Controller - 원료직접배출량 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException
import logging
from typing import List
import time

from .matdir_service import MatDirService
from .matdir_schema import (
    MatDirCreateRequest, 
    MatDirUpdateRequest, 
    MatDirResponse,
    MatDirCalculationRequest,
    MatDirCalculationResponse,
    # 🔍 원료-배출계수 매핑 관련 스키마들
    MaterialMappingResponse,
    MaterialMappingCreateRequest,
    MaterialMappingUpdateRequest,
    MaterialMappingFullResponse,
    MaterialNameLookupRequest,
    MaterialNameLookupResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/boundary", tags=["material_master"])

# 서비스 인스턴스 생성
matdir_service = MatDirService()

# ============================================================================
# 📦 1. 기존 MatDir 관련 엔드포인트 (원료직접배출량 데이터 관리)
# ============================================================================

@router.post("/matdir", response_model=MatDirResponse, status_code=201)
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

@router.get("/matdir", response_model=List[MatDirResponse])
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

@router.get("/matdir/process/{process_id}", response_model=List[MatDirResponse])
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

@router.get("/matdir/{matdir_id}", response_model=MatDirResponse)
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

@router.put("/matdir/{matdir_id}", response_model=MatDirResponse)
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

@router.delete("/matdir/{matdir_id}")
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

@router.post("/matdir/calculate", response_model=MatDirCalculationResponse)
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

@router.get("/matdir/process/{process_id}/total")
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
# 🔍 3. 원료 마스터 관리 엔드포인트 (통합)
# ============================================================================

@router.post("/material-master", response_model=MaterialMappingFullResponse, status_code=201)
async def create_material_mapping(mapping_data: MaterialMappingCreateRequest):
    """원료-배출계수 매핑 생성"""
    try:
        logger.info(f"📝 원료-배출계수 매핑 생성 요청: {mapping_data.dict()}")
        result = await matdir_service.create_material_mapping(mapping_data)
        logger.info(f"✅ 원료-배출계수 매핑 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 원료-배출계수 매핑 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료-배출계수 매핑 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/material-master", response_model=List[MaterialMappingFullResponse])
async def get_material_master_list(skip: int = 0, limit: int = 100):
    """원료 마스터 목록 조회"""
    try:
        logger.info("📋 원료 마스터 목록 조회 요청")
        mappings = await matdir_service.get_all_material_mappings(skip, limit)
        logger.info(f"✅ 원료 마스터 목록 조회 성공: {len(mappings)}개")
        return mappings
    except Exception as e:
        logger.error(f"❌ 원료 마스터 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 마스터 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/material-master/{mapping_id}", response_model=MaterialMappingFullResponse)
async def get_material_mapping(mapping_id: int):
    """특정 원료-배출계수 매핑 조회"""
    try:
        logger.info(f"📋 원료-배출계수 매핑 조회 요청: ID {mapping_id}")
        mapping = await matdir_service.get_material_mapping(mapping_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="원료-배출계수 매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ 원료-배출계수 매핑 조회 성공: ID {mapping_id}")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료-배출계수 매핑 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료-배출계수 매핑 조회 중 오류가 발생했습니다: {str(e)}")

@router.put("/material-master/{mapping_id}", response_model=MaterialMappingFullResponse)
async def update_material_mapping(mapping_id: int, mapping_data: MaterialMappingUpdateRequest):
    """원료-배출계수 매핑 수정"""
    try:
        logger.info(f"📝 원료-배출계수 매핑 수정 요청: ID {mapping_id}")
        result = await matdir_service.update_material_mapping(mapping_id, mapping_data)
        if not result:
            raise HTTPException(status_code=404, detail="원료-배출계수 매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ 원료-배출계수 매핑 수정 성공: ID {mapping_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료-배출계수 매핑 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료-배출계수 매핑 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/material-master/{mapping_id}")
async def delete_material_mapping(mapping_id: int):
    """원료-배출계수 매핑 삭제"""
    try:
        logger.info(f"🗑️ 원료-배출계수 매핑 삭제 요청: ID {mapping_id}")
        success = await matdir_service.delete_material_mapping(mapping_id)
        if not success:
            raise HTTPException(status_code=404, detail="원료-배출계수 매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ 원료-배출계수 매핑 삭제 성공: ID {mapping_id}")
        return {"message": "원료-배출계수 매핑이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 원료-배출계수 매핑 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료-배출계수 매핑 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔍 4. 원료명 검색 및 배출계수 조회 엔드포인트 (통합)
# ============================================================================

@router.get("/material-master/search/{mat_name}", response_model=MaterialNameLookupResponse)
async def search_material_master_by_name(mat_name: str):
    """원료 마스터에서 원료명으로 검색 (부분 검색)"""
    try:
        logger.info(f"🔍 원료 마스터 검색 요청: '{mat_name}'")
        result = await matdir_service.lookup_material_by_name(mat_name)
        logger.info(f"✅ 원료 마스터 검색 성공: '{mat_name}' → {result.count}개 결과")
        return result
    except Exception as e:
        logger.error(f"❌ 원료 마스터 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 마스터 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/material-master/factor/{mat_name}", response_model=MaterialNameLookupResponse)
async def get_material_master_factor(mat_name: str):
    """원료 마스터에서 원료명으로 배출계수 조회"""
    try:
        logger.info(f"🔍 원료 마스터 배출계수 조회 요청: '{mat_name}'")
        result = await matdir_service.lookup_material_by_name(mat_name)
        logger.info(f"✅ 원료 마스터 배출계수 조회 성공: '{mat_name}' → {result.count}개 결과")
        return result
    except Exception as e:
        logger.error(f"❌ 원료 마스터 배출계수 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"원료 마스터 배출계수 조회 중 오류가 발생했습니다: {str(e)}")
