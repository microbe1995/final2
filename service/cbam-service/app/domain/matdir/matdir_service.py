from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from .matdir_repository import MatDirRepository
from .matdir_schema import MatDirCreateRequest, MatDirUpdateRequest, MatDirCalculationRequest, MatDirCalculationResponse

class MatDirService:
    def __init__(self, db: Session):
        self.repository = MatDirRepository(db)

    def create_matdir(self, matdir_data: MatDirCreateRequest):
        """원료직접배출량 데이터 생성"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 계산 수행
            matdir_em = self.calculate_matdir_emission(
                matdir_data.mat_amount,
                matdir_data.mat_factor,
                matdir_data.oxyfactor
            )
            
            logger.info(f"🧮 계산된 배출량: {matdir_em}")
            
            # DB에 저장할 데이터 준비
            db_data = matdir_data.dict()
            db_data['matdir_em'] = matdir_em
            
            logger.info(f"💾 DB 저장 데이터: {db_data}")
            
            result = self.repository.create_matdir(db_data)
            logger.info(f"✅ DB 저장 성공: ID {result.id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 원료직접배출량 생성 중 오류: {str(e)}")
            raise

    def get_matdirs(self, skip: int = 0, limit: int = 100):
        """모든 원료직접배출량 데이터 조회"""
        return self.repository.get_matdirs(skip, limit)

    def get_matdirs_by_process(self, process_id: int):
        """특정 공정의 원료직접배출량 데이터 조회"""
        return self.repository.get_matdirs_by_process(process_id)

    def get_matdir(self, matdir_id: int):
        """특정 원료직접배출량 데이터 조회"""
        return self.repository.get_matdir(matdir_id)

    def update_matdir(self, matdir_id: int, matdir_data: MatDirUpdateRequest):
        """원료직접배출량 데이터 수정"""
        # 기존 데이터 조회
        existing_matdir = self.repository.get_matdir(matdir_id)
        if not existing_matdir:
            return None
        
        # 업데이트할 데이터 준비
        update_data = matdir_data.dict(exclude_unset=True)
        
        # 값이 변경된 경우에만 재계산
        if any(key in update_data for key in ['mat_amount', 'mat_factor', 'oxyfactor']):
            # 기존 값과 새 값을 조합하여 계산
            mat_amount = update_data.get('mat_amount', existing_matdir.mat_amount)
            mat_factor = update_data.get('mat_factor', existing_matdir.mat_factor)
            oxyfactor = update_data.get('oxyfactor', existing_matdir.oxyfactor)
            
            matdir_em = self.calculate_matdir_emission(mat_amount, mat_factor, oxyfactor)
            update_data['matdir_em'] = matdir_em
        
        return self.repository.update_matdir(matdir_id, update_data)

    def delete_matdir(self, matdir_id: int):
        """원료직접배출량 데이터 삭제"""
        return self.repository.delete_matdir(matdir_id)

    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return self.repository.calculate_matdir_emission(mat_amount, mat_factor, oxyfactor)

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

    def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        return self.repository.get_total_matdir_emission_by_process(process_id)
