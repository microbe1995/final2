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
    
    def __repr__(self):
        return f"<Edge(id={self.id}, source_node_type='{self.source_node_type}', source_id={self.source_id}, target_node_type='{self.target_node_type}', target_id={self.target_id}, edge_kind='{self.edge_kind}')>"
