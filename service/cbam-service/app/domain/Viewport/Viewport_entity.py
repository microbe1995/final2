# ============================================================================
# 🖱️ Viewport Entity - ReactFlow 뷰포트 엔티티
# ============================================================================

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.common.database_base import Base

class ReactFlowViewport(Base):
    """ReactFlow 뷰포트 상태를 표현하는 엔티티"""
    __tablename__ = "reactflow_viewports"
    
    # 기본 필드
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("reactflow_states.id"), nullable=False, comment="플로우 ID")
    
    # 뷰포트 상태
    x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="뷰포트 X 좌표")
    y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="뷰포트 Y 좌표")
    zoom: Mapped[float] = mapped_column(Float, nullable=False, default=1.0, comment="뷰포트 줌 레벨")
    
    # 뷰포트 설정
    min_zoom: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.1, comment="최소 줌 레벨")
    max_zoom: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=5.0, comment="최대 줌 레벨")
    pan_enabled: Mapped[bool] = mapped_column(String(5), nullable=False, default="true", comment="팬 활성화 여부")
    zoom_enabled: Mapped[bool] = mapped_column(String(5), nullable=False, default="true", comment="줌 활성화 여부")
    
    # 뷰포트 메타데이터
    settings_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="뷰포트 설정 JSON")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="뷰포트 메타데이터 JSON")
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 관계 설정
    flow = relationship("ReactFlowState", back_populates="viewport")
    
    @property
    def viewport_state(self) -> Dict[str, float]:
        """뷰포트 상태 반환"""
        return {
            "x": self.x,
            "y": self.y,
            "zoom": self.zoom
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
            "minZoom": self.min_zoom or 0.1,
            "maxZoom": self.max_zoom or 5.0,
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
        return f"<ReactFlowViewport(id={self.id}, flow_id={self.flow_id}, x={self.x}, y={self.y}, zoom={self.zoom})>"
