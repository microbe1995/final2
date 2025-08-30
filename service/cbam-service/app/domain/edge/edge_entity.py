from sqlalchemy import Column, Integer, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

# ============================================================================
# 🔗 Edge Entity - 엣지 데이터베이스 모델
# ============================================================================

class Edge(Base):
    """엣지 엔티티"""
    
    __tablename__ = "edge"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, index=True)  # 소스 노드 ID
    target_id = Column(Integer, nullable=False, index=True)  # 타겟 노드 ID
    edge_kind = Column(Text, nullable=False)  # 엣지 종류 (consume/produce/continue)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_kind": self.edge_kind,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """딕셔너리에서 엔티티 생성"""
        return cls(
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            edge_kind=data.get("edge_kind")
        )
    
    def __repr__(self):
        return f"<Edge(id={self.id}, source_id={self.source_id}, target_id={self.target_id}, edge_kind='{self.edge_kind}')>"
