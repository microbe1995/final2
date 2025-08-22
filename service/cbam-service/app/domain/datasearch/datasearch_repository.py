# ============================================================================
# 🔍 DataSearch Repository - CBAM 데이터 검색 저장소
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DataSearchRepository:
    """데이터 검색 저장소 클래스"""
    
    def __init__(self, use_database: bool = False):
        self.use_database = use_database
        self._memory_data = self._initialize_memory_data() if not use_database else {}
        self._search_logs: List[Dict[str, Any]] = []
        
        if self.use_database:
            logger.info("✅ PostgreSQL 데이터 검색 저장소 사용")
        else:
            logger.info("✅ 메모리 데이터 검색 저장소 사용")
    
    # ============================================================================
    # 📊 HS코드 검색 메서드
    # ============================================================================
    
    async def search_hscode(self, hs: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """HS코드 검색"""
        try:
            if self.use_database:
                return await self._search_hscode_db(hs, page, page_size)
            else:
                return self._search_hscode_memory(hs, page, page_size)
        except Exception as e:
            logger.error(f"❌ HS코드 검색 실패: {str(e)}")
            return {"results": [], "total": 0, "page": page, "page_size": page_size}
    
    async def _search_hscode_db(self, hs: str, page: int, page_size: int) -> Dict[str, Any]:
        """PostgreSQL에서 HS코드 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_hscode_memory(hs, page, page_size)
    
    def _search_hscode_memory(self, hs: str, page: int, page_size: int) -> Dict[str, Any]:
        """메모리에서 HS코드 검색"""
        results = []
        if hs and hs.isdigit():
            for item in self._memory_data.get("hscode", []):
                if str(item.get("hs_코드", "")).startswith(hs):
                    results.append(item)
        else:
            results = self._memory_data.get("hscode", [])
        
        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = results[start:end]
        
        # 검색 로그
        self._log_search(search_type="hscode", search_term=hs, result_count=len(results))
        
        return {
            "results": paginated_results,
            "total": len(results),
            "page": page,
            "page_size": page_size
        }
    
    # ============================================================================
    # 🌍 국가 검색 메서드
    # ============================================================================
    
    async def search_country(self, name_kr: str) -> List[Dict[str, Any]]:
        """국가 검색"""
        try:
            if self.use_database:
                return await self._search_country_db(name_kr)
            else:
                return self._search_country_memory(name_kr)
        except Exception as e:
            logger.error(f"❌ 국가 검색 실패: {str(e)}")
            return []
    
    async def _search_country_db(self, name_kr: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 국가 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_country_memory(name_kr)
    
    def _search_country_memory(self, name_kr: str) -> List[Dict[str, Any]]:
        """메모리에서 국가 검색"""
        results = []
        for country in self._memory_data.get("countries", []):
            if name_kr.lower() in country.get("name_kr", "").lower():
                results.append(country)
        
        # 검색 로그
        self._log_search(search_type="country", search_term=name_kr, result_count=len(results))
        
        return results
    
    # ============================================================================
    # 🔥 연료 검색 메서드
    # ============================================================================
    
    async def search_fuels(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """연료 검색"""
        try:
            if self.use_database:
                return await self._search_fuels_db(search, limit)
            else:
                return self._search_fuels_memory(search, limit)
        except Exception as e:
            logger.error(f"❌ 연료 검색 실패: {str(e)}")
            return []
    
    async def _search_fuels_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 연료 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_fuels_memory(search, limit)
    
    def _search_fuels_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 연료 검색"""
        results = []
        for fuel in self._memory_data.get("fuels", []):
            if not search or search.lower() in fuel.get("name", "").lower() or search.lower() in fuel.get("name_eng", "").lower():
                results.append(fuel)
                if len(results) >= limit:
                    break
        
        # 검색 로그
        self._log_search(search_type="fuel", search_term=search, result_count=len(results))
        
        return results
    
    # ============================================================================
    # 🧱 원료 검색 메서드
    # ============================================================================
    
    async def search_materials(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """원료 검색"""
        try:
            if self.use_database:
                return await self._search_materials_db(search, limit)
            else:
                return self._search_materials_memory(search, limit)
        except Exception as e:
            logger.error(f"❌ 원료 검색 실패: {str(e)}")
            return []
    
    async def _search_materials_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 원료 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_materials_memory(search, limit)
    
    def _search_materials_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 원료 검색"""
        results = []
        for material in self._memory_data.get("materials", []):
            if not search or search.lower() in material.get("name", "").lower() or search.lower() in material.get("name_eng", "").lower():
                results.append(material)
                if len(results) >= limit:
                    break
        
        # 검색 로그
        self._log_search(search_type="material", search_term=search, result_count=len(results))
        
        return results
    
    # ============================================================================
    # 🔗 전구물질 검색 메서드
    # ============================================================================
    
    async def search_precursors(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """전구물질 검색"""
        try:
            if self.use_database:
                return await self._search_precursors_db(search, limit)
            else:
                return self._search_precursors_memory(search, limit)
        except Exception as e:
            logger.error(f"❌ 전구물질 검색 실패: {str(e)}")
            return []
    
    async def _search_precursors_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 전구물질 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_precursors_memory(search, limit)
    
    def _search_precursors_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 전구물질 검색"""
        results = []
        for precursor in self._memory_data.get("precursors", []):
            if not search or search.lower() in precursor.get("name", "").lower():
                results.append(precursor)
                if len(results) >= limit:
                    break
        
        # 검색 로그
        self._log_search(search_type="precursor", search_term=search, result_count=len(results))
        
        return results
    
    # ============================================================================
    # 📊 통계 및 로그 메서드
    # ============================================================================
    
    async def log_search_activity(self, search_type: str, search_term: str, result_count: int) -> None:
        """검색 활동 로그"""
        self._log_search(search_type, search_term, result_count)
    
    async def get_search_stats(self) -> Dict[str, Any]:
        """검색 통계 조회"""
        try:
            total_searches = len(self._search_logs)
            
            searches_by_type = {}
            for log in self._search_logs:
                search_type = log.get("search_type", "unknown")
                searches_by_type[search_type] = searches_by_type.get(search_type, 0) + 1
            
            return {
                "total_searches": total_searches,
                "hscode_searches": searches_by_type.get("hscode", 0),
                "country_searches": searches_by_type.get("country", 0),
                "fuel_searches": searches_by_type.get("fuel", 0),
                "material_searches": searches_by_type.get("material", 0),
                "precursor_searches": searches_by_type.get("precursor", 0),
                "searches_by_type": searches_by_type,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 검색 통계 조회 실패: {str(e)}")
            return {}
    
    def _log_search(self, search_type: str, search_term: str, result_count: int) -> None:
        """검색 로그 기록"""
        log_entry = {
            "search_type": search_type,
            "search_term": search_term,
            "result_count": result_count,
            "timestamp": datetime.now().isoformat()
        }
        self._search_logs.append(log_entry)
    
    # ============================================================================
    # 🔧 초기화 및 유틸리티 메서드
    # ============================================================================
    
    def _initialize_memory_data(self) -> Dict[str, Any]:
        """메모리 저장소 샘플 데이터 초기화"""
        return {
            "hscode": [
                {
                    "id": 1,
                    "hs_코드": 720810,
                    "cn_검증용": 720810,
                    "품목군__(cn기준)": "철강",
                    "품목_(cn기준)": "평판압연제품",
                    "품목_(cn기준_영문)": "Flat-rolled products",
                    "cn_코드": "7208",
                    "배출계수": 1.89,
                    "탄소함량": 0.5
                },
                {
                    "id": 2,
                    "hs_코드": 720825,
                    "cn_검증용": 720825,
                    "품목군__(cn기준)": "철강",
                    "품목_(cn기준)": "평판압연제품",
                    "품목_(cn기준_영문)": "Flat-rolled products",
                    "cn_코드": "7208",
                    "배출계수": 1.92,
                    "탄소함량": 0.5
                }
            ],
            "countries": [
                {"country_name": "South Korea", "name_kr": "대한민국", "code": "KR"},
                {"country_name": "China", "name_kr": "중국", "code": "CN"},
                {"country_name": "Japan", "name_kr": "일본", "code": "JP"},
                {"country_name": "United States", "name_kr": "미국", "code": "US"},
                {"country_name": "Germany", "name_kr": "독일", "code": "DE"}
            ],
            "fuels": [
                {"id": 1, "name": "천연가스", "name_eng": "Natural Gas", "fuel_emfactor": 56.1, "net_calory": 48.0},
                {"id": 2, "name": "석탄", "name_eng": "Coal", "fuel_emfactor": 94.6, "net_calory": 25.8},
                {"id": 3, "name": "중유", "name_eng": "Heavy Oil", "fuel_emfactor": 77.4, "net_calory": 40.4},
                {"id": 4, "name": "경유", "name_eng": "Light Oil", "fuel_emfactor": 74.1, "net_calory": 43.0}
            ],
            "materials": [
                {"id": 1, "name": "철광석", "name_eng": "Iron Ore", "em_factor": 0.024, "carbon_factor": 0.5, "cn_code": "2601", "cn_code1": "260111", "cn_code2": "26011100"},
                {"id": 2, "name": "석회석", "name_eng": "Limestone", "em_factor": 0.034, "carbon_factor": 12.0, "cn_code": "2521", "cn_code1": "252100", "cn_code2": "25210000"},
                {"id": 3, "name": "코크스", "name_eng": "Coke", "em_factor": 3.2, "carbon_factor": 85.0, "cn_code": "2704", "cn_code1": "270400", "cn_code2": "27040010"},
                {"id": 4, "name": "스크랩", "name_eng": "Scrap", "em_factor": 0.01, "carbon_factor": 0.1, "cn_code": "7204", "cn_code1": "720410", "cn_code2": "72041000"}
            ],
            "precursors": [
                {"id": 1, "precursor": "펠릿", "precursor_eng": "Pellet", "direct": 0.15, "indirect": 0.08, "cn1": "2601"},
                {"id": 2, "precursor": "소결광", "precursor_eng": "Sinter", "direct": 0.12, "indirect": 0.06, "cn1": "2601"},
                {"id": 3, "precursor": "괴광석", "precursor_eng": "Lump Ore", "direct": 0.024, "indirect": 0.012, "cn1": "2601"},
                {"id": 4, "precursor": "분광석", "precursor_eng": "Fine Ore", "direct": 0.018, "indirect": 0.009, "cn1": "2601"}
            ]
        }