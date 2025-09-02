"""
Dummy 데이터 서비스
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from .repository import DummyRepository
from .entity import DummyData


class DummyService:
    """Dummy 데이터 서비스"""
    
    def __init__(self, db: Session):
        self.repository = DummyRepository(db)
    
    def get_all_dummy_data(self) -> List[DummyData]:
        """모든 dummy 데이터 조회"""
        return self.repository.get_all()
    
    def get_dummy_data_by_id(self, dummy_id: int) -> Optional[DummyData]:
        """ID로 dummy 데이터 조회"""
        return self.repository.get_by_id(dummy_id)
