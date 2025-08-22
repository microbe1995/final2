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
    PrecursorCalculationRequest,
    PrecursorCalculationResponse,
    PrecursorData,
    PrecursorListRequest,
    PrecursorResponse,
    PrecursorListResponse,
    PrecursorSaveResponse,
    ElectricityCalculationRequest,
    ElectricityCalculationResponse,
    ProductionProcess,
    CBAmCalculationRequest,
    CBAMCalculationResponse,
    CalculationStatsResponse,
    BoundaryCreateRequest,
    BoundaryResponse,
    ProductCreateRequest,
    ProductResponse,
    OperationCreateRequest,
    OperationResponse,
    NodeCreateRequest,
    NodeResponse,
    EdgeCreateRequest,
    EdgeResponse,
    ProductionEmissionCreateRequest,
    ProductionEmissionResponse
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
                raise ValueError(f"연료 '{request.fuel_name}'을 찾을 수 없습니다")
            
            # 배출계수와 순발열량 확인
            fuel_emfactor = fuel_data.get("fuel_emfactor")
            net_calory = fuel_data.get("net_calory")
            
            if fuel_emfactor is None or fuel_emfactor <= 0:
                raise ValueError(f"연료 '{request.fuel_name}'의 배출계수가 유효하지 않습니다")
            
            if net_calory is None or net_calory <= 0:
                raise ValueError(f"연료 '{request.fuel_name}'의 순발열량이 유효하지 않습니다")
            
            # 배출량 계산: 연료량(톤) × 순발열량(TJ/Gg) × 배출계수(tCO2/TJ) × 1e-3
            emission = self._calculate_fuel_emission_amount(request.fuel_amount, net_calory, fuel_emfactor)
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="fuel",
                input_data=request.dict(),
                result_data={"emission": emission, "fuel_emfactor": fuel_emfactor, "net_calory": net_calory}
            )
            
            logger.info(f"✅ 연료 배출량 계산 성공: {emission} tCO2")
            
            return FuelCalculationResponse(
                emission=emission,
                fuel_name=request.fuel_name,
                fuel_emfactor=fuel_emfactor,
                net_calory=net_calory
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
                raise ValueError(f"원료 '{request.material_name}'을 찾을 수 없습니다")
            
            # 배출계수 확인
            em_factor = material_data.get("em_factor")
            if em_factor is None or em_factor <= 0:
                raise ValueError(f"원료 '{request.material_name}'의 배출계수가 유효하지 않습니다")
            
            # 배출량 계산
            emission = self._calculate_material_emission_amount(request.material_amount, em_factor)
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="material",
                input_data=request.dict(),
                result_data={"emission": emission, "em_factor": em_factor}
            )
            
            logger.info(f"✅ 원료 배출량 계산 성공: {emission} tCO2")
            
            return MaterialCalculationResponse(
                emission=emission,
                material_name=request.material_name,
                em_factor=em_factor
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
            
            for precursor in request.precursors:
                try:
                    # CN코드 정보 보완
                    cn_codes = await self._enhance_cn_codes(
                        precursor.name, 
                        precursor.cn_code, 
                        precursor.cn_code1, 
                        precursor.cn_code2
                    )
                    
                    # 전구물질 데이터 생성
                    precursor_data = {
                        "user_id": precursor.user_id,
                        "precursor": precursor.precursor,
                        "precursor_eng": precursor.precursor_eng,
                        "cn1": precursor.cn1,
                        "cn2": precursor.cn2,
                        "cn3": precursor.cn3,
                        "direct": precursor.direct,
                        "indirect": precursor.indirect,
                        "final_country_code": precursor.final_country_code
                    }
                    
                    # 전구물질 생성
                    await self.calc_repository.create_precursor(precursor_data)
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
    # 🔬 전구물질 계산 메서드
    # ============================================================================
    
    async def calculate_precursor_emission(self, request: PrecursorCalculationRequest) -> PrecursorCalculationResponse:
        """전구물질 배출량 계산"""
        try:
            logger.info(f"🔬 전구물질 배출량 계산 요청: {request.precursor_name} ({request.precursor_amount}톤)")
            
            # 배출량 계산: 전구물질량(톤) × (직접배출계수 + 간접배출계수)
            total_factor = request.direct + request.indirect
            emission = request.precursor_amount * total_factor
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="precursor",
                input_data=request.dict(),
                result_data={"emission": emission, "direct": request.direct, "indirect": request.indirect}
            )
            
            logger.info(f"✅ 전구물질 배출량 계산 성공: {emission} tCO2")
            
            return PrecursorCalculationResponse(
                emission=emission,
                precursor_name=request.precursor_name,
                direct=request.direct,
                indirect=request.indirect
            )
            
        except Exception as e:
            logger.error(f"❌ 전구물질 배출량 계산 실패: {str(e)}")
            raise ValueError(f"전구물질 배출량 계산 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # ⚡ 전력 사용 배출량 계산 메서드
    # ============================================================================
    
    async def calculate_electricity_emission(self, request: ElectricityCalculationRequest) -> ElectricityCalculationResponse:
        """전력 사용 배출량 계산"""
        try:
            logger.info(f"⚡ 전력 사용 배출량 계산 요청: {request.power_usage} MWh")
            
            # 배출량 계산: 전력사용량(MWh) × 배출계수(tCO2/MWh)
            emission = request.power_usage * request.emission_factor
            
            # 계산 결과 저장
            await self._save_calculation_result(
                user_id="system",
                calculation_type="electricity",
                input_data=request.dict(),
                result_data={"emission": emission, "emission_factor": request.emission_factor}
            )
            
            logger.info(f"✅ 전력 사용 배출량 계산 성공: {emission} tCO2")
            
            return ElectricityCalculationResponse(
                emission=emission,
                power_usage=request.power_usage,
                emission_factor=request.emission_factor
            )
            
        except Exception as e:
            logger.error(f"❌ 전력 사용 배출량 계산 실패: {str(e)}")
            raise ValueError(f"전력 사용 배출량 계산 중 오류가 발생했습니다: {str(e)}")
    
    # ============================================================================
    # 🏭 생산 공정 계산 메서드
    # ============================================================================
    
    async def calculate_process_emissions(self, processes: List[ProductionProcess]) -> List[ProductionProcess]:
        """생산 공정별 배출량 계산"""
        try:
            logger.info(f"🏭 생산 공정별 배출량 계산: {len(processes)}개 공정")
            
            calculated_processes = []
            
            for process in processes:
                # 직접 배출량 계산 (연료 + 원료)
                direct_emission = 0.0
                if process.input_fuel_amount > 0 and process.input_fuel_name:
                    try:
                        fuel_calc = await self.calculate_fuel_emission(
                            FuelCalculationRequest(fuel_name=process.input_fuel_name, fuel_amount=process.input_fuel_amount)
                        )
                        direct_emission += fuel_calc.emission
                    except Exception as e:
                        logger.warning(f"⚠️ 공정 연료 계산 실패: {process.process_name} - {str(e)}")
                
                if process.input_material_amount > 0 and process.input_material_name:
                    try:
                        material_calc = await self.calculate_material_emission(
                            MaterialCalculationRequest(material_name=process.input_material_name, material_amount=process.input_material_amount)
                        )
                        direct_emission += material_calc.emission
                    except Exception as e:
                        logger.warning(f"⚠️ 공정 원료 계산 실패: {process.process_name} - {str(e)}")
                
                # 간접 배출량 계산 (전력)
                indirect_emission = 0.0
                if process.power_usage > 0:
                    try:
                        electricity_calc = await self.calculate_electricity_emission(
                            ElectricityCalculationRequest(power_usage=process.power_usage)
                        )
                        indirect_emission = electricity_calc.emission
                    except Exception as e:
                        logger.warning(f"⚠️ 공정 전력 계산 실패: {process.process_name} - {str(e)}")
                
                # 전구물질 배출량 (복합제품의 경우에만)
                precursor_emission = process.precursor_emission  # 이미 입력된 값 사용
                
                # 총 배출량 계산
                total_emission = direct_emission + indirect_emission + precursor_emission
                
                # 업데이트된 공정 정보
                updated_process = ProductionProcess(
                    process_order=process.process_order,
                    process_name=process.process_name,
                    start_date=process.start_date,
                    end_date=process.end_date,
                    duration_days=process.duration_days,
                    input_material_name=process.input_material_name,
                    input_material_amount=process.input_material_amount,
                    input_fuel_name=process.input_fuel_name,
                    input_fuel_amount=process.input_fuel_amount,
                    power_usage=process.power_usage,
                    direct_emission=direct_emission,
                    indirect_emission=indirect_emission,
                    precursor_emission=precursor_emission,
                    total_emission=total_emission
                )
                
                calculated_processes.append(updated_process)
            
            logger.info(f"✅ 생산 공정별 배출량 계산 완료: {len(calculated_processes)}개")
            return calculated_processes
            
        except Exception as e:
            logger.error(f"❌ 생산 공정별 배출량 계산 실패: {str(e)}")
            raise ValueError(f"생산 공정별 배출량 계산 중 오류가 발생했습니다: {str(e)}")
    
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
                        "fuel_emfactor": fuel_calc.fuel_emfactor
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
                        "direct_factor": material_calc.em_factor
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
                            "name": precursor_data["name"],
                            "amount": precursor_data["amount"],
                            "emission": precursor_calc.emission,
                            "direct_factor": precursor_calc.direct_factor,
                            "indirect_factor": precursor_calc.indirect_factor
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
    
    def _calculate_fuel_emission_amount(self, fuel_amount: float, net_calory: float, fuel_emfactor: float) -> float:
        """연료 배출량 계산"""
        emission = fuel_amount * net_calory * fuel_emfactor * 1e-3
        return round(emission, 6)
    
    def _calculate_material_emission_amount(self, material_amount: float, em_factor: float) -> float:
        """원료 배출량 계산"""
        emission = material_amount * em_factor * 1.0
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
            precursor=precursor["precursor"],
            precursor_eng=precursor.get("precursor_eng", ""),
            cn1=precursor.get("cn1", ""),
            cn2=precursor.get("cn2", ""),
            cn3=precursor.get("cn3", ""),
            direct=precursor.get("direct", 0.0),
            indirect=precursor.get("indirect", 0.0),
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

    # ============================================================================
    # 🗄️ 새로운 테이블 서비스 메서드들
    # ============================================================================

    async def create_boundary(self, request: BoundaryCreateRequest) -> BoundaryResponse:
        """경계 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            boundary_data = {
                "boundary_id": 1,  # 실제로는 DB에서 자동 생성
                "name": request.name,
                "created_at": datetime.now().isoformat()
            }
            return BoundaryResponse(**boundary_data)
        except Exception as e:
            logger.error(f"Error creating boundary: {e}")
            raise e

    async def get_boundaries(self) -> List[BoundaryResponse]:
        """경계 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            boundaries = [
                {
                    "boundary_id": 1,
                    "name": "기본 경계",
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [BoundaryResponse(**boundary) for boundary in boundaries]
        except Exception as e:
            logger.error(f"Error getting boundaries: {e}")
            raise e

    async def create_product(self, request: ProductCreateRequest) -> ProductResponse:
        """제품 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            product_data = {
                "product_id": 1,  # 실제로는 DB에서 자동 생성
                "name": request.name,
                "cn_code": request.cn_code,
                "period_start": request.period_start,
                "period_end": request.period_end,
                "production_qty": request.production_qty,
                "sales_qty": request.sales_qty,
                "export_qty": request.export_qty,
                "inventory_qty": request.inventory_qty,
                "defect_rate": request.defect_rate,
                "node_id": None,
                "created_at": datetime.now().isoformat()
            }
            return ProductResponse(**product_data)
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise e

    async def get_products(self) -> List[ProductResponse]:
        """제품 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            products = [
                {
                    "product_id": 1,
                    "name": "철강 제품",
                    "cn_code": "7208",
                    "period_start": "2024-01-01",
                    "period_end": "2024-12-31",
                    "production_qty": 1000.0,
                    "sales_qty": 800.0,
                    "export_qty": 200.0,
                    "inventory_qty": 100.0,
                    "defect_rate": 0.05,
                    "node_id": None,
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [ProductResponse(**product) for product in products]
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise e

    async def create_operation(self, request: OperationCreateRequest) -> OperationResponse:
        """공정 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            operation_data = {
                "operation_id": 1,  # 실제로는 DB에서 자동 생성
                "name": request.name,
                "facility_id": request.facility_id,
                "category": request.category,
                "boundary_id": request.boundary_id,
                "node_id": request.node_id,
                "input_kind": request.input_kind,
                "material_id": request.material_id,
                "fuel_id": request.fuel_id,
                "quantity": request.quantity,
                "unit_id": request.unit_id,
                "created_at": datetime.now().isoformat()
            }
            return OperationResponse(**operation_data)
        except Exception as e:
            logger.error(f"Error creating operation: {e}")
            raise e

    async def get_operations(self) -> List[OperationResponse]:
        """공정 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            operations = [
                {
                    "operation_id": 1,
                    "name": "용해 공정",
                    "facility_id": 1,
                    "category": "제강",
                    "boundary_id": 1,
                    "node_id": "node-1",
                    "input_kind": "fuel",
                    "material_id": None,
                    "fuel_id": 1,
                    "quantity": 100.0,
                    "unit_id": 1,
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [OperationResponse(**operation) for operation in operations]
        except Exception as e:
            logger.error(f"Error getting operations: {e}")
            raise e

    async def create_node(self, request: NodeCreateRequest) -> NodeResponse:
        """노드 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            node_data = {
                "node_id": "node-" + str(uuid.uuid4()),  # 실제로는 DB에서 자동 생성
                "boundary_id": request.boundary_id,
                "node_type": request.node_type,
                "ref_id": request.ref_id,
                "label": request.label,
                "pos_x": request.pos_x,
                "pos_y": request.pos_y,
                "created_at": datetime.now().isoformat()
            }
            return NodeResponse(**node_data)
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            raise e

    async def get_nodes(self) -> List[NodeResponse]:
        """노드 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            nodes = [
                {
                    "node_id": "node-1",
                    "boundary_id": 1,
                    "node_type": "product",
                    "ref_id": 1,
                    "label": "철강 제품",
                    "pos_x": 100.0,
                    "pos_y": 100.0,
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [NodeResponse(**node) for node in nodes]
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            raise e

    async def create_edge(self, request: EdgeCreateRequest) -> EdgeResponse:
        """엣지 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            edge_data = {
                "edge_id": "edge-" + str(uuid.uuid4()),  # 실제로는 DB에서 자동 생성
                "boundary_id": request.boundary_id,
                "sourcenode_id": request.sourcenode_id,
                "targetnode_id": request.targetnode_id,
                "flow_type": request.flow_type,
                "label": request.label,
                "created_at": datetime.now().isoformat()
            }
            return EdgeResponse(**edge_data)
        except Exception as e:
            logger.error(f"Error creating edge: {e}")
            raise e

    async def get_edges(self) -> List[EdgeResponse]:
        """엣지 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            edges = [
                {
                    "edge_id": "edge-1",
                    "boundary_id": 1,
                    "sourcenode_id": "node-1",
                    "targetnode_id": "node-2",
                    "flow_type": "material",
                    "label": "원료 흐름",
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [EdgeResponse(**edge) for edge in edges]
        except Exception as e:
            logger.error(f"Error getting edges: {e}")
            raise e

    async def create_production_emission(self, request: ProductionEmissionCreateRequest) -> ProductionEmissionResponse:
        """생산 배출량 생성"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 저장 로직 구현
            emission_data = {
                "prod_result_id": 1,  # 실제로는 DB에서 자동 생성
                "product_id": request.product_id,
                "boundary_id": request.boundary_id,
                "result_unit_id": request.result_unit_id,
                "dir_emission": request.dir_emission,
                "indir_emission": request.indir_emission,
                "see": request.see,
                "created_at": datetime.now().isoformat()
            }
            return ProductionEmissionResponse(**emission_data)
        except Exception as e:
            logger.error(f"Error creating production emission: {e}")
            raise e

    async def get_production_emissions(self) -> List[ProductionEmissionResponse]:
        """생산 배출량 목록 조회"""
        try:
            # 실제 DB 연동 시에는 여기서 DB 조회 로직 구현
            emissions = [
                {
                    "prod_result_id": 1,
                    "product_id": 1,
                    "boundary_id": 1,
                    "result_unit_id": 1,
                    "dir_emission": 50.0,
                    "indir_emission": 30.0,
                    "see": 20.0,
                    "created_at": datetime.now().isoformat()
                }
            ]
            return [ProductionEmissionResponse(**emission) for emission in emissions]
        except Exception as e:
            logger.error(f"Error getting production emissions: {e}")
            raise e