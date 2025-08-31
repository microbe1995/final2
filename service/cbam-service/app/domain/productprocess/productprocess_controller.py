# ============================================================================
# 🏭 Product Process Controller - 제품-공정 관계 API 엔드포인트
# ============================================================================

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.domain.productprocess.productprocess_service import ProductProcessService
from app.domain.productprocess.productprocess_schema import (
    ProductProcessCreateRequest, ProductProcessResponse,
    ProductProcessUpdateRequest, ProductProcessSearchRequest,
    ProductProcessFullResponse, ProductProcessByProductResponse,
    ProductProcessByProcessResponse, ProductProcessStatsResponse
)

logger = logging.getLogger(__name__)

# Gateway를 통해 접근하므로 prefix 제거 (경로 중복 방지)
router = APIRouter(tags=["Product Process"])

# 서비스 인스턴스 생성
product_process_service = ProductProcessService()

# ============================================================================
# 🔗 ProductProcess 관련 엔드포인트 (다대다 관계)
# ============================================================================

@router.post("/", response_model=ProductProcessResponse)
async def create_product_process(request: ProductProcessCreateRequest):
    """제품-공정 관계 생성"""
    try:
        logger.info(f"🔄 제품-공정 관계 생성 요청: 제품 ID {request.product_id}, 공정 ID {request.process_id}")
        result = await product_process_service.create_product_process(request)
        logger.info(f"✅ 제품-공정 관계 생성 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/{relation_id}", response_model=ProductProcessFullResponse)
async def get_product_process_by_id(relation_id: int):
    """ID로 제품-공정 관계 조회"""
    try:
        logger.info(f"🔍 제품-공정 관계 조회 요청: ID {relation_id}")
        result = await product_process_service.get_product_process_by_id(relation_id)
        if not result:
            raise HTTPException(status_code=404, detail="제품-공정 관계를 찾을 수 없습니다")
        logger.info(f"✅ 제품-공정 관계 조회 성공: ID {relation_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/", response_model=List[ProductProcessFullResponse])
async def get_all_product_processes(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 레코드 수")
):
    """모든 제품-공정 관계 조회"""
    try:
        logger.info(f"🔍 제품-공정 관계 목록 조회 요청: skip={skip}, limit={limit}")
        result = await product_process_service.get_all_product_processes(skip, limit)
        logger.info(f"✅ 제품-공정 관계 목록 조회 성공: {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.put("/{relation_id}", response_model=ProductProcessResponse)
async def update_product_process(relation_id: int, request: ProductProcessUpdateRequest):
    """제품-공정 관계 수정"""
    try:
        logger.info(f"🔄 제품-공정 관계 수정 요청: ID {relation_id}")
        result = await product_process_service.update_product_process(relation_id, request)
        if not result:
            raise HTTPException(status_code=404, detail="제품-공정 관계를 찾을 수 없습니다")
        logger.info(f"✅ 제품-공정 관계 수정 성공: ID {relation_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 수정 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{product_id}/{process_id}")
async def delete_product_process(product_id: int, process_id: int):
    """제품-공정 관계 삭제"""
    try:
        logger.info(f"🗑️ 제품-공정 관계 삭제 요청: 제품 ID {product_id}, 공정 ID {process_id}")
        success = await product_process_service.delete_product_process(product_id, process_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품-공정 관계를 찾을 수 없습니다")
        logger.info(f"✅ 제품-공정 관계 삭제 성공")
        return {"message": "제품-공정 관계가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 삭제 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 삭제 중 오류가 발생했습니다: {str(e)}")

@router.get("/by-product/{product_id}", response_model=ProductProcessByProductResponse)
async def get_product_processes_by_product(product_id: int):
    """제품별 제품-공정 관계 조회"""
    try:
        logger.info(f"🔍 제품별 제품-공정 관계 조회 요청: 제품 ID {product_id}")
        result = await product_process_service.get_product_processes_by_product(product_id)
        logger.info(f"✅ 제품별 제품-공정 관계 조회 성공: 제품 ID {product_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 제품별 제품-공정 관계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품별 제품-공정 관계 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/by-process/{process_id}", response_model=ProductProcessByProcessResponse)
async def get_product_processes_by_process(process_id: int):
    """공정별 제품-공정 관계 조회"""
    try:
        logger.info(f"🔍 공정별 제품-공정 관계 조회 요청: 공정 ID {process_id}")
        result = await product_process_service.get_product_processes_by_process(process_id)
        logger.info(f"✅ 공정별 제품-공정 관계 조회 성공: 공정 ID {process_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 공정별 제품-공정 관계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공정별 제품-공정 관계 조회 중 오류가 발생했습니다: {str(e)}")

@router.post("/search", response_model=List[ProductProcessFullResponse])
async def search_product_processes(request: ProductProcessSearchRequest):
    """제품-공정 관계 검색"""
    try:
        logger.info(f"🔍 제품-공정 관계 검색 요청: {request}")
        result = await product_process_service.search_product_processes(request)
        logger.info(f"✅ 제품-공정 관계 검색 성공: {len(result)}개")
        return result
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/stats/overview", response_model=ProductProcessStatsResponse)
async def get_product_process_stats():
    """제품-공정 관계 통계 조회"""
    try:
        logger.info("📊 제품-공정 관계 통계 조회 요청")
        result = await product_process_service.get_product_process_stats()
        logger.info("✅ 제품-공정 관계 통계 조회 성공")
        return result
    except Exception as e:
        logger.error(f"❌ 제품-공정 관계 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 통계 조회 중 오류가 발생했습니다: {str(e)}")

# ============================================================================
# 🔄 기존 호환성 엔드포인트 (점진적 마이그레이션용)
# ============================================================================

@router.post("/legacy", response_model=ProductProcessResponse)
async def create_product_process_legacy(request: ProductProcessCreateRequest):
    """기존 호환성 엔드포인트 (점진적 마이그레이션용)"""
    try:
        logger.info(f"🔄 기존 호환성 엔드포인트 호출: 제품 ID {request.product_id}, 공정 ID {request.process_id}")
        result = await product_process_service.create_product_process(request)
        logger.info(f"✅ 기존 호환성 엔드포인트 성공: ID {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ 기존 호환성 엔드포인트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 생성 중 오류가 발생했습니다: {str(e)}")

@router.delete("/legacy/{product_id}/{process_id}")
async def delete_product_process_legacy(product_id: int, process_id: int):
    """기존 호환성 엔드포인트 (점진적 마이그레이션용)"""
    try:
        logger.info(f"🗑️ 기존 호환성 엔드포인트 호출: 제품 ID {product_id}, 공정 ID {process_id}")
        success = await product_process_service.delete_product_process(product_id, process_id)
        if not success:
            raise HTTPException(status_code=404, detail="제품-공정 관계를 찾을 수 없습니다")
        logger.info(f"✅ 기존 호환성 엔드포인트 성공")
        return {"message": "제품-공정 관계가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 기존 호환성 엔드포인트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"제품-공정 관계 삭제 중 오류가 발생했습니다: {str(e)}")
