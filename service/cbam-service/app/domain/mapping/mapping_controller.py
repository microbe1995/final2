# ============================================================================
# 🏭 Mapping Controller - 매핑 API 엔드포인트
# ============================================================================

from fastapi import APIRouter, HTTPException, Query
import logging
from typing import List

from app.domain.mapping.mapping_service import HSCNMappingService
from app.domain.mapping.mapping_schema import (
    HSCNMappingCreateRequest, HSCNMappingResponse, HSCNMappingUpdateRequest,
    HSCNMappingFullResponse, HSCodeLookupResponse, MappingStatsResponse,
    HSCNMappingBatchCreateRequest, HSCNMappingBatchResponse
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Mapping"])

# 서비스 인스턴스는 요청 시마다 생성 (모듈 레벨 초기화 방지)
def get_mapping_service():
    """매핑 서비스 인스턴스 반환"""
    return HSCNMappingService(None)  # Repository에서 직접 DB 연결 사용

# ============================================================================
# 🔍 HS 코드 조회 엔드포인트 (메인 기능)
# ============================================================================

@router.get("/cncode/lookup/{hs_code}", response_model=List[HSCNMappingResponse])
async def lookup_cn_code_by_hs_code(hs_code: str):
    """
    HS 코드로 CN 코드 조회 (부분 검색 허용)
    
    - **hs_code**: HS 코드 (예: 72, 720, 7208, 720851) - 2자리 이상 입력
    - **응답**: CN 코드 매핑 정보 목록
    """
    try:
        logger.info(f"🔍 HS 코드 조회 요청: {hs_code}")
        
        mapping_service = get_mapping_service()
        result = await mapping_service.lookup_by_hs_code(hs_code)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"✅ HS 코드 조회 성공: {hs_code} -> {result.count}개 결과")
        return result.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HS 코드 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HS 코드 조회 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📋 기본 CRUD 엔드포인트
# ============================================================================

@router.get("/mapping", response_model=List[HSCNMappingFullResponse])
async def get_all_mappings(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 레코드 수")
):
    """모든 HS-CN 매핑 조회 (페이지네이션)"""
    try:
        logger.info(f"📋 HS-CN 매핑 목록 조회 요청: skip={skip}, limit={limit}")
        mapping_service = get_mapping_service()
        mappings = await mapping_service.get_all_mappings(skip, limit)
        logger.info(f"✅ HS-CN 매핑 목록 조회 성공: {len(mappings)}개")
        return mappings
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/mapping/{mapping_id}", response_model=HSCNMappingFullResponse)
async def get_mapping(mapping_id: int):
    """특정 HS-CN 매핑 조회"""
    try:
        logger.info(f"📋 HS-CN 매핑 조회 요청: ID {mapping_id}")
        mapping_service = get_mapping_service()
        mapping = await mapping_service.get_mapping_by_id(mapping_id)
        if not mapping:
            raise HTTPException(status_code=404, detail="매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ HS-CN 매핑 조회 성공: ID {mapping_id}")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/mapping", response_model=HSCNMappingFullResponse)
async def create_mapping(request: HSCNMappingCreateRequest):
    """HS-CN 매핑 생성"""
    try:
        logger.info(f"📝 HS-CN 매핑 생성 요청: HS={request.hscode}, CN={request.cncode_total}")
        mapping_service = get_mapping_service()
        mapping = await mapping_service.create_mapping(request)
        if not mapping:
            raise HTTPException(status_code=400, detail="매핑 생성에 실패했습니다")
        
        logger.info(f"✅ HS-CN 매핑 생성 성공: ID {mapping.id}")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 생성 중 오류가 발생했습니다: {str(e)}")

@router.put("/mapping/{mapping_id}", response_model=HSCNMappingFullResponse)
async def update_mapping(mapping_id: int, request: HSCNMappingUpdateRequest):
    """HS-CN 매핑 수정"""
    try:
        logger.info(f"📝 HS-CN 매핑 수정 요청: ID {mapping_id}")
        mapping_service = get_mapping_service()
        mapping = await mapping_service.update_mapping(mapping_id, request)
        if not mapping:
            raise HTTPException(status_code=404, detail="매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ HS-CN 매핑 수정 성공: ID {mapping_id}")
        return mapping
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/mapping/{mapping_id}")
async def delete_mapping(mapping_id: int):
    """HS-CN 매핑 삭제"""
    try:
        logger.info(f"🗑️ HS-CN 매핑 삭제 요청: ID {mapping_id}")
        mapping_service = get_mapping_service()
        success = await mapping_service.delete_mapping(mapping_id)
        if not success:
            raise HTTPException(status_code=404, detail="매핑을 찾을 수 없습니다")
        
        logger.info(f"✅ HS-CN 매핑 삭제 성공: ID {mapping_id}")
        return {"message": "매핑이 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 삭제 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔍 검색 엔드포인트
# ============================================================================

@router.get("/mapping/search/hs/{hs_code}", response_model=List[HSCNMappingFullResponse])
async def search_by_hs_code(hs_code: str):
    """HS 코드로 검색"""
    try:
        logger.info(f"🔍 HS 코드 검색 요청: {hs_code}")
        mapping_service = get_mapping_service()
        mappings = await mapping_service.search_by_hs_code(hs_code)
        logger.info(f"✅ HS 코드 검색 성공: {len(mappings)}개 결과")
        return mappings
    except Exception as e:
        logger.error(f"❌ HS 코드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HS 코드 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/mapping/search/cn/{cn_code}", response_model=List[HSCNMappingFullResponse])
async def search_by_cn_code(cn_code: str):
    """CN 코드로 검색"""
    try:
        logger.info(f"🔍 CN 코드 검색 요청: {cn_code}")
        mapping_service = get_mapping_service()
        mappings = await mapping_service.search_by_cn_code(cn_code)
        logger.info(f"✅ CN 코드 검색 성공: {len(mappings)}개 결과")
        return mappings
    except Exception as e:
        logger.error(f"❌ CN 코드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CN 코드 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/mapping/search/goods/{goods_name}", response_model=List[HSCNMappingFullResponse])
async def search_by_goods_name(goods_name: str):
    """품목명으로 검색"""
    try:
        logger.info(f"🔍 품목명 검색 요청: {goods_name}")
        mapping_service = get_mapping_service()
        mappings = await mapping_service.search_by_goods_name(goods_name)
        logger.info(f"✅ 품목명 검색 성공: {len(mappings)}개 결과")
        return mappings
    except Exception as e:
        logger.error(f"❌ 품목명 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"품목명 검색 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📊 통계 엔드포인트
# ============================================================================

@router.get("/mapping/stats", response_model=MappingStatsResponse)
async def get_mapping_stats():
    """매핑 통계 조회"""
    try:
        logger.info("📊 매핑 통계 조회 요청")
        mapping_service = get_mapping_service()
        stats = await mapping_service.get_mapping_stats()
        logger.info("✅ 매핑 통계 조회 성공")
        return stats
    except Exception as e:
        logger.error(f"❌ 매핑 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 통계 조회 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 일괄 처리 엔드포인트
# ============================================================================

@router.post("/mapping/batch", response_model=HSCNMappingBatchResponse)
async def create_mappings_batch(request: HSCNMappingBatchCreateRequest):
    """HS-CN 매핑 일괄 생성"""
    try:
        logger.info(f"📦 HS-CN 매핑 일괄 생성 요청: {len(request.mappings)}개")
        mapping_service = get_mapping_service()
        result = await mapping_service.create_mappings_batch(request)
        logger.info(f"✅ HS-CN 매핑 일괄 생성 완료: 성공 {result.created_count}개, 실패 {result.failed_count}개")
        return result
    except Exception as e:
        logger.error(f"❌ HS-CN 매핑 일괄 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"매핑 일괄 생성 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 📦 Router Export
# ============================================================================

# mapping_router를 다른 모듈에서 import할 수 있도록 export
mapping_router = router
__all__ = ["router", "mapping_router"]
