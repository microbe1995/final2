# ============================================================================
# 🌊 Flow Entity - ReactFlow 플로우 엔티티
# ============================================================================

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

# ============================================================================
# 🌊 플로우 엔티티
# ============================================================================

class Flow(Base):
    """플로우 엔티티"""
    
    __tablename__ = "reactflow_states"
    
    id: Mapped[str] = mapped_column(Text, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="플로우 이름")
    
    # 플로우 설정
    description = Column(Text, comment="플로우 설명")
    version = Column(Text, default="1.0.0", comment="플로우 버전")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
