# ============================================================================
# 🔍 DataSearch Service - CBAM 데이터 검색 비즈니스 로직
# ============================================================================

from typing import List, Optional, Dict, Any
from loguru import logger

from .datasearch_repository import DataSearchRepository
from .datasearch_schema import (
    HSCodeSearchResponse,
    CountrySearchRequest,
    CountrySearchResponse,
    FuelSearchResponse,
    MaterialSearchResponse,
    PrecursorSearchResponse,
    CountryData,
    FuelData,
    MaterialData,
    PrecursorData,
    SearchStatsResponse
)

class DataSearchService:
    """데이터 검색 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[DataSearchRepository] = None):
        """DataSearchService 초기화"""
        self.datasearch_repository = repository or DataSearchRepository(use_database=False)
    
    # ============================================================================
    # 📊 HS코드 검색 메서드
    # ============================================================================
    
    async def search_hscode(self, hs: str, page: int = 1, page_size: int = 5) -> HSCodeSearchResponse:
        """HS코드 검색"""
        try:
            logger.info(f"📊 HS코드 검색: '{hs}' (페이지: {page})")
            
            result = await self.datasearch_repository.search_hscode(hs, page, page_size)
            
            logger.info(f"✅ HS코드 검색 완료: {len(result.get('results', []))}개")
            return HSCodeSearchResponse(**result)
            
        except Exception as e:
            logger.error(f"❌ HS코드 검색 실패: {str(e)}")
            raise ValueError(f"HS코드 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🌍 국가 검색 메서드
    # ============================================================================
    
    async def search_country(self, request: CountrySearchRequest) -> CountrySearchResponse:
        """국가 검색"""
        try:
            logger.info(f"🌍 국가 검색: '{request.name_kr}'")
            
            countries = await self.datasearch_repository.search_country(request.name_kr)
            
            # CountryData 형식으로 변환
            country_data = [
                CountryData(
                    name_en=country.get("country_name", ""),
                    name_kr=country.get("name_kr", ""),
                    unlocode=country.get("code", "")
                )
                for country in countries
            ]
            
            logger.info(f"✅ 국가 검색 완료: {len(country_data)}개")
            return CountrySearchResponse(result=country_data)
            
        except Exception as e:
            logger.error(f"❌ 국가 검색 실패: {str(e)}")
            raise ValueError(f"국가 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔥 연료 검색 메서드
    # ============================================================================
    
    async def search_fuels(self, search: str = "", limit: int = 50) -> FuelSearchResponse:
        """연료 검색"""
        try:
            logger.info(f"🔥 연료 검색: '{search}'")
            
            fuels_data = await self.datasearch_repository.search_fuels(search, limit)
            
            # FuelData 형식으로 변환
            fuels = [
                FuelData(
                    id=fuel.get("id", 0),
                    name=fuel.get("name", ""),
                    name_eng=fuel.get("name_eng", ""),
                    fuel_emfactor=fuel.get("fuel_emfactor", 0.0),
                    net_calory=fuel.get("net_calory", 0.0)
                )
                for fuel in fuels_data
            ]
            
            logger.info(f"✅ 연료 검색 완료: {len(fuels)}개")
            return FuelSearchResponse(fuels=fuels)
            
        except Exception as e:
            logger.error(f"❌ 연료 검색 실패: {str(e)}")
            raise ValueError(f"연료 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🧱 원료 검색 메서드
    # ============================================================================
    
    async def search_materials(self, search: str = "", limit: int = 50) -> MaterialSearchResponse:
        """원료 검색"""
        try:
            logger.info(f"🧱 원료 검색: '{search}'")
            
            materials_data = await self.datasearch_repository.search_materials(search, limit)
            
            # MaterialData 형식으로 변환
            materials = [
                MaterialData(
                    id=material.get("id", 0),
                    name=material.get("name", ""),
                    name_eng=material.get("name_eng", ""),
                    em_factor=material.get("em_factor"),
                    carbon_factor=material.get("carbon_factor", 0.0),
                    cn_code=material.get("cn_code", ""),
                    cn_code1=material.get("cn_code1", ""),
                    cn_code2=material.get("cn_code2", "")
                )
                for material in materials_data
            ]
            
            logger.info(f"✅ 원료 검색 완료: {len(materials)}개")
            return MaterialSearchResponse(materials=materials)
            
        except Exception as e:
            logger.error(f"❌ 원료 검색 실패: {str(e)}")
            raise ValueError(f"원료 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔗 전구물질 검색 메서드
    # ============================================================================
    
    async def search_precursors(self, search: str = "", limit: int = 50) -> PrecursorSearchResponse:
        """전구물질 검색"""
        try:
            logger.info(f"🔗 전구물질 검색: '{search}'")
            
            precursors_data = await self.datasearch_repository.search_precursors(search, limit)
            
            # PrecursorData 형식으로 변환
            precursors = [
                PrecursorData(
                    id=precursor.get("id", 0),
                    precursor=precursor.get("precursor", ""),
                    precursor_eng=precursor.get("precursor_eng", ""),
                    direct=precursor.get("direct", 0.0),
                    indirect=precursor.get("indirect", 0.0),
                    cn1=precursor.get("cn1", "")
                )
                for precursor in precursors_data
            ]
            
            logger.info(f"✅ 전구물질 검색 완료: {len(precursors)}개")
            return PrecursorSearchResponse(precursors=precursors)
            
        except Exception as e:
            logger.error(f"❌ 전구물질 검색 실패: {str(e)}")
            raise ValueError(f"전구물질 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 📊 통계 메서드
    # ============================================================================
    
    async def get_search_stats(self) -> SearchStatsResponse:
        """검색 통계 조회"""
        try:
            logger.info(f"📊 검색 통계 조회")
            
            stats = await self.datasearch_repository.get_search_stats()
            
            logger.info(f"✅ 검색 통계 조회 완료")
            return SearchStatsResponse(
                total_searches=stats.get("total_searches", 0),
                hscode_searches=stats.get("hscode_searches", 0),
                country_searches=stats.get("country_searches", 0),
                fuel_searches=stats.get("fuel_searches", 0),
                material_searches=stats.get("material_searches", 0),
                precursor_searches=stats.get("precursor_searches", 0),
                searches_by_type=stats.get("searches_by_type", {}),
                last_updated=stats.get("last_updated", "")
            )
            
        except Exception as e:
            logger.error(f"❌ 검색 통계 조회 실패: {str(e)}")
            raise ValueError(f"검색 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    async def _log_search_activity(self, search_type: str, search_term: str, result_count: int) -> None:
        """검색 활동 로그"""
        try:
            await self.datasearch_repository.log_search_activity(search_type, search_term, result_count)
        except Exception as e:
            logger.warning(f"⚠️ 검색 활동 로그 실패: {str(e)}")
            # 로그 실패는 전체 검색을 중단시키지 않음