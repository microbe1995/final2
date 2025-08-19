# ============================================================================
# 🌊 Flow Entity - ReactFlow 플로우 엔티티
# ============================================================================

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.common.database_base import Base

class ReactFlowState(Base):
    """ReactFlow 플로우 상태를 표현하는 엔티티"""
    __tablename__ = "reactflow_states"
    
    # 기본 필드
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="플로우 이름")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="플로우 설명")
    
    # 뷰포트 상태
    viewport_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="뷰포트 X")
    viewport_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="뷰포트 Y")
    viewport_zoom: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, comment="뷰포트 줌")
    
    # 설정 및 메타데이터
    settings_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="플로우 설정 JSON")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="플로우 메타데이터 JSON")
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    @property
    def viewport(self) -> Dict[str, float]:
        """뷰포트 상태 반환"""
        return {
            "x": self.viewport_x,
            "y": self.viewport_y,
            "zoom": self.viewport_zoom
        }
    
    @viewport.setter
    def viewport(self, value: Dict[str, float]) -> None:
        """뷰포트 상태 설정"""
        self.viewport_x = value.get("x", 0.0)
        self.viewport_y = value.get("y", 0.0)
        self.viewport_zoom = value.get("zoom", 1.0)
    
    @property
    def settings(self) -> Dict[str, Any]:
        """플로우 설정 반환"""
        if self.settings_json:
            return json.loads(self.settings_json)
        return {}
    
    @settings.setter
    def settings(self, value: Dict[str, Any]) -> None:
        """플로우 설정 설정"""
        self.settings_json = json.dumps(value) if value else None
    
    @property
    def flow_metadata(self) -> Dict[str, Any]:
        """플로우 메타데이터 반환"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
    
    @flow_metadata.setter
    def flow_metadata(self, value: Dict[str, Any]) -> None:
        """플로우 메타데이터 설정"""
        self.metadata_json = json.dumps(value) if value else None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "viewport": self.viewport,
            "settings": self.settings,
            "metadata": self.flow_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
