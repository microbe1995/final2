# ============================================================================
# 🖱️ Viewport Entity - ReactFlow 뷰포트 엔티티
# ============================================================================

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Viewport(Base):
    """뷰포트 상태를 표현하는 엔티티"""
    __tablename__ = "reactflow_viewports"
    
    # 기본 키
    id: Mapped[str] = mapped_column(Text, primary_key=True, index=True, comment="뷰포트 고유 ID")
    flow_id: Mapped[str] = mapped_column(Text, ForeignKey("reactflow_states.id"), nullable=False, comment="플로우 ID")
    
    # 뷰포트 위치 및 줌
    x: Mapped[float] = mapped_column(Numeric, default=0, comment="X 좌표")
    y: Mapped[float] = mapped_column(Numeric, default=0, comment="Y 좌표")
    zoom: Mapped[float] = mapped_column(Numeric, default=1.0, comment="줌 레벨")
    
    # 뷰포트 제한 설정
    min_zoom: Mapped[float] = mapped_column(Numeric, default=0.1, comment="최소 줌 레벨")
    max_zoom: Mapped[float] = mapped_column(Numeric, default=4.0, comment="최대 줌 레벨")
    
    # 뷰포트 제어 설정
    pan_enabled: Mapped[str] = mapped_column(Text, default="true", comment="팬 활성화 여부")
    zoom_enabled: Mapped[str] = mapped_column(Text, default="true", comment="줌 활성화 여부")
    
    # 메타데이터
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="생성 시간")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시간")
    
    # 관계 설정
    flow = relationship("Flow", back_populates="viewport")
    
    @property
    def viewport_state(self) -> Dict[str, float]:
        """뷰포트 상태 반환"""
        return {
            "x": float(self.x) if self.x else 0.0,
            "y": float(self.y) if self.y else 0.0,
            "zoom": float(self.zoom) if self.zoom else 1.0
        }
    
    @viewport_state.setter
    def viewport_state(self, value: Dict[str, float]) -> None:
        """뷰포트 상태 설정"""
        self.x = value.get("x", 0.0)
        self.y = value.get("y", 0.0)
        self.zoom = value.get("zoom", 1.0)
    
    @property
    def viewport_settings(self) -> Dict[str, Any]:
        """뷰포트 설정 반환"""
        if self.settings_json:
            return json.loads(self.settings_json)
        return {
            "minZoom": float(self.min_zoom) if self.min_zoom else 0.1,
            "maxZoom": float(self.max_zoom) if self.max_zoom else 5.0,
            "panEnabled": self.pan_enabled == "true",
            "zoomEnabled": self.zoom_enabled == "true"
        }
    
    @viewport_settings.setter
    def viewport_settings(self, value: Dict[str, Any]) -> None:
        """뷰포트 설정 설정"""
        self.settings_json = json.dumps(value) if value else None
        
        # 개별 필드 업데이트
        if value:
            self.min_zoom = value.get("minZoom", 0.1)
            self.max_zoom = value.get("maxZoom", 5.0)
            self.pan_enabled = str(value.get("panEnabled", True)).lower()
            self.zoom_enabled = str(value.get("zoomEnabled", True)).lower()
    
    @property
    def viewport_metadata(self) -> Dict[str, Any]:
        """뷰포트 메타데이터 반환"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
    
    @viewport_metadata.setter
    def viewport_metadata(self, value: Dict[str, Any]) -> None:
        """뷰포트 메타데이터 설정"""
        self.metadata_json = json.dumps(value) if value else None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "flow_id": self.flow_id,
            "viewport": self.viewport_state,
            "settings": self.viewport_settings,
            "metadata": self.viewport_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Viewport(id={self.id}, flow_id={self.flow_id}, x={self.x}, y={self.y}, zoom={self.zoom})>"
