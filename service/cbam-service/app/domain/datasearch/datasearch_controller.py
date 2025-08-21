# ============================================================================
# 🔍 DataSearch Controller - CBAM 데이터 검색 HTTP API
# ============================================================================

from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional
from loguru import logger
from datetime import datetime

from .datasearch_service import DataSearchService
from .datasearch_repository import DataSearchRepository
from .datasearch_schema import (
    HSCodeSearchResponse,
    CountrySearchRequest,
    CountrySearchResponse,
    FuelSearchResponse,
    MaterialSearchResponse,
    PrecursorSearchResponse,
    HealthCheckResponse,
    SearchStatsResponse
)

# 라우터 생성
datasearch_router = APIRouter(tags=["datasearch"])

# 서비스 의존성
def get_datasearch_repository() -> DataSearchRepository:
    return DataSearchRepository(use_database=False)  # 메모리 사용

def get_datasearch_service() -> DataSearchService:
    repository = get_datasearch_repository()
    return DataSearchService(repository=repository)

# ============================================================================
# 📊 HS코드 검색 API
# ============================================================================

@datasearch_router.get("/data/hscode/search", response_model=HSCodeSearchResponse)
async def search_hscode(
    hs: str = Query(..., description="HS코드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(5, ge=1, le=20, description="페이지 크기"),
    datasearch_service: DataSearchService = Depends(get_datasearch_service)
):
    """📊 **HS코드 검색** - HS코드로 품목 정보를 검색합니다."""
    try:
        logger.info(f"📊 HS코드 검색 API 호출: '{hs}' (페이지: {page})")
        
        result = await datasearch_service.search_hscode(hs, page, page_size)
        
        logger.info(f"✅ HS코드 검색 API 성공: {len(result.results)}개")
        return result
        
    except ValueError as e:
        logger.error(f"❌ HS코드 검색 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ HS코드 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="HS코드 검색 중 오류가 발생했습니다")

# ============================================================================
# 🌍 국가 검색 API
# ============================================================================

@datasearch_router.post("/data/country/search", response_model=CountrySearchResponse)
async def search_country(
    request: CountrySearchRequest,
    datasearch_service: DataSearchService = Depends(get_datasearch_service)
):
    """🌍 **국가 검색** - 한글 국가명으로 국가 정보를 검색합니다."""
    try:
        logger.info(f"🌍 국가 검색 API 호출: '{request.name_kr}'")
        
        result = await datasearch_service.search_country(request)
        
        logger.info(f"✅ 국가 검색 API 성공: {len(result.result)}개")
        return result
        
    except ValueError as e:
        logger.error(f"❌ 국가 검색 API 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ 국가 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="국가 검색 중 오류가 발생했습니다")

# ============================================================================
# 🔥 연료 검색 API
# ============================================================================

@datasearch_router.get("/data/fuels/search", response_model=FuelSearchResponse)
async def search_fuels(
    search: str = Query("", description="검색어"),
    limit: int = Query(50, ge=1, le=100, description="결과 제한"),
    datasearch_service: DataSearchService = Depends(get_datasearch_service)
):
    """🔥 **연료 검색** - 연료 정보를 검색합니다."""
    try:
        logger.info(f"🔥 연료 검색 API 호출: '{search}'")
        
        result = await datasearch_service.search_fuels(search, limit)
        
        logger.info(f"✅ 연료 검색 API 성공: {len(result.fuels)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 연료 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="연료 검색 중 오류가 발생했습니다")

# ============================================================================
# 🧱 원료 검색 API
# ============================================================================

@datasearch_router.get("/data/materials/search", response_model=MaterialSearchResponse)
async def search_materials(
    search: str = Query("", description="검색어"),
    limit: int = Query(50, ge=1, le=100, description="결과 제한"),
    datasearch_service: DataSearchService = Depends(get_datasearch_service)
):
    """🧱 **원료 검색** - 원료 정보를 검색합니다."""
    try:
        logger.info(f"🧱 원료 검색 API 호출: '{search}'")
        
        result = await datasearch_service.search_materials(search, limit)
        
        logger.info(f"✅ 원료 검색 API 성공: {len(result.materials)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 원료 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="원료 검색 중 오류가 발생했습니다")

# ============================================================================
# 🔗 전구물질 검색 API
# ============================================================================

@datasearch_router.get("/data/precursors/search", response_model=PrecursorSearchResponse)
async def search_precursors(
    search: str = Query("", description="검색어"),
    limit: int = Query(50, ge=1, le=100, description="결과 제한"),
    datasearch_service: DataSearchService = Depends(get_datasearch_service)
):
    """🔗 **전구물질 검색** - 전구물질 정보를 검색합니다."""
    try:
        logger.info(f"🔗 전구물질 검색 API 호출: '{search}'")
        
        result = await datasearch_service.search_precursors(search, limit)
        
        logger.info(f"✅ 전구물질 검색 API 성공: {len(result.precursors)}개")
        return result
        
    except Exception as e:
        logger.error(f"❌ 전구물질 검색 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="전구물질 검색 중 오류가 발생했습니다")

# ============================================================================
# 📊 통계 API
# ============================================================================

@datasearch_router.get("/data/stats", response_model=SearchStatsResponse)
async def get_search_stats(datasearch_service: DataSearchService = Depends(get_datasearch_service)):
    """📊 **검색 통계 조회** - 검색 관련 통계 정보를 조회합니다."""
    try:
        logger.info(f"📊 검색 통계 조회 API 호출")
        
        result = await datasearch_service.get_search_stats()
        
        logger.info(f"✅ 검색 통계 조회 API 성공")
        return result
        
    except Exception as e:
        logger.error(f"❌ 검색 통계 조회 API 오류: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="검색 통계 조회 중 오류가 발생했습니다")

# ============================================================================
# 🏥 헬스체크 API
# ============================================================================

@datasearch_router.get("/health")
async def datasearch_health_check():
    """데이터 검색 서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "CBAM Data Search Domain",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# 📝 예제 API
# ============================================================================

@datasearch_router.get("/data/examples/hscode")
async def get_hscode_search_example():
    """HS코드 검색 예제"""
    return {
        "example_request": {
            "hs": "7208",
            "page": 1,
            "page_size": 5
        },
        "example_response": {
            "results": [
                {
                    "id": 1,
                    "hs_코드": 720810,
                    "품목군__(cn기준)": "철강",
                    "품목_(cn기준)": "평판압연제품",
                    "직접": 1.89,
                    "간접": 0.95
                }
            ],
            "total": 2,
            "page": 1,
            "page_size": 5
        },
        "usage": "이 예제를 참고하여 HS코드를 검색하세요"
    }

@datasearch_router.get("/data/examples/country")
async def get_country_search_example():
    """국가 검색 예제"""
    return {
        "example_request": {
            "name_kr": "독일"
        },
        "example_response": {
            "result": [
                {
                    "name_en": "Germany",
                    "name_kr": "독일",
                    "unlocode": "DE"
                }
            ]
        },
        "usage": "이 예제를 참고하여 국가를 검색하세요"
    }