# ============================================================================
# 🔵 Node Entity - ReactFlow 노드 엔티티
# ============================================================================

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ReactFlowNode(Base):
    """ReactFlow 노드를 표현하는 엔티티"""
    __tablename__ = "reactflow_nodes"
    
    # 기본 필드
    id: Mapped[str] = mapped_column(Text, primary_key=True, index=True)
    flow_id: Mapped[str] = mapped_column(Text, nullable=False, index=True, comment="플로우 ID")
    
    # ReactFlow 노드 속성
    node_type: Mapped[str] = mapped_column(Text, nullable=False, default="default", comment="노드 타입")
    position_x: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, comment="X 좌표")
    position_y: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, comment="Y 좌표")
    
    # 노드 데이터 (JSON)
    data_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="노드 데이터 JSON")
    
    # 노드 설정
    width: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True, comment="노드 너비")
    height: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True, comment="노드 높이")
    draggable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="드래그 가능 여부")
    selectable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="선택 가능 여부")
    deletable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="삭제 가능 여부")
    
    # 스타일 (JSON)
    style_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="노드 스타일 JSON")
    
    # 메타데이터
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    @property
    def position(self) -> Dict[str, float]:
        """노드 위치 반환"""
        return {
            "x": float(self.position_x) if self.position_x else 0.0,
            "y": float(self.position_y) if self.position_y else 0.0
        }
    
    @position.setter
    def position(self, value: Dict[str, float]) -> None:
        """노드 위치 설정"""
        self.position_x = value.get("x", 0)
        self.position_y = value.get("y", 0)
    
    @property
    def data(self) -> Dict[str, Any]:
        """노드 데이터 반환"""
        if self.data_json:
            return json.loads(self.data_json)
        return {}
    
    @data.setter
    def data(self, value: Dict[str, Any]) -> None:
        """노드 데이터 설정"""
        self.data_json = json.dumps(value) if value else None
    
    @property
    def style(self) -> Dict[str, Any]:
        """노드 스타일 반환"""
        if self.style_json:
            return json.loads(self.style_json)
        return {}
    
    @style.setter
    def style(self, value: Dict[str, Any]) -> None:
        """노드 스타일 설정"""
        self.style_json = json.dumps(value) if value else None
    
    def to_reactflow_format(self) -> Dict[str, Any]:
        """ReactFlow 형식으로 변환"""
        result = {
            "id": self.id,
            "type": self.node_type,
            "position": self.position,
            "data": self.data,
            "draggable": self.draggable,
            "selectable": self.selectable,
            "deletable": self.deletable
        }
        
        if self.width and self.height:
            result["width"] = float(self.width) if self.width else None
            result["height"] = float(self.height) if self.height else None
            
        if self.style:
            result["style"] = self.style
            
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "flow_id": self.flow_id,
            "type": self.node_type,
            "position": self.position,
            "data": self.data,
            "width": float(self.width) if self.width else None,
            "height": float(self.height) if self.height else None,
            "draggable": self.draggable,
            "selectable": self.selectable,
            "deletable": self.deletable,
            "style": self.style,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
