# ============================================================================
# 🎯 FuelDir Service - 연료직접배출량 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.domain.fueldir.fueldir_repository import FuelDirRepository
from app.domain.fueldir.fueldir_schema import (
    FuelDirCreateRequest, FuelDirResponse, FuelDirUpdateRequest, 
    FuelDirCalculationRequest, FuelDirCalculationResponse,
    FuelMasterSearchRequest, FuelMasterResponse, 
    FuelMasterListResponse, FuelMasterFactorResponse
)

logger = logging.getLogger(__name__)

class FuelDirService:
    """연료직접배출량 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.fueldir_repository = FuelDirRepository()
        logger.info("✅ FuelDir 서비스 초기화 완료")
    
    # ============================================================================
    # 📦 기존 FuelDir 관련 메서드들
    # ============================================================================
    
    async def create_fueldir(self, request: FuelDirCreateRequest) -> FuelDirResponse:
        """연료직접배출량 데이터 생성"""
        try:
            # 계산 수행
            fueldir_em = self.calculate_fueldir_emission(
                request.fuel_amount,
                request.fuel_factor,
                request.fuel_oxyfactor
            )
            
            logger.info(f"🧮 계산된 배출량: {fueldir_em}")
            
            # DB에 저장할 데이터 준비
            fueldir_data = {
                "process_id": request.process_id,
                "fuel_name": request.fuel_name,
                "fuel_factor": request.fuel_factor,
                "fuel_amount": request.fuel_amount,
                "fuel_oxyfactor": request.fuel_oxyfactor,
                "fueldir_em": fueldir_em
            }
            
            logger.info(f"💾 DB 저장 데이터: {fueldir_data}")
            
            saved_fueldir = await self.fueldir_repository.create_fueldir(fueldir_data)
            if saved_fueldir:
                return FuelDirResponse(**saved_fueldir)
            else:
                raise Exception("연료직접배출량 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating fueldir: {e}")
            raise e
    
    async def get_fueldirs(self, skip: int = 0, limit: int = 100) -> List[FuelDirResponse]:
        """모든 연료직접배출량 데이터 조회"""
        try:
            fueldirs = await self.fueldir_repository.get_fueldirs(skip, limit)
            return [FuelDirResponse(**fueldir) for fueldir in fueldirs]
        except Exception as e:
            logger.error(f"Error getting fueldirs: {e}")
            raise e
    
    async def get_fueldirs_by_process(self, process_id: int) -> List[FuelDirResponse]:
        """특정 공정의 연료직접배출량 데이터 조회"""
        try:
            fueldirs = await self.fueldir_repository.get_fueldirs_by_process(process_id)
            return [FuelDirResponse(**fueldir) for fueldir in fueldirs]
        except Exception as e:
            logger.error(f"Error getting fueldirs by process: {e}")
            raise e
    
    async def get_fueldir(self, fueldir_id: int) -> Optional[FuelDirResponse]:
        """특정 연료직접배출량 데이터 조회"""
        try:
            fueldir = await self.fueldir_repository.get_fueldir(fueldir_id)
            if fueldir:
                return FuelDirResponse(**fueldir)
            return None
        except Exception as e:
            logger.error(f"Error getting fueldir: {e}")
            raise e
    
    async def update_fueldir(self, fueldir_id: int, request: FuelDirUpdateRequest) -> Optional[FuelDirResponse]:
        """연료직접배출량 데이터 수정"""
        try:
            # 업데이트할 데이터 준비
            update_data = {}
            if request.fuel_name is not None:
                update_data['fuel_name'] = request.fuel_name
            if request.fuel_factor is not None:
                update_data['fuel_factor'] = request.fuel_factor
            if request.fuel_amount is not None:
                update_data['fuel_amount'] = request.fuel_amount
            if request.fuel_oxyfactor is not None:
                update_data['fuel_oxyfactor'] = request.fuel_oxyfactor
            
            # 값이 변경된 경우에만 재계산
            if any(key in update_data for key in ['fuel_amount', 'fuel_factor', 'fuel_oxyfactor']):
                # 기존 데이터 조회
                existing_fueldir = await self.fueldir_repository.get_fueldir(fueldir_id)
                if not existing_fueldir:
                    return None
                
                # 기존 값과 새 값을 조합하여 계산
                fuel_amount = update_data.get('fuel_amount', existing_fueldir['fuel_amount'])
                fuel_factor = update_data.get('fuel_factor', existing_fueldir['fuel_factor'])
                fuel_oxyfactor = update_data.get('fuel_oxyfactor', existing_fueldir['fuel_oxyfactor'])
                
                fueldir_em = self.calculate_fueldir_emission(fuel_amount, fuel_factor, fuel_oxyfactor)
                update_data['fueldir_em'] = fueldir_em
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_fueldir = await self.fueldir_repository.update_fueldir(fueldir_id, update_data)
            if updated_fueldir:
                return FuelDirResponse(**updated_fueldir)
            return None
        except Exception as e:
            logger.error(f"Error updating fueldir: {e}")
            raise e
    
    async def delete_fueldir(self, fueldir_id: int) -> bool:
        """연료직접배출량 데이터 삭제"""
        try:
            success = await self.fueldir_repository.delete_fueldir(fueldir_id)
            return success
        except Exception as e:
            logger.error(f"Error deleting fueldir: {e}")
            raise e

    def calculate_fueldir_emission(self, fuel_amount: Decimal, fuel_factor: Decimal, fuel_oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """연료직접배출량 계산: fueldir_em = fuel_amount * fuel_factor * fuel_oxyfactor"""
        try:
            # 배출량 계산
            emission = fuel_amount * fuel_factor * fuel_oxyfactor
            
            # 소수점 6자리로 반올림
            emission = round(emission, 6)
            
            logger.info(f"🧮 연료직접배출량 계산: {fuel_amount} × {fuel_factor} × {fuel_oxyfactor} = {emission}")
            return emission
            
        except Exception as e:
            logger.error(f"Error calculating fueldir emission: {e}")
            raise e
    
    def calculate_fueldir_emission_with_formula(self, request: FuelDirCalculationRequest) -> FuelDirCalculationResponse:
        """연료직접배출량 계산 (공식 포함)"""
        try:
            # 배출량 계산
            emission = self.calculate_fueldir_emission(
                request.fuel_amount,
                request.fuel_factor,
                request.fuel_oxyfactor
            )
            
            # 계산 공식 문자열 생성
            formula = f"연료직접배출량 = 연료량({request.fuel_amount}) × 배출계수({request.fuel_factor}) × 산화계수({request.fuel_oxyfactor}) = {emission} tCO2e"
            
            logger.info(f"✅ 연료직접배출량 계산 완료: {emission}")
            
            return FuelDirCalculationResponse(
                fuel_amount=request.fuel_amount,
                fuel_factor=request.fuel_factor,
                fuel_oxyfactor=request.fuel_oxyfactor,
                fueldir_em=emission,
                calculation_formula=formula
            )
            
        except Exception as e:
            logger.error(f"Error calculating fueldir emission with formula: {e}")
            raise e

    # ============================================================================
    # 🏗️ Fuel Master 관련 메서드들 (새로 추가)
    # ============================================================================

    async def get_fuel_by_name(self, fuel_name: str) -> Optional[FuelMasterResponse]:
        """연료명으로 마스터 데이터 조회"""
        try:
            fuel = await self.fueldir_repository.get_fuel_by_name(fuel_name)
            if fuel:
                return FuelMasterResponse(**fuel)
            return None
        except Exception as e:
            logger.error(f"Error getting fuel by name '{fuel_name}': {e}")
            raise e

    async def search_fuels(self, search_term: str) -> List[FuelMasterResponse]:
        """연료명으로 검색 (부분 검색)"""
        try:
            fuels = await self.fueldir_repository.search_fuels(search_term)
            return [FuelMasterResponse(**fuel) for fuel in fuels]
        except Exception as e:
            logger.error(f"Error searching fuels with term '{search_term}': {e}")
            raise e

    async def get_all_fuels(self) -> FuelMasterListResponse:
        """모든 연료 마스터 데이터 조회"""
        try:
            fuels = await self.fueldir_repository.get_all_fuels()
            fuel_responses = [FuelMasterResponse(**fuel) for fuel in fuels]
            return FuelMasterListResponse(
                fuels=fuel_responses,
                total_count=len(fuel_responses)
            )
        except Exception as e:
            logger.error(f"Error getting all fuels: {e}")
            raise e

    async def get_fuel_factor_by_name(self, fuel_name: str) -> FuelMasterFactorResponse:
        """연료명으로 배출계수 조회 (자동 매핑 기능)"""
        try:
            factor_data = await self.fueldir_repository.get_fuel_factor_by_name(fuel_name)
            return FuelMasterFactorResponse(**factor_data)
        except Exception as e:
            logger.error(f"Error getting fuel factor for '{fuel_name}': {e}")
            # 오류 시에도 응답 형식 유지
            return FuelMasterFactorResponse(
                fuel_name=fuel_name,
                fuel_factor=None,
                net_calory=None,
                found=False
            )

    async def create_fueldir_with_auto_factor(self, request: FuelDirCreateRequest) -> FuelDirResponse:
        """연료직접배출량 데이터 생성 (배출계수 자동 매핑)"""
        try:
            # 배출계수가 제공되지 않은 경우 자동으로 조회
            if request.fuel_factor is None or request.fuel_factor == 0:
                logger.info(f"🔍 배출계수 자동 조회: {request.fuel_name}")
                factor_response = await self.get_fuel_factor_by_name(request.fuel_name)
                
                if factor_response.found:
                    # 자동으로 배출계수 설정
                    request.fuel_factor = Decimal(str(factor_response.fuel_factor))
                    logger.info(f"✅ 배출계수 자동 설정: {request.fuel_name} → {request.fuel_factor}")
                else:
                    logger.warning(f"⚠️ 배출계수를 찾을 수 없음: {request.fuel_name}")
                    raise Exception(f"연료 '{request.fuel_name}'의 배출계수를 찾을 수 없습니다. 수동으로 입력해주세요.")
            
            # 기존 생성 로직 실행
            return await self.create_fueldir(request)
            
        except Exception as e:
            logger.error(f"Error creating fueldir with auto factor: {e}")
            raise e

    # ============================================================================
    # 📊 통계 및 요약 메서드
    # ============================================================================
    
    async def get_total_fueldir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 연료직접배출량 계산"""
        try:
            return await self.fueldir_repository.get_total_fueldir_emission_by_process(process_id)
        except Exception as e:
            logger.error(f"Error getting total fueldir emission by process: {e}")
            raise e
    
    async def get_fueldir_summary(self) -> Dict[str, Any]:
        """연료직접배출량 통계 요약"""
        try:
            return await self.fueldir_repository.get_fueldir_summary()
        except Exception as e:
            logger.error(f"Error getting fueldir summary: {e}")
            raise e
    
    # ============================================================================
    # 🔍 검색 및 필터링 메서드
    # ============================================================================
    
    async def search_fueldirs_by_name(self, fuel_name: str, skip: int = 0, limit: int = 100) -> List[FuelDirResponse]:
        """연료명으로 연료직접배출량 검색"""
        try:
            # 간단한 구현: 모든 데이터를 가져와서 필터링
            all_fueldirs = await self.fueldir_repository.get_fueldirs(0, 1000)  # 충분히 큰 수
            filtered_fueldirs = [
                fueldir for fueldir in all_fueldirs 
                if fuel_name.lower() in fueldir['fuel_name'].lower()
            ]
            
            # 페이지네이션 적용
            paginated_fueldirs = filtered_fueldirs[skip:skip + limit]
            
            return [FuelDirResponse(**fueldir) for fueldir in paginated_fueldirs]
            
        except Exception as e:
            logger.error(f"Error searching fueldirs by name: {e}")
            raise e
    
    async def get_fueldirs_by_date_range(self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[FuelDirResponse]:
        """날짜 범위로 연료직접배출량 조회"""
        try:
            # 간단한 구현: 모든 데이터를 가져와서 필터링
            all_fueldirs = await self.fueldir_repository.get_fueldirs(0, 1000)
            filtered_fueldirs = [
                fueldir for fueldir in all_fueldirs 
                if start_date <= fueldir['created_at'] <= end_date
            ]
            
            # 페이지네이션 적용
            paginated_fueldirs = filtered_fueldirs[skip:skip + limit]
            
            return [FuelDirResponse(**fueldir) for fueldir in paginated_fueldirs]
            
        except Exception as e:
            logger.error(f"Error getting fueldirs by date range: {e}")
            raise e
