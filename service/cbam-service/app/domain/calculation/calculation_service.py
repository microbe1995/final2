# ============================================================================
# 🎯 Calculation Service - CBAM 계산 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.calculation.calculation_repository import CalculationRepository
from app.domain.calculation.calculation_schema import (
    ProcessAttrdirEmissionCreateRequest, ProcessAttrdirEmissionResponse, ProcessAttrdirEmissionUpdateRequest,
    ProcessEmissionCalculationRequest, ProcessEmissionCalculationResponse,
    ProductEmissionCalculationRequest, ProductEmissionCalculationResponse
)

logger = logging.getLogger(__name__)

class CalculationService:
    """CBAM 계산 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.calc_repository = CalculationRepository()
        logger.info("✅ Calculation 서비스 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            await self.calc_repository.initialize()
            logger.info("✅ CBAM 계산 서비스 데이터베이스 연결 초기화 완료")
        except Exception as e:
            logger.warning(f"⚠️ Calculation 서비스 데이터베이스 초기화 실패 (서비스는 계속 실행): {e}")
            logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    
    async def delete_process(self, process_id: int) -> bool:
        """프로세스 삭제"""
        try:
            success = await self.calc_repository.delete_process(process_id)
            if success:
                logger.info(f"✅ 프로세스 {process_id} 삭제 성공")
            else:
                logger.warning(f"⚠️ 프로세스 {process_id}를 찾을 수 없음")
            return success
        except Exception as e:
            logger.error(f"Error deleting process {process_id}: {e}")
            raise e


    # ============================================================================
    # 📊 배출량 계산 관련 메서드들
    # ============================================================================
    
    async def calculate_process_attrdir_emission(self, process_id: int) -> ProcessAttrdirEmissionResponse:
        """공정별 직접귀속배출량 계산 및 저장"""
        try:
            result = await self.calc_repository.calculate_process_attrdir_emission(process_id)
            if result:
                return ProcessAttrdirEmissionResponse(**result)
            else:
                raise Exception("공정별 직접귀속배출량 계산에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error calculating process attrdir emission for process {process_id}: {e}")
            raise e
    
    async def get_process_attrdir_emission(self, process_id: int) -> Optional[ProcessAttrdirEmissionResponse]:
        """공정별 직접귀속배출량 조회"""
        try:
            result = await self.calc_repository.get_process_attrdir_emission(process_id)
            if result:
                return ProcessAttrdirEmissionResponse(**result)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting process attrdir emission for process {process_id}: {e}")
            raise e

    async def get_all_process_attrdir_emissions(self) -> List[ProcessAttrdirEmissionResponse]:
        """모든 공정별 직접귀속배출량 조회"""
        try:
            results = await self.calc_repository.get_all_process_attrdir_emissions()
            return [ProcessAttrdirEmissionResponse(**result) for result in results]
        except Exception as e:
            logger.error(f"Error getting all process attrdir emissions: {e}")
            raise e

    async def calculate_product_total_emission(self, product_id: int) -> ProductEmissionCalculationResponse:
        """제품별 총 배출량 계산"""
        try:
            result = await self.calc_repository.calculate_product_total_emission(product_id)
            if result:
                return ProductEmissionCalculationResponse(**result)
            else:
                raise Exception("제품별 총 배출량 계산에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error calculating product total emission for product {product_id}: {e}")
            raise e
    
    async def get_all_process_attrdir_emissions(self) -> List[ProcessAttrdirEmissionResponse]:
        """모든 공정별 직접귀속배출량 조회"""
        try:
            results = await self.calc_repository.get_all_process_attrdir_emissions()
            return [ProcessAttrdirEmissionResponse(**result) for result in results]
        except Exception as e:
            logger.error(f"Error getting all process attrdir emissions: {e}")
            raise e
    
    async def calculate_process_emission(self, request: ProcessEmissionCalculationRequest) -> ProcessEmissionCalculationResponse:
        """공정별 배출량 계산 (공식 포함)"""
        try:
            from datetime import datetime
            
            # 1. 공정 정보 조회
            process = await self.calc_repository.get_process(request.process_id)
            if not process:
                raise Exception(f"공정 ID {request.process_id}를 찾을 수 없습니다.")
            
            # 2. 직접귀속배출량 계산 및 저장
            emission_summary = await self.calc_repository.calculate_process_attrdir_emission(request.process_id)
            if not emission_summary:
                raise Exception("직접귀속배출량 계산에 실패했습니다.")
            
            # 3. 계산 공식 생성
            calculation_formula = (
                f"직접귀속배출량 = 원료직접배출량({emission_summary['total_matdir_emission']}) + "
                f"연료직접배출량({emission_summary['total_fueldir_emission']}) = "
                f"{emission_summary['attrdir_em']} tCO2e"
            )
            
            logger.info(f"✅ 공정 {request.process_id} 직접귀속배출량 계산 완료: {emission_summary['attrdir_em']}")
            
            return ProcessEmissionCalculationResponse(
                process_id=request.process_id,
                process_name=process['process_name'],
                total_matdir_emission=float(emission_summary['total_matdir_emission']),
                total_fueldir_emission=float(emission_summary['total_fueldir_emission']),
                attrdir_em=float(emission_summary['attrdir_em']),
                calculation_formula=calculation_formula,
                calculation_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating process emission for process {request.process_id}: {e}")
            raise e
    
    async def calculate_product_emission(self, request: ProductEmissionCalculationRequest) -> ProductEmissionCalculationResponse:
        """제품별 배출량 계산 (공식 포함)"""
        try:
            from datetime import datetime
            
            # 1. 제품별 총 배출량 계산
            product_emission_data = await self.calc_repository.calculate_product_total_emission(request.product_id)
            if not product_emission_data:
                raise Exception(f"제품 ID {request.product_id}의 배출량 계산에 실패했습니다.")
            
            # 2. 각 공정별 배출량 계산 응답 생성
            process_emissions = []
            for pe in product_emission_data['process_emissions']:
                process_emission_response = ProcessEmissionCalculationResponse(
                    process_id=pe['process_id'],
                    process_name=pe['process_name'],
                    total_matdir_emission=float(pe['total_matdir_emission']),
                    total_fueldir_emission=float(pe['total_fueldir_emission']),
                    attrdir_em=float(pe['attrdir_em']),
                    calculation_formula=f"공정별 직접귀속배출량 = {pe['attrdir_em']} tCO2e",
                    calculation_date=datetime.utcnow()
                )
                process_emissions.append(process_emission_response)
            
            # 3. 제품별 계산 공식 생성
            calculation_formula = (
                f"제품 총 배출량 = Σ(공정별 배출량) = {product_emission_data['total_emission']} tCO2e "
                f"(연결된 공정 수: {product_emission_data['process_count']}개)"
            )
            
            logger.info(f"✅ 제품 {request.product_id} 배출량 계산 완료: {product_emission_data['total_emission']}")
            
            return ProductEmissionCalculationResponse(
                product_id=request.product_id,
                product_name=product_emission_data['product_name'],
                total_emission=product_emission_data['total_emission'],
                process_emissions=process_emissions,
                calculation_formula=calculation_formula,
                calculation_date=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error calculating product emission for product {request.product_id}: {e}")
            raise e

