# ============================================================================
# 🎯 MatDir Service - 원료직접배출량 비즈니스 로직
# ============================================================================

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.domain.matdir.matdir_repository import MatDirRepository
from app.domain.matdir.matdir_schema import (
    MatDirCreateRequest, MatDirResponse, MatDirUpdateRequest, 
    MatDirCalculationRequest, MatDirCalculationResponse,
    MaterialMasterSearchRequest, MaterialMasterResponse, 
    MaterialMasterListResponse, MaterialMasterFactorResponse
)

logger = logging.getLogger(__name__)

class MatDirService:
    """원료직접배출량 비즈니스 로직 클래스"""
    
    def __init__(self):
        self.matdir_repository = MatDirRepository()
        logger.info("✅ MatDir 서비스 초기화 완료")
    
    # ============================================================================
    # 📦 기존 MatDir 관련 메서드들
    # ============================================================================
    
    async def create_matdir(self, request: MatDirCreateRequest) -> MatDirResponse:
        """원료직접배출량 데이터 생성"""
        try:
            # 계산 수행
            matdir_em = self.calculate_matdir_emission(
                request.mat_amount,
                request.mat_factor,
                request.oxyfactor
            )
            
            logger.info(f"🧮 계산된 배출량: {matdir_em}")
            
            # DB에 저장할 데이터 준비
            matdir_data = {
                "process_id": request.process_id,
                "mat_name": request.mat_name,
                "mat_factor": request.mat_factor,
                "mat_amount": request.mat_amount,
                "oxyfactor": request.oxyfactor,
                "matdir_em": matdir_em
            }
            
            logger.info(f"💾 DB 저장 데이터: {matdir_data}")
            
            saved_matdir = await self.matdir_repository.create_matdir(matdir_data)
            if saved_matdir:
                return MatDirResponse(**saved_matdir)
            else:
                raise Exception("원료직접배출량 저장에 실패했습니다.")
        except Exception as e:
            logger.error(f"Error creating matdir: {e}")
            raise e
    
    async def get_matdirs(self, skip: int = 0, limit: int = 100) -> List[MatDirResponse]:
        """모든 원료직접배출량 데이터 조회"""
        try:
            matdirs = await self.matdir_repository.get_matdirs(skip, limit)
            return [MatDirResponse(**matdir) for matdir in matdirs]
        except Exception as e:
            logger.error(f"Error getting matdirs: {e}")
            raise e
    
    async def get_matdirs_by_process(self, process_id: int) -> List[MatDirResponse]:
        """특정 공정의 원료직접배출량 데이터 조회"""
        try:
            matdirs = await self.matdir_repository.get_matdirs_by_process(process_id)
            return [MatDirResponse(**matdir) for matdir in matdirs]
        except Exception as e:
            logger.error(f"Error getting matdirs by process {process_id}: {e}")
            raise e
    
    async def get_matdir(self, matdir_id: int) -> Optional[MatDirResponse]:
        """특정 원료직접배출량 데이터 조회"""
        try:
            matdir = await self.matdir_repository.get_matdir(matdir_id)
            if matdir:
                return MatDirResponse(**matdir)
            return None
        except Exception as e:
            logger.error(f"Error getting matdir {matdir_id}: {e}")
            raise e
    
    async def update_matdir(self, matdir_id: int, request: MatDirUpdateRequest) -> Optional[MatDirResponse]:
        """원료직접배출량 데이터 수정"""
        try:
            # 기존 데이터 조회
            existing_matdir = await self.matdir_repository.get_matdir(matdir_id)
            if not existing_matdir:
                return None
            
            # 업데이트할 데이터 준비
            update_data = {}
            if request.process_id is not None:
                update_data["process_id"] = request.process_id
            if request.mat_name is not None:
                update_data["mat_name"] = request.mat_name
            if request.mat_factor is not None:
                update_data["mat_factor"] = request.mat_factor
            if request.mat_amount is not None:
                update_data["mat_amount"] = request.mat_amount
            if request.oxyfactor is not None:
                update_data["oxyfactor"] = request.oxyfactor
            
            # 값이 변경된 경우에만 재계산
            if any(key in update_data for key in ['mat_amount', 'mat_factor', 'oxyfactor']):
                # 기존 값과 새 값을 조합하여 계산
                mat_amount = update_data.get('mat_amount', existing_matdir['mat_amount'])
                mat_factor = update_data.get('mat_factor', existing_matdir['mat_factor'])
                oxyfactor = update_data.get('oxyfactor', existing_matdir['oxyfactor'])
                
                matdir_em = self.calculate_matdir_emission(mat_amount, mat_factor, oxyfactor)
                update_data['matdir_em'] = matdir_em
            
            if not update_data:
                raise Exception("업데이트할 데이터가 없습니다.")
            
            updated_matdir = await self.matdir_repository.update_matdir(matdir_id, update_data)
            if updated_matdir:
                return MatDirResponse(**updated_matdir)
            return None
        except Exception as e:
            logger.error(f"Error updating matdir {matdir_id}: {e}")
            raise e
    
    async def delete_matdir(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제"""
        try:
            success = await self.matdir_repository.delete_matdir(matdir_id)
            return success
        except Exception as e:
            logger.error(f"Error deleting matdir {matdir_id}: {e}")
            raise e
    
    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return self.matdir_repository.calculate_matdir_emission(mat_amount, mat_factor, oxyfactor)

    def calculate_matdir_emission_with_formula(self, calculation_data: MatDirCalculationRequest) -> MatDirCalculationResponse:
        """원료직접배출량 계산 (공식 포함)"""
        matdir_em = self.calculate_matdir_emission(
            calculation_data.mat_amount,
            calculation_data.mat_factor,
            calculation_data.oxyfactor
        )
        
        formula = f"matdir_em = {calculation_data.mat_amount} × {calculation_data.mat_factor} × {calculation_data.oxyfactor} = {matdir_em}"
        
        return MatDirCalculationResponse(
            matdir_em=matdir_em,
            calculation_formula=formula
        )

    async def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        try:
            total_emission = await self.matdir_repository.get_total_matdir_emission_by_process(process_id)
            return total_emission
        except Exception as e:
            logger.error(f"Error getting total matdir emission for process {process_id}: {e}")
            raise e

    # ============================================================================
    # 🏗️ Material Master 관련 메서드들 (새로 추가)
    # ============================================================================

    async def get_material_by_name(self, mat_name: str) -> Optional[MaterialMasterResponse]:
        """원료명으로 마스터 데이터 조회"""
        try:
            material = await self.matdir_repository.get_material_by_name(mat_name)
            if material:
                return MaterialMasterResponse(**material)
            return None
        except Exception as e:
            logger.error(f"Error getting material by name '{mat_name}': {e}")
            raise e

    async def search_materials(self, search_term: str) -> List[MaterialMasterResponse]:
        """원료명으로 검색 (부분 검색)"""
        try:
            materials = await self.matdir_repository.search_materials(search_term)
            return [MaterialMasterResponse(**material) for material in materials]
        except Exception as e:
            logger.error(f"Error searching materials with term '{search_term}': {e}")
            raise e

    async def get_all_materials(self) -> MaterialMasterListResponse:
        """모든 원료 마스터 데이터 조회"""
        try:
            materials = await self.matdir_repository.get_all_materials()
            material_responses = [MaterialMasterResponse(**material) for material in materials]
            return MaterialMasterListResponse(
                materials=material_responses,
                total_count=len(material_responses)
            )
        except Exception as e:
            logger.error(f"Error getting all materials: {e}")
            raise e

    async def get_material_factor_by_name(self, mat_name: str) -> MaterialMasterFactorResponse:
        """원료명으로 배출계수 조회 (자동 매핑 기능)"""
        try:
            factor_data = await self.matdir_repository.get_material_factor_by_name(mat_name)
            return MaterialMasterFactorResponse(**factor_data)
        except Exception as e:
            logger.error(f"Error getting material factor for '{mat_name}': {e}")
            # 오류 시에도 응답 형식 유지
            return MaterialMasterFactorResponse(
                mat_name=mat_name,
                mat_factor=None,
                carbon_content=None,
                found=False
            )

    async def create_matdir_with_auto_factor(self, request: MatDirCreateRequest) -> MatDirResponse:
        """원료직접배출량 데이터 생성 (배출계수 자동 매핑)"""
        try:
            # 배출계수가 제공되지 않은 경우 자동으로 조회
            if request.mat_factor is None or request.mat_factor == 0:
                logger.info(f"🔍 배출계수 자동 조회: {request.mat_name}")
                factor_response = await self.get_material_factor_by_name(request.mat_name)
                
                if factor_response.found:
                    # 자동으로 배출계수 설정
                    request.mat_factor = Decimal(str(factor_response.mat_factor))
                    logger.info(f"✅ 배출계수 자동 설정: {request.mat_name} → {request.mat_factor}")
                else:
                    logger.warning(f"⚠️ 배출계수를 찾을 수 없음: {request.mat_name}")
                    raise Exception(f"원료 '{request.mat_name}'의 배출계수를 찾을 수 없습니다. 수동으로 입력해주세요.")
            
            # 기존 생성 로직 실행
            return await self.create_matdir(request)
            
        except Exception as e:
            logger.error(f"Error creating matdir with auto factor: {e}")
            raise e
