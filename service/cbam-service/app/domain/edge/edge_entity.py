# ============================================================================
# 🔗 Edge Entity - ReactFlow 엣지 데이터 모델
# ============================================================================

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any

from app.common.database_base import Base

# ============================================================================
# 🔗 엣지 엔티티
# ============================================================================

class Edge(Base):
    """엣지 엔티티"""
    
    __tablename__ = "reactflow_edges"
    
    id = Column(Text, primary_key=True, index=True)
    flow_id = Column(Text, ForeignKey("reactflow_states.id"), nullable=False, index=True)
    
    # 엣지 기본 정보
    source = Column(Text, nullable=False)  # 시작 노드 ID
    target = Column(Text, nullable=False)  # 끝 노드 ID
    type = Column(Text, default="default")  # 엣지 타입
    
    # 엣지 스타일 및 속성
    style = Column(Text)  # CSS 스타일 (JSON)
    animated = Column(Boolean, default=False)  # 애니메이션 여부
    label = Column(Text)  # 엣지 라벨
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "flow_id": self.flow_id,
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "style": self.style,
            "animated": self.animated,
            "label": self.label,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_reactflow_data(cls, flow_id: str, edge_data: Dict[str, Any]) -> "Edge":
        """ReactFlow 데이터로부터 엣지 엔티티 생성"""
        return cls(
            id=edge_data.get('id'),
            flow_id=flow_id,
            source=edge_data.get('source'),
            target=edge_data.get('target'),
            type=edge_data.get('type', 'default'),
            style=edge_data.get('style'),
            animated=edge_data.get('animated', False),
            label=edge_data.get('label')
        )
