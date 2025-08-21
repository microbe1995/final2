# ============================================================================
# 🧮 Calculation Service - CBAM 계산 비즈니스 로직
# ============================================================================

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from loguru import logger

from .calculation_repository import CalculationRepository
from .calculation_schema import (
    FuelCalculationRequest,
    FuelCalculationResponse,
    MaterialCalculationRequest,
    MaterialCalculationResponse,
    PrecursorData,
    PrecursorListRequest,
    PrecursorResponse,
    PrecursorListResponse,
    PrecursorSaveResponse,
    CBAmCalculationRequest,
    CBAMCalculationResponse,
    CalculationStatsResponse
)

class CalculationService:
    """계산 관련 비즈니스 로직을 처리하는 서비스 클래스"""
    
    def __init__(self, repository: Optional[CalculationRepository] = None):
        """CalculationService 초기화"""
        self.calc_repository = repository or CalculationRepository(use_database=True)
    
    # ============================================================================
    # 🔥 연료 계산 메서드
    # ============================================================================
    
    async def calculate_fuel_emission(self, request: FuelCalculationRequest) -> FuelCalculationResponse:
        """연료 배출량 계산"""
        try:
            logger.info(f"🔥 연료 배출량 계산 요청: {request.fuel_name} ({request.fuel_amount}톤)")
            
            # 연료 정보 조회
            fuel_data = await self.calc_repository.get_fuel_by_name(request.fuel_name)
            if not fuel_data:
                raise ValueError(f"해당 연료명을 찾을 수 없습니다: {request.fuel_name}")
            
            emission_factor = fuel_data.get("emission_factor", 0)
            net_calorific_value = fuel_data.get("net_calorific_value", 0)
            
            if emission_factor <= 0 or net_calorific_value <= 0:
                raise ValueError("DB에 배출계수 또는 순발열량 값이 올바르지 않습니다")
            
            # 배출량 계산: 연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3 (Gg→톤)
            emission = self._calculate_fuel_emission_amount(
                request.fuel_amount, net_calorific_value, emission_factor
            )
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="fuel",
                input_data=request.dict(),
                result_data={"emission": emission, "emission_factor": emission_factor, "net_calorific_value": net_calorific_value}
            )
            
            logger.info(f"✅ 연료 배출량 계산 성공: {emission} tCO2")
            
            return FuelCalculationResponse(
                emission=emission,
                fuel_name=fuel_data["fuel_type_description"],
                emission_factor=emission_factor,
                net_calorific_value=net_calorific_value
            )
            
        except Exception as e:
            logger.error(f"❌ 연료 배출량 계산 실패: {str(e)}")
            raise ValueError(f"연료 배출량 계산 중 오류가 발생했습니다: {str(e)}")
    
    async def search_fuels(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """연료 검색"""
        try:
            logger.info(f"🔍 연료 검색: '{search}'")
            fuels = await self.calc_repository.search_fuels(search, limit)
            logger.info(f"✅ 연료 검색 완료: {len(fuels)}개")
            return fuels
        except Exception as e:
            logger.error(f"❌ 연료 검색 실패: {str(e)}")
            raise ValueError(f"연료 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🧱 원료 계산 메서드
    # ============================================================================
    
    async def calculate_material_emission(self, request: MaterialCalculationRequest) -> MaterialCalculationResponse:
        """원료 배출량 계산"""
        try:
            logger.info(f"🧱 원료 배출량 계산 요청: {request.material_name} ({request.material_amount}톤)")
            
            # 원료 정보 조회
            material_data = await self.calc_repository.get_material_by_name(request.material_name)
            if not material_data:
                raise ValueError(f"해당 원료명을 찾을 수 없습니다: {request.material_name}")
            
            direct_factor = material_data.get("direct_factor")
            if direct_factor is None or direct_factor <= 0:
                raise ValueError("해당 원료의 직접배출계수가 없거나 올바르지 않습니다")
            
            # 배출량 계산: 원료량(톤) × 직접배출계수
            emission = self._calculate_material_emission_amount(request.material_amount, direct_factor)
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="material",
                input_data=request.dict(),
                result_data={"emission": emission, "direct_factor": direct_factor}
            )
            
            logger.info(f"✅ 원료 배출량 계산 성공: {emission} tCO2")
            
            return MaterialCalculationResponse(
                emission=emission,
                material_name=material_data["item_name"],
                direct_factor=direct_factor
            )
            
        except Exception as e:
            logger.error(f"❌ 원료 배출량 계산 실패: {str(e)}")
            raise ValueError(f"원료 배출량 계산 중 오류가 발생했습니다: {str(e)}")
    
    async def search_materials(self, search: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """원료 검색"""
        try:
            logger.info(f"🔍 원료 검색: '{search}'")
            materials = await self.calc_repository.search_materials(search, limit)
            logger.info(f"✅ 원료 검색 완료: {len(materials)}개")
            return materials
        except Exception as e:
            logger.error(f"❌ 원료 검색 실패: {str(e)}")
            raise ValueError(f"원료 검색 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔗 전구물질 관리 메서드
    # ============================================================================
    
    async def get_user_precursors(self, user_id: str) -> PrecursorListResponse:
        """사용자 전구물질 목록 조회"""
        try:
            logger.info(f"📋 사용자 전구물질 목록 조회: {user_id}")
            
            precursors = await self.calc_repository.get_precursors_by_user_id(user_id)
            precursor_responses = [self._convert_to_precursor_response(p) for p in precursors]
            
            logger.info(f"✅ 사용자 전구물질 목록 조회 성공: {len(precursors)}개")
            return PrecursorListResponse(precursors=precursor_responses, total=len(precursors))
            
        except Exception as e:
            logger.error(f"❌ 사용자 전구물질 목록 조회 실패: {str(e)}")
            raise ValueError(f"사용자 전구물질 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def save_precursors_batch(self, request: PrecursorListRequest) -> PrecursorSaveResponse:
        """전구물질 일괄 저장"""
        try:
            logger.info(f"📊 전구물질 일괄 저장: {len(request.precursors)}개")
            
            if not request.precursors:
                raise ValueError("저장할 전구물질 목록이 필요합니다")
            
            inserted_count = 0
            
            for precursor_data in request.precursors:
                try:
                    # CN코드 정보 보완
                    cn_codes = await self._enhance_cn_codes(
                        precursor_data.name, 
                        precursor_data.cn_code, 
                        precursor_data.cn_code1, 
                        precursor_data.cn_code2
                    )
                    
                    # 전구물질 데이터 준비
                    data = {
                        "user_id": precursor_data.user_id,
                        "name": precursor_data.name,
                        "name_en": precursor_data.name_en,
                        "cn_code": cn_codes["cn_code"],
                        "cn_code1": cn_codes["cn_code1"],
                        "cn_code2": cn_codes["cn_code2"],
                        "production_routes": precursor_data.production_routes,
                        "final_country_code": precursor_data.final_country_code
                    }
                    
                    # 전구물질 생성
                    await self.calc_repository.create_precursor(data)
                    inserted_count += 1
                    
                except Exception as item_error:
                    logger.error(f"❌ 개별 전구물질 저장 실패: {str(item_error)}")
                    continue
            
            logger.info(f"✅ 전구물질 일괄 저장 완료: {inserted_count}개")
            return PrecursorSaveResponse(
                inserted_count=inserted_count,
                message=f"{inserted_count}개의 전구물질이 성공적으로 저장되었습니다"
            )
            
        except Exception as e:
            logger.error(f"❌ 전구물질 일괄 저장 실패: {str(e)}")
            raise ValueError(f"전구물질 일괄 저장 중 오류가 발생했습니다: {str(e)}")
    
    async def delete_precursor(self, precursor_id: int, user_id: str) -> bool:
        """전구물질 삭제"""
        try:
            logger.info(f"🗑️ 전구물질 삭제: {precursor_id}")
            
            # 권한 확인
            precursor = await self.calc_repository.get_precursor_by_id(precursor_id)
            if not precursor:
                logger.warning(f"⚠️ 삭제할 전구물질을 찾을 수 없음: {precursor_id}")
                return False
            
            if precursor.get("user_id") != user_id:
                logger.warning(f"⚠️ 전구물질 삭제 권한 없음: {precursor_id}")
                return False
            
            # 전구물질 삭제
            deleted = await self.calc_repository.delete_precursor(precursor_id)
            
            if deleted:
                logger.info(f"✅ 전구물질 삭제 성공: {precursor_id}")
            else:
                logger.error(f"❌ 전구물질 삭제 실패: {precursor_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"❌ 전구물질 삭제 실패: {str(e)}")
            raise ValueError(f"전구물질 삭제 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🎯 CBAM 종합 계산 메서드
    # ============================================================================
    
    async def calculate_cbam_total(self, request: CBAmCalculationRequest) -> CBAMCalculationResponse:
        """CBAM 종합 배출량 계산"""
        try:
            logger.info(f"🎯 CBAM 종합 계산: {request.product_name}")
            
            # 연료 배출량 계산
            fuel_emissions = []
            total_fuel_emission = 0.0
            
            for fuel_data in request.fuels:
                try:
                    fuel_calc = await self.calculate_fuel_emission(
                        FuelCalculationRequest(fuel_name=fuel_data["name"], fuel_amount=fuel_data["amount"])
                    )
                    fuel_emissions.append({
                        "name": fuel_calc.fuel_name,
                        "amount": fuel_data["amount"],
                        "emission": fuel_calc.emission,
                        "emission_factor": fuel_calc.emission_factor
                    })
                    total_fuel_emission += fuel_calc.emission
                except Exception as e:
                    logger.warning(f"⚠️ 연료 계산 실패: {fuel_data.get('name')} - {str(e)}")
            
            # 원료 배출량 계산
            material_emissions = []
            total_material_emission = 0.0
            
            for material_data in request.materials:
                try:
                    material_calc = await self.calculate_material_emission(
                        MaterialCalculationRequest(material_name=material_data["name"], material_amount=material_data["amount"])
                    )
                    material_emissions.append({
                        "name": material_calc.material_name,
                        "amount": material_data["amount"],
                        "emission": material_calc.emission,
                        "direct_factor": material_calc.direct_factor
                    })
                    total_material_emission += material_calc.emission
                except Exception as e:
                    logger.warning(f"⚠️ 원료 계산 실패: {material_data.get('name')} - {str(e)}")
            
            # 전력 배출량 계산
            electricity_emission = None
            total_electricity_emission = 0.0
            
            if request.electricity:
                try:
                    electricity_amount = request.electricity.get("amount", 0)
                    electricity_factor = request.electricity.get("factor", 0)
                    elec_emission = electricity_amount * electricity_factor
                    
                    electricity_emission = {
                        "amount": electricity_amount,
                        "factor": electricity_factor,
                        "emission": elec_emission
                    }
                    total_electricity_emission = elec_emission
                except Exception as e:
                    logger.warning(f"⚠️ 전력 계산 실패: {str(e)}")
            
            # 전구물질 배출량 계산
            precursor_emissions = []
            total_precursor_emission = 0.0
            
            if request.product_type == "복합제품":
                for precursor_data in request.precursors:
                    try:
                        direct_emission = precursor_data.get("directEmission", 0)
                        precursor_emissions.append({
                            "name": precursor_data.get("name", ""),
                            "directEmission": direct_emission
                        })
                        total_precursor_emission += direct_emission
                    except Exception as e:
                        logger.warning(f"⚠️ 전구물질 계산 실패: {precursor_data.get('name')} - {str(e)}")
            
            # 총 배출량 계산
            total_direct_emission = total_fuel_emission + total_material_emission
            total_indirect_emission = total_electricity_emission
            total_emission = total_direct_emission + total_indirect_emission + total_precursor_emission
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id=request.user_id,
                calculation_type="cbam",
                input_data=request.dict(),
                result_data={
                    "total_emission": total_emission,
                    "total_direct_emission": total_direct_emission,
                    "total_indirect_emission": total_indirect_emission,
                    "total_precursor_emission": total_precursor_emission
                }
            )
            
            logger.info(f"✅ CBAM 종합 계산 성공: {total_emission} tCO2")
            
            return CBAMCalculationResponse(
                product_name=request.product_name,
                product_type=request.product_type,
                user_id=request.user_id,
                total_direct_emission=total_direct_emission,
                total_indirect_emission=total_indirect_emission,
                total_precursor_emission=total_precursor_emission,
                total_emission=total_emission,
                fuel_emissions=fuel_emissions,
                material_emissions=material_emissions,
                electricity_emission=electricity_emission,
                precursor_emissions=precursor_emissions,
                calculation_date=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ CBAM 종합 계산 실패: {str(e)}")
            raise ValueError(f"CBAM 종합 계산 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 📊 통계 메서드
    # ============================================================================
    
    async def get_calculation_stats(self) -> CalculationStatsResponse:
        """계산 통계 조회"""
        try:
            logger.info(f"📊 계산 통계 조회")
            stats = await self.calc_repository.get_calculation_stats()
            logger.info(f"✅ 계산 통계 조회 완료")
            return CalculationStatsResponse(
                total_calculations=stats.get("total_calculations", 0),
                fuel_calculations=stats.get("fuel_calculations", 0),
                material_calculations=stats.get("material_calculations", 0),
                total_precursors=stats.get("total_precursors", 0),
                active_users=stats.get("active_users", 0),
                calculations_by_type=stats.get("calculations_by_type", {}),
                last_updated=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"❌ 계산 통계 조회 실패: {str(e)}")
            raise ValueError(f"계산 통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    def _calculate_fuel_emission_amount(self, fuel_amount: float, net_calorific_value: float, emission_factor: float) -> float:
        """연료 배출량 계산 공식"""
        emission = fuel_amount * net_calorific_value * emission_factor * 1e-3
        return round(emission, 6)
    
    def _calculate_material_emission_amount(self, material_amount: float, direct_factor: float) -> float:
        """원료 배출량 계산 공식"""
        emission = material_amount * direct_factor * 1.0
        return round(emission, 6)
    
    async def _enhance_cn_codes(self, name: str, cn_code: str, cn_code1: str, cn_code2: str) -> Dict[str, str]:
        """CN코드 정보 보완"""
        if not cn_code or not cn_code1 or not cn_code2:
            material = await self.calc_repository.get_material_by_name(name)
            if material:
                return {
                    "cn_code": cn_code or material.get("cn_code", ""),
                    "cn_code1": cn_code1 or material.get("cn_code1", ""),
                    "cn_code2": cn_code2 or material.get("cn_code2", "")
                }
        
        return {
            "cn_code": cn_code or "",
            "cn_code1": cn_code1 or "",
            "cn_code2": cn_code2 or ""
        }
    
    def _convert_to_precursor_response(self, precursor: Dict[str, Any]) -> PrecursorResponse:
        """전구물질을 PrecursorResponse로 변환"""
        return PrecursorResponse(
            id=precursor["id"],
            user_id=precursor["user_id"],
            name=precursor["name"],
            name_en=precursor.get("name_en", ""),
            cn_code=precursor.get("cn_code", ""),
            cn_code1=precursor.get("cn_code1", ""),
            cn_code2=precursor.get("cn_code2", ""),
            production_routes=precursor.get("production_routes", []),
            final_country_code=precursor.get("final_country_code", ""),
            created_at=precursor.get("created_at", "")
        )
    
    async def _save_calculation_result(self, user_id: str, calculation_type: str, input_data: Dict[str, Any], result_data: Dict[str, Any]) -> None:
        """계산 결과 저장"""
        try:
            result_info = {
                "user_id": user_id,
                "calculation_type": calculation_type,
                "input_data": input_data,
                "result_data": result_data
            }
            await self.calc_repository.save_calculation_result(result_info)
        except Exception as e:
            logger.warning(f"⚠️ 계산 결과 저장 실패: {str(e)}")
            # 계산 결과 저장 실패는 전체 계산을 중단시키지 않음