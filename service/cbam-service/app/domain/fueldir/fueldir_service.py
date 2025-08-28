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
    FuelDirCalculationRequest, FuelDirCalculationResponse
)

logger = logging.getLogger(__name__)

class FuelDirService:
    """연료직접배출량 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.fueldir_repository = FuelDirRepository()
        logger.info("✅ FuelDir 서비스 초기화 완료")
    
    # ============================================================================
    # 📦 FuelDir 관련 메서드
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
            
            # 배출량 재계산이 필요한 경우
            if any(key in update_data for key in ['fuel_factor', 'fuel_amount', 'fuel_oxyfactor']):
                # 기존 데이터 조회
                existing_fueldir = await self.fueldir_repository.get_fueldir(fueldir_id)
                if existing_fueldir:
                    # 새로운 값으로 계산
                    new_factor = update_data.get('fuel_factor', existing_fueldir['fuel_factor'])
                    new_amount = update_data.get('fuel_amount', existing_fueldir['fuel_amount'])
                    new_oxyfactor = update_data.get('fuel_oxyfactor', existing_fueldir['fuel_oxyfactor'])
                    
                    new_emission = self.calculate_fueldir_emission(new_amount, new_factor, new_oxyfactor)
                    update_data['fueldir_em'] = new_emission
                    logger.info(f"🧮 배출량 재계산: {new_emission}")
            
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
            return await self.fueldir_repository.delete_fueldir(fueldir_id)
        except Exception as e:
            logger.error(f"Error deleting fueldir: {e}")
            raise e
    
    # ============================================================================
    # 🧮 계산 관련 메서드
    # ============================================================================
    
    def calculate_fueldir_emission(self, fuel_amount: Decimal, fuel_factor: Decimal, fuel_oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """연료직접배출량 계산"""
        try:
            # 기본 공식: 연료량 × 배출계수 × 산화계수
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
