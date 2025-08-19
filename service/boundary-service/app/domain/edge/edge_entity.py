# ============================================================================
# 🔗 Edge Entity - ReactFlow 엣지 데이터 모델
# ============================================================================

from sqlalchemy import Column, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional

from app.common.database_base import Base

class ReactFlowEdge(Base):
    """ReactFlow 엣지 엔티티"""
    
    __tablename__ = "reactflow_edges"
    
    # ============================================================================
    # 🔑 기본 필드
    # ============================================================================
    
    id = Column(String(255), primary_key=True, index=True)
    flow_id = Column(String(255), ForeignKey("reactflow_states.id"), nullable=False, index=True)
    
    # ============================================================================
    # 🔗 ReactFlow 엣지 기본 속성
    # ============================================================================
    
    source = Column(String(255), nullable=False)  # 시작 노드 ID
    target = Column(String(255), nullable=False)  # 끝 노드 ID
    type = Column(String(100), default="default")  # 엣지 타입
    
    # ============================================================================
    # 📊 엣지 데이터 (JSON 형태)
    # ============================================================================
    
    data_json = Column(JSON, nullable=True)  # 엣지 데이터 (label, processType 등)
    
    # ============================================================================
    # 🎨 스타일 및 설정
    # ============================================================================
    
    style_json = Column(JSON, nullable=True)  # 엣지 스타일
    animated = Column(Boolean, default=False)  # 애니메이션 여부
    hidden = Column(Boolean, default=False)  # 숨김 여부
    deletable = Column(Boolean, default=True)  # 삭제 가능 여부
    
    # ============================================================================
    # 🔄 상태 및 메타데이터
    # ============================================================================
    
    selected = Column(Boolean, default=False)  # 선택 상태
    
    # ============================================================================
    # ⏰ 타임스탬프
    # ============================================================================
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ============================================================================
    # 🔗 관계 설정
    # ============================================================================
    
    # Flow와의 관계 (한 Flow는 여러 Edge를 가질 수 있음)
    flow = relationship("ReactFlowState", back_populates="edges")
    
    def __repr__(self) -> str:
        return f"<ReactFlowEdge(id='{self.id}', source='{self.source}', target='{self.target}', type='{self.type}')>"
    
    # ============================================================================
    # 🔧 유틸리티 메서드
    # ============================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        import json
        
        # data_json 파싱
        data = {}
        if self.data_json:
            if isinstance(self.data_json, str):
                try:
                    data = json.loads(self.data_json)
                except:
                    data = {}
            else:
                data = self.data_json
        
        # style_json 파싱
        style = {}
        if self.style_json:
            if isinstance(self.style_json, str):
                try:
                    style = json.loads(self.style_json)
                except:
                    style = {}
            else:
                style = self.style_json
        
        return {
            "id": self.id,
            "flow_id": self.flow_id,
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "data": data,
            "style": style,
            "animated": self.animated,
            "hidden": self.hidden,
            "deletable": self.deletable,
            "selected": self.selected,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_reactflow_format(self) -> Dict[str, Any]:
        """ReactFlow 프론트엔드 형식으로 변환"""
        import json
        
        # data_json 파싱
        data = {}
        if self.data_json:
            if isinstance(self.data_json, str):
                try:
                    data = json.loads(self.data_json)
                except:
                    data = {}
            else:
                data = self.data_json
        
        # style_json 파싱
        style = {}
        if self.style_json:
            if isinstance(self.style_json, str):
                try:
                    style = json.loads(self.style_json)
                except:
                    style = {}
            else:
                style = self.style_json
        
        edge_data = {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "data": data
        }
        
        # 선택적 필드들 추가
        if self.type and self.type != "default":
            edge_data["type"] = self.type
            
        if style:
            edge_data["style"] = style
            
        if self.animated:
            edge_data["animated"] = True
            
        if self.hidden:
            edge_data["hidden"] = True
            
        if not self.deletable:
            edge_data["deletable"] = False
            
        if self.selected:
            edge_data["selected"] = True
        
        return edge_data
    
    @classmethod
    def from_reactflow_data(cls, flow_id: str, edge_data: Dict[str, Any]) -> "ReactFlowEdge":
        """ReactFlow 데이터에서 엔티티 생성"""
        import json
        
        return cls(
            id=edge_data.get("id"),
            flow_id=flow_id,
            source=edge_data.get("source"),
            target=edge_data.get("target"),
            type=edge_data.get("type", "default"),
            data_json=json.dumps(edge_data.get("data", {})) if edge_data.get("data") else None,
            style_json=json.dumps(edge_data.get("style", {})) if edge_data.get("style") else None,
            animated=edge_data.get("animated", False),
            hidden=edge_data.get("hidden", False),
            deletable=edge_data.get("deletable", True),
            selected=edge_data.get("selected", False)
        )
