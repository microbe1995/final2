# 🔄 Process Entity - 공정 데이터베이스 모델
from sqlalchemy import Column, Integer, Text, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Dict, Any, List

# 공통 Base 클래스 사용
from app.common.database_base import Base

class Process(Base):
    """프로세스 엔티티"""
    
    __tablename__ = "process"
    
    id = Column(Integer, primary_key=True, index=True)
    process_name = Column(Text, nullable=False, index=True)  # 프로세스명
    start_period = Column(Date, nullable=False)  # 시작일
    end_period = Column(Date, nullable=False)  # 종료일
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # 관계 설정
    product_processes = relationship("ProductProcess", back_populates="process")
    
    # 다대다 관계를 위한 편의 메서드
    @property
    def products(self):
        """이 공정과 연결된 모든 제품들"""
        return [pp.product for pp in self.product_processes]
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "process_name": self.process_name,
            "start_period": self.start_period.isoformat() if self.start_period else None,
            "end_period": self.end_period.isoformat() if self.end_period else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Process":
        """딕셔너리에서 엔티티 생성"""
        from datetime import date
        
        return cls(
            process_name=data.get("process_name"),
            start_period=date.fromisoformat(data.get("start_period")) if data.get("start_period") else None,
            end_period=date.fromisoformat(data.get("end_period")) if data.get("end_period") else None,
            created_at=datetime.now(timezone.utc)
        )
    
    def __repr__(self):
        return f"<Process(id={self.id}, process_name='{self.process_name}')>"
