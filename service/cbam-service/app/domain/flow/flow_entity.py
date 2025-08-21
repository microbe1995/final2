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
    
    # 뷰포트 관련 필드 제거 (Viewport 도메인으로 분리됨)
    
    # 설정 및 메타데이터
    settings_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="플로우 설정 JSON")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="플로우 메타데이터 JSON")
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 뷰포트 관련 프로퍼티 제거 (Viewport 도메인으로 분리됨)
    
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
            # "viewport": self.viewport,  # 뷰포트 관련 필드 제거 (Viewport 도메인으로 분리됨)
            "settings": self.settings,
            "metadata": self.flow_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
