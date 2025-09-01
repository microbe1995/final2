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
    MatDirCalculationRequest, MatDirCalculationResponse
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
            # 데이터베이스 연결 상태 테스트
            logger.info("🔍 데이터베이스 연결 상태 테스트 시작")
            connection_ok = await self.matdir_repository.test_connection()
            if not connection_ok:
                raise Exception("데이터베이스 연결에 실패했습니다.")
            logger.info("✅ 데이터베이스 연결 상태 정상")
            
            # oxyfactor 기본값 설정
            oxyfactor = request.oxyfactor if request.oxyfactor is not None else Decimal('1.0000')
            
            # 계산 수행
            matdir_em = self.calculate_matdir_emission(
                request.mat_amount,
                request.mat_factor,
                oxyfactor
            )
            
            logger.info(f"🧮 계산된 배출량: {matdir_em}")
            
            # DB에 저장할 데이터 준비
            matdir_data = {
                "process_id": request.process_id,
                "mat_name": request.mat_name,
                "mat_factor": request.mat_factor,
                "mat_amount": request.mat_amount,
                "oxyfactor": oxyfactor,
                "matdir_em": matdir_em
            }
            
            logger.info(f"💾 DB 저장 데이터: {matdir_data}")
            logger.info(f"🔍 oxyfactor 최종 값: {matdir_data['oxyfactor']}")
            logger.info(f"🔍 matdir_em 최종 값: {matdir_data['matdir_em']}")
            logger.info(f"🔍 process_id 최종 값: {matdir_data['process_id']}")
            logger.info(f"🔍 mat_name 최종 값: {matdir_data['mat_name']}")
            logger.info(f"🔍 mat_factor 최종 값: {matdir_data['mat_factor']}")
            logger.info(f"🔍 mat_amount 최종 값: {matdir_data['mat_amount']}")
            
            logger.info("🚀 Repository create_matdir 호출 시작")
            saved_matdir = await self.matdir_repository.create_matdir(matdir_data)
            logger.info(f"✅ Repository create_matdir 호출 완료: {saved_matdir}")
            
            if saved_matdir:
                logger.info("🔄 MatDirResponse 변환 시작")
                response = MatDirResponse(**saved_matdir)
                logger.info(f"✅ MatDirResponse 변환 완료: {response}")
                return response
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
    # 🔍 원료명 조회 관련 메서드들 (Railway DB의 materials 테이블 사용)
    # ============================================================================

    async def lookup_material_by_name(self, mat_name: str) -> List[Dict[str, Any]]:
        """원료명으로 배출계수 조회 (자동 매핑 기능) - Railway DB의 materials 테이블 사용"""
        try:
            mappings = await self.matdir_repository.lookup_material_by_name(mat_name)
            return mappings
        except Exception as e:
            logger.error(f"Error looking up material by name '{mat_name}': {e}")
            raise e

    async def search_material_by_name(self, mat_name: str) -> List[Dict[str, Any]]:
        """원료명으로 검색 (부분 검색)"""
        try:
            # lookup_material_by_name과 동일한 로직 사용
            return await self.lookup_material_by_name(mat_name)
        except Exception as e:
            logger.error(f"Error searching material by name '{mat_name}': {e}")
            raise e

    # ============================================================================
    # 🏗️ Material Master 관련 메서드들 (fueldir과 동일한 패턴)
    # ============================================================================

    async def get_all_materials(self) -> Dict[str, Any]:
        """모든 원료 마스터 데이터 조회 - Railway DB의 materials 테이블 사용"""
        try:
            materials = await self.matdir_repository.get_all_materials()
            return {
                "materials": materials,
                "total_count": len(materials)
            }
        except Exception as e:
            logger.error(f"Error getting all materials: {e}")
            raise e

    async def search_materials(self, mat_name: str) -> List[Dict[str, Any]]:
        """원료명으로 검색 (부분 검색) - Railway DB의 materials 테이블 사용"""
        try:
            materials = await self.matdir_repository.search_materials(mat_name)
            return materials
        except Exception as e:
            logger.error(f"Error searching materials by name '{mat_name}': {e}")
            raise e

    async def get_material_factor_by_name(self, mat_name: str) -> Dict[str, Any]:
        """원료명으로 배출계수 조회 (자동 매핑 기능) - Railway DB의 materials 테이블 사용"""
        try:
            result = await self.matdir_repository.get_material_factor_by_name(mat_name)
            return result
        except Exception as e:
            logger.error(f"Error getting material factor by name '{mat_name}': {e}")
            raise e

    async def create_matdir_with_auto_factor(self, matdir_data: MatDirCreateRequest) -> MatDirResponse:
        """원료직접배출량 데이터 생성 (배출계수 자동 매핑) - Railway DB의 materials 테이블 사용"""
        try:
            # 원료명으로 배출계수 자동 조회
            material_factor = await self.get_material_factor_by_name(matdir_data.mat_name)
            
            if material_factor and material_factor.get('found'):
                # 배출계수를 자동으로 설정
                matdir_data.mat_factor = Decimal(str(material_factor['mat_factor']))
                logger.info(f"✅ 배출계수 자동 매핑 성공: {matdir_data.mat_name} → {matdir_data.mat_factor}")
            else:
                logger.warning(f"⚠️ 배출계수 자동 매핑 실패: {matdir_data.mat_name} - 기본값 사용")
                raise Exception(f"원료 '{matdir_data.mat_name}'의 배출계수를 찾을 수 없습니다. 수동으로 입력해주세요.")
            
            # 기존 생성 로직 사용
            return await self.create_matdir(matdir_data)
            
        except Exception as e:
            logger.error(f"Error creating matdir with auto factor: {e}")
            raise e
