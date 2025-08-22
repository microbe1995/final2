# ============================================================================
# 🔘 Handle Entity - ReactFlow 핸들 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

# ============================================================================
# 🔗 핸들 엔티티
# ============================================================================

class Handle(Base):
    """핸들 엔티티"""
    
    __tablename__ = "reactflow_handles"
    
    id = Column(Text, primary_key=True, index=True)
    node_id = Column(Text, ForeignKey("reactflow_nodes.id"), nullable=False)
    flow_id = Column(Text, ForeignKey("reactflow_flows.id"), nullable=False)
    
    # 핸들 정보
    type = Column(Text, nullable=False, default="default")  # source, target
    position = Column(Text, nullable=False, default="left")  # left, right, top, bottom
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "node_id": self.node_id,
            "flow_id": self.flow_id,
            "type": self.type,
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
