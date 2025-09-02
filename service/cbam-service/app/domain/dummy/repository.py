"""
Dummy 데이터 리포지토리
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from .entity import DummyData


class DummyRepository:
    """Dummy 데이터 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[DummyData]:
        """모든 dummy 데이터 조회"""
        try:
            # Railway DB의 dummy 테이블에서 데이터 조회
            query = text("""
                SELECT id, 로트번호, 생산품명, 생산수량, 투입일, 종료일, 
                       공정, 투입물명, 수량, 단위, created_at, updated_at
                FROM dummy
                ORDER BY id
            """)
            
            result = self.db.execute(query)
            rows = result.fetchall()
            
            dummy_data = []
            for row in rows:
                dummy_data.append(DummyData(
                    id=row.id,
                    로트번호=row.로트번호,
                    생산품명=row.생산품명,
                    생산수량=row.생산수량,
                    투입일=row.투입일,
                    종료일=row.종료일,
                    공정=row.공정,
                    투입물명=row.투입물명,
                    수량=row.수량,
                    단위=row.단위,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                ))
            
            return dummy_data
            
        except Exception as e:
            print(f"Dummy 데이터 조회 실패: {e}")
            return []
    
    def get_by_id(self, dummy_id: int) -> Optional[DummyData]:
        """ID로 dummy 데이터 조회"""
        try:
            query = text("""
                SELECT id, 로트번호, 생산품명, 생산수량, 투입일, 종료일, 
                       공정, 투입물명, 수량, 단위, created_at, updated_at
                FROM dummy
                WHERE id = :id
            """)
            
            result = self.db.execute(query, {"id": dummy_id})
            row = result.fetchone()
            
            if row:
                return DummyData(
                    id=row.id,
                    로트번호=row.로트번호,
                    생산품명=row.생산품명,
                    생산수량=row.생산수량,
                    투입일=row.투입일,
                    종료일=row.종료일,
                    공정=row.공정,
                    투입물명=row.투입물명,
                    수량=row.수량,
                    단위=row.단위,
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            
            return None
            
        except Exception as e:
            print(f"Dummy 데이터 조회 실패: {e}")
            return None
