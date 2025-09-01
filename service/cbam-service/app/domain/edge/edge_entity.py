from sqlalchemy import Column, Integer, Text, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Dict, Any

from app.common.database_base import Base

# ============================================================================
# 🔗 Edge Entity - 엣지 데이터베이스 모델
# ============================================================================

class Edge(Base):
    """엣지 엔티티"""
    
    __tablename__ = "edge"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_node_type = Column(Text, nullable=False, index=True)  # 소스 노드 타입
    source_id = Column(Integer, nullable=False, index=True)  # 소스 노드 ID
    target_node_type = Column(Text, nullable=False, index=True)  # 타겟 노드 타입
    target_id = Column(Integer, nullable=False, index=True)  # 타겟 노드 ID
    edge_kind = Column(Text, nullable=False)  # 엣지 종류 (consume/produce/continue)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "source_node_type": self.source_node_type,
            "source_id": self.source_id,
            "target_node_type": self.target_node_type,
            "target_id": self.target_id,
            "edge_kind": self.edge_kind,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        """딕셔너리에서 엔티티 생성"""
        return cls(
            source_node_type=data.get("source_node_type"),
            source_id=data.get("source_id"),
            target_node_type=data.get("target_node_type"),
            target_id=data.get("target_id"),
            edge_kind=data.get("edge_kind")
        )
    
    def __repr__(self):
        return f"<Edge(id={self.id}, source_node_type='{self.source_node_type}', source_id={self.source_id}, target_node_type='{self.target_node_type}', target_id={self.target_id}, edge_kind='{self.edge_kind}')>"
