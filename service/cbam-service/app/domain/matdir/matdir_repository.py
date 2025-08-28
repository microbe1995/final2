from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from .matdir_entity import MatDir

class MatDirRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_matdir(self, matdir_data: dict) -> MatDir:
        """원료직접배출량 데이터 생성"""
        db_matdir = MatDir(**matdir_data)
        self.db.add(db_matdir)
        self.db.commit()
        self.db.refresh(db_matdir)
        return db_matdir

    def get_matdirs(self, skip: int = 0, limit: int = 100) -> List[MatDir]:
        """모든 원료직접배출량 데이터 조회"""
        return self.db.query(MatDir).offset(skip).limit(limit).all()

    def get_matdirs_by_process(self, process_id: int) -> List[MatDir]:
        """특정 공정의 원료직접배출량 데이터 조회"""
        return self.db.query(MatDir).filter(MatDir.process_id == process_id).all()

    def get_matdir(self, matdir_id: int) -> Optional[MatDir]:
        """특정 원료직접배출량 데이터 조회"""
        return self.db.query(MatDir).filter(MatDir.id == matdir_id).first()

    def update_matdir(self, matdir_id: int, matdir_data: dict) -> Optional[MatDir]:
        """원료직접배출량 데이터 수정"""
        db_matdir = self.get_matdir(matdir_id)
        if db_matdir:
            for key, value in matdir_data.items():
                if hasattr(db_matdir, key):
                    setattr(db_matdir, key, value)
            self.db.commit()
            self.db.refresh(db_matdir)
        return db_matdir

    def delete_matdir(self, matdir_id: int) -> bool:
        """원료직접배출량 데이터 삭제"""
        db_matdir = self.get_matdir(matdir_id)
        if db_matdir:
            self.db.delete(db_matdir)
            self.db.commit()
            return True
        return False

    def calculate_matdir_emission(self, mat_amount: Decimal, mat_factor: Decimal, oxyfactor: Decimal = Decimal('1.0000')) -> Decimal:
        """원료직접배출량 계산: matdir_em = mat_amount * mat_factor * oxyfactor"""
        return mat_amount * mat_factor * oxyfactor

    def update_matdir_emission(self, matdir_id: int) -> Optional[MatDir]:
        """원료직접배출량 계산 및 업데이트"""
        db_matdir = self.get_matdir(matdir_id)
        if db_matdir:
            matdir_em = self.calculate_matdir_emission(
                db_matdir.mat_amount,
                db_matdir.mat_factor,
                db_matdir.oxyfactor
            )
            db_matdir.matdir_em = matdir_em
            self.db.commit()
            self.db.refresh(db_matdir)
        return db_matdir

    def get_total_matdir_emission_by_process(self, process_id: int) -> Decimal:
        """특정 공정의 총 원료직접배출량 계산"""
        matdirs = self.get_matdirs_by_process(process_id)
        total_emission = sum(matdir.matdir_em for matdir in matdirs if matdir.matdir_em)
        return total_emission
