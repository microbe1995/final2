# ============================================================================
# 🧮 Calculation Repository - CBAM 계산 데이터 접근
# ============================================================================

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CalculationRepository:
    """계산 데이터 접근 클래스"""
    
    def __init__(self, use_database: bool = True):
        self.use_database = use_database
        self._memory_fuels: Dict[str, Dict[str, Any]] = {}
        self._memory_materials: Dict[str, Dict[str, Any]] = {}
        self._memory_precursors: Dict[int, Dict[str, Any]] = {}
        self._memory_results: Dict[int, Dict[str, Any]] = {}
        
        if self.use_database:
            logger.info("✅ PostgreSQL 계산 저장소 사용")
        else:
            logger.info("✅ 메모리 계산 저장소 사용")
            self._initialize_memory_data()
    
    # ============================================================================
    # 🔥 연료 관련 메서드
    # ============================================================================
    
    async def get_fuel_by_name(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """연료명으로 연료 정보 조회"""
        try:
            if self.use_database:
                return await self._get_fuel_by_name_db(fuel_name)
            else:
                return self._get_fuel_by_name_memory(fuel_name)
        except Exception as e:
            logger.error(f"❌ 연료 조회 실패: {str(e)}")
            return None
    
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
    
    async def _get_fuel_by_name_db(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 연료명으로 조회"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._get_fuel_by_name_memory(fuel_name)
    
    async def _search_fuels_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 연료 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_fuels_memory(search, limit)
    
    def _get_fuel_by_name_memory(self, fuel_name: str) -> Optional[Dict[str, Any]]:
        """메모리에서 연료명으로 조회"""
        for fuel in self._memory_fuels.values():
            if fuel_name.lower() in fuel["fuel_name"].lower():
                return fuel
        return None
    
    def _search_fuels_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 연료 검색"""
        results = []
        for fuel in self._memory_fuels.values():
            if not search or search.lower() in fuel["fuel_name"].lower():
                results.append(fuel)
                if len(results) >= limit:
                    break
        return results
    
    # ============================================================================
    # 🧱 원료 관련 메서드
    # ============================================================================
    
    async def get_material_by_name(self, material_name: str) -> Optional[Dict[str, Any]]:
        """원료명으로 원료 정보 조회"""
        try:
            if self.use_database:
                return await self._get_material_by_name_db(material_name)
            else:
                return self._get_material_by_name_memory(material_name)
        except Exception as e:
            logger.error(f"❌ 원료 조회 실패: {str(e)}")
            return None
    
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
    
    async def _get_material_by_name_db(self, material_name: str) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 원료명으로 조회"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._get_material_by_name_memory(material_name)
    
    async def _search_materials_db(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """PostgreSQL에서 원료 검색"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._search_materials_memory(search, limit)
    
    def _get_material_by_name_memory(self, material_name: str) -> Optional[Dict[str, Any]]:
        """메모리에서 원료명으로 조회"""
        for material in self._memory_materials.values():
            if material_name.lower() in material["item_name"].lower():
                return material
        return None
    
    def _search_materials_memory(self, search: str, limit: int) -> List[Dict[str, Any]]:
        """메모리에서 원료 검색"""
        results = []
        for material in self._memory_materials.values():
            if not search or search.lower() in material["item_name"].lower():
                results.append(material)
                if len(results) >= limit:
                    break
        return results
    
    # ============================================================================
    # 🔗 전구물질 관련 메서드
    # ============================================================================
    
    async def create_precursor(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """전구물질 생성"""
        try:
            if self.use_database:
                return await self._create_precursor_db(precursor_data)
            else:
                return self._create_precursor_memory(precursor_data)
        except Exception as e:
            logger.error(f"❌ 전구물질 생성 실패: {str(e)}")
            raise
    
    async def get_precursor_by_id(self, precursor_id: int) -> Optional[Dict[str, Any]]:
        """전구물질 ID로 조회"""
        try:
            if self.use_database:
                return await self._get_precursor_by_id_db(precursor_id)
            else:
                return self._memory_precursors.get(precursor_id)
        except Exception as e:
            logger.error(f"❌ 전구물질 조회 실패: {str(e)}")
            return None
    
    async def get_precursors_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자 ID로 전구물질 목록 조회"""
        try:
            if self.use_database:
                return await self._get_precursors_by_user_id_db(user_id)
            else:
                return [p for p in self._memory_precursors.values() if p.get("user_id") == user_id]
        except Exception as e:
            logger.error(f"❌ 사용자별 전구물질 조회 실패: {str(e)}")
            return []
    
    async def delete_precursor(self, precursor_id: int) -> bool:
        """전구물질 삭제"""
        try:
            if self.use_database:
                return await self._delete_precursor_db(precursor_id)
            else:
                return self._delete_precursor_memory(precursor_id)
        except Exception as e:
            logger.error(f"❌ 전구물질 삭제 실패: {str(e)}")
            return False
    
    async def _create_precursor_db(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 전구물질 생성"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._create_precursor_memory(precursor_data)
    
    async def _get_precursor_by_id_db(self, precursor_id: int) -> Optional[Dict[str, Any]]:
        """PostgreSQL에서 전구물질 ID로 조회"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._memory_precursors.get(precursor_id)
    
    async def _get_precursors_by_user_id_db(self, user_id: str) -> List[Dict[str, Any]]:
        """PostgreSQL에서 사용자별 전구물질 조회"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return [p for p in self._memory_precursors.values() if p.get("user_id") == user_id]
    
    async def _delete_precursor_db(self, precursor_id: int) -> bool:
        """PostgreSQL에서 전구물질 삭제"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._delete_precursor_memory(precursor_id)
    
    def _create_precursor_memory(self, precursor_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 전구물질 생성"""
        precursor_id = len(self._memory_precursors) + 1
        precursor = {
            **precursor_data,
            "id": precursor_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self._memory_precursors[precursor_id] = precursor
        
        logger.info(f"✅ 메모리 전구물질 생성: {precursor_id}")
        return precursor
    
    def _delete_precursor_memory(self, precursor_id: int) -> bool:
        """메모리에서 전구물질 삭제"""
        if precursor_id in self._memory_precursors:
            del self._memory_precursors[precursor_id]
            logger.info(f"✅ 메모리 전구물질 삭제 성공: {precursor_id}")
            return True
        else:
            logger.warning(f"⚠️ 메모리 전구물질 삭제 실패: 전구물질을 찾을 수 없음 {precursor_id}")
            return False
    
    # ============================================================================
    # 📊 계산 결과 및 통계 메서드
    # ============================================================================
    
    async def save_calculation_result(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """계산 결과 저장"""
        try:
            if self.use_database:
                return await self._save_calculation_result_db(result_data)
            else:
                return self._save_calculation_result_memory(result_data)
        except Exception as e:
            logger.error(f"❌ 계산 결과 저장 실패: {str(e)}")
            raise
    
    async def get_calculation_stats(self) -> Dict[str, Any]:
        """계산 통계 조회"""
        try:
            if self.use_database:
                return await self._get_calculation_stats_db()
            else:
                return self._get_calculation_stats_memory()
        except Exception as e:
            logger.error(f"❌ 계산 통계 조회 실패: {str(e)}")
            return {}
    
    async def _save_calculation_result_db(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """PostgreSQL에 계산 결과 저장"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._save_calculation_result_memory(result_data)
    
    async def _get_calculation_stats_db(self) -> Dict[str, Any]:
        """PostgreSQL에서 계산 통계 조회"""
        # TODO: PostgreSQL 연결 구현
        logger.warning("PostgreSQL 연결이 구현되지 않음. 메모리 데이터 사용")
        return self._get_calculation_stats_memory()
    
    def _save_calculation_result_memory(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에 계산 결과 저장"""
        result_id = len(self._memory_results) + 1
        result = {
            **result_data,
            "id": result_id,
            "created_at": datetime.utcnow().isoformat()
        }
        self._memory_results[result_id] = result
        return result
    
    def _get_calculation_stats_memory(self) -> Dict[str, Any]:
        """메모리에서 계산 통계 조회"""
        total_calculations = len(self._memory_results)
        fuel_calculations = len([r for r in self._memory_results.values() if r.get("calculation_type") == "fuel"])
        material_calculations = len([r for r in self._memory_results.values() if r.get("calculation_type") == "material"])
        total_precursors = len(self._memory_precursors)
        
        user_ids = set(r.get("user_id") for r in self._memory_results.values())
        active_users = len(user_ids)
        
        calculations_by_type = {}
        for result in self._memory_results.values():
            calc_type = result.get("calculation_type", "unknown")
            calculations_by_type[calc_type] = calculations_by_type.get(calc_type, 0) + 1
        
        return {
            "total_calculations": total_calculations,
            "fuel_calculations": fuel_calculations,
            "material_calculations": material_calculations,
            "total_precursors": total_precursors,
            "active_users": active_users,
            "calculations_by_type": calculations_by_type
        }
    
    # ============================================================================
    # 🔧 초기화 및 유틸리티 메서드
    # ============================================================================
    
    def _initialize_memory_data(self):
        """메모리 저장소 샘플 데이터 초기화"""
        # 샘플 연료 데이터
        self._memory_fuels = {
            "천연가스": {
                "id": 1,
                "fuel_name": "천연가스",
                "fuel_eng": "Natural Gas",
                "fuel_emfactor": 56.1,
                "net_calory": 48.0
            },
            "석탄": {
                "id": 2,
                "fuel_name": "석탄",
                "fuel_eng": "Coal",
                "fuel_emfactor": 94.6,
                "net_calory": 25.8
            },
            "중유": {
                "id": 3,
                "fuel_name": "중유",
                "fuel_eng": "Heavy Oil",
                "fuel_emfactor": 77.4,
                "net_calory": 40.4
            }
        }
        
        # 샘플 원료 데이터
        self._memory_materials = {
            "철광석": {
                "id": 1,
                "item_name": "철광석",
                "item_eng": "Iron Ore",
                "carbon_factor": 0.5,  # 탄소함량 (%)
                "em_factor": 0.024,  # 배출계수 (tCO2/톤)
                "cn_code": "2601",
                "cn_code1": "260111",
                "cn_code2": "26011100"
            },
            "석회석": {
                "id": 2,
                "item_name": "석회석",
                "item_eng": "Limestone",
                "carbon_factor": 12.0,  # 탄소함량 (%)
                "em_factor": 0.034,  # 배출계수 (tCO2/톤)
                "cn_code": "2521",
                "cn_code1": "252100",
                "cn_code2": "25210000"
            }
        }
        
        logger.info("✅ 메모리 저장소 샘플 데이터 초기화 완료")