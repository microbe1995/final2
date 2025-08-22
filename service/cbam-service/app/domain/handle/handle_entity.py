# ============================================================================
# 🔘 Handle Entity - ReactFlow 핸들 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import relationship

Base = declarative_base()

# ============================================================================
# 🔗 핸들 엔티티
# ============================================================================

class Handle(Base):
    """핸들 엔티티"""
    __tablename__ = "reactflow_handles"
    
    # 기본 키
    id = Column(Text, primary_key=True, index=True)
    node_id = Column(Text, ForeignKey("reactflow_nodes.id"), nullable=False)
    flow_id = Column(Text, ForeignKey("reactflow_flows.id"), nullable=False)
    
    # 핸들 속성
    type = Column(Text, nullable=False, comment="핸들 타입 (source/target)")
    position = Column(Text, nullable=False, comment="핸들 위치 (top/bottom/left/right)")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    node = relationship("Node", back_populates="handles")
    flow = relationship("Flow", back_populates="handles")
    
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
