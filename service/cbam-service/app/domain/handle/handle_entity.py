# ============================================================================
# 🔘 Handle Entity - ReactFlow 핸들 데이터 모델
# ============================================================================

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.common.database_base import Base

class ReactFlowHandle(Base):
    """ReactFlow 핸들 엔티티"""
    
    __tablename__ = "reactflow_handles"
    
    # 기본 필드
    id = Column(String(50), primary_key=True, index=True)
    node_id = Column(String(50), ForeignKey("reactflow_nodes.id"), nullable=False)
    flow_id = Column(String(50), ForeignKey("reactflow_flows.id"), nullable=False)
    
    # 핸들 타입 및 위치
    type = Column(String(20), nullable=False, default="default")  # source, target
    position = Column(String(20), nullable=False, default="left")  # left, right, top, bottom
    
    # 핸들 속성
    style = Column(Text, nullable=True)  # JSON 스타일
    data = Column(Text, nullable=True)   # JSON 데이터
    
    # 연결 관련
    is_connectable = Column(Boolean, default=True)
    is_valid_connection = Column(Boolean, default=True)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    node = relationship("ReactFlowNode", back_populates="handles")
    flow = relationship("ReactFlowFlow", back_populates="handles")
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "node_id": self.node_id,
            "flow_id": self.flow_id,
            "type": self.type,
            "position": self.position,
            "style": self.style,
            "data": self.data,
            "is_connectable": self.is_connectable,
            "is_valid_connection": self.is_valid_connection,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<ReactFlowHandle(id={self.id}, node_id={self.node_id}, type={self.type}, position={self.position})>"
