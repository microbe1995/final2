# ============================================================================
# ➡️ Arrow Entity - 화살표 엔티티 (SQLAlchemy 모델)
# ============================================================================

import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
from sqlalchemy import String, Float, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.ext.declarative import declarative_base

# Arrow 도메인 전용 Base
Base = declarative_base()

class ArrowType(str, Enum):
    """화살표 타입 열거형"""
    STRAIGHT = "straight"      # 직선 화살표
    CURVED = "curved"          # 곡선 화살표
    BIDIRECTIONAL = "bidirectional"  # 양방향 화살표
    DASHED = "dashed"          # 점선 화살표

class Arrow(Base):
    """화살표를 표현하는 엔티티 클래스 (SQLAlchemy 모델)"""
    __tablename__ = "arrows"
    
    # Arrow 관련 상수들 (구 utility에서 이동)
    ARROW_COLORS = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
    MAX_ARROW_LENGTH = 5000
    MIN_ARROW_LENGTH = 1
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    type: Mapped[ArrowType] = mapped_column(SQLEnum(ArrowType), nullable=False)
    
    # 시작점과 끝점
    start_x: Mapped[float] = mapped_column(Float, nullable=False)
    start_y: Mapped[float] = mapped_column(Float, nullable=False)
    end_x: Mapped[float] = mapped_column(Float, nullable=False)
    end_y: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 스타일
    color: Mapped[str] = mapped_column(String(16), nullable=False, default="#000000")
    width: Mapped[float] = mapped_column(Float, nullable=False, default=2.0)
    opacity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # 관련 정보
    canvas_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Arrow")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 메타데이터
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """메타데이터"""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}
    
    @metadata.setter
    def metadata(self, value: Dict[str, Any]) -> None:
        """메타데이터 설정"""
        self.metadata_json = json.dumps(value) if value else None
    
    def move(self, dx: float, dy: float) -> None:
        """화살표를 이동시킵니다"""
        self.start_x += dx
        self.start_y += dy
        self.end_x += dx
        self.end_y += dy
        self.updated_at = datetime.utcnow()
    
    def set_points(self, new_start_x: float, new_start_y: float, new_end_x: float, new_end_y: float) -> None:
        """화살표의 시작점과 끝점을 설정합니다"""
        self.start_x = new_start_x
        self.start_y = new_start_y
        self.end_x = new_end_x
        self.end_y = new_end_y
        self.updated_at = datetime.utcnow()
    
    def get_length(self) -> float:
        """화살표의 길이를 계산합니다"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return (dx * dx + dy * dy) ** 0.5
    
    def get_angle(self) -> float:
        """화살표의 각도를 계산합니다 (라디안)"""
        import math
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return math.atan2(dy, dx)
    
    def get_center(self) -> Tuple[float, float]:
        """화살표의 중심점을 반환합니다"""
        return ((self.start_x + self.end_x) / 2, (self.start_y + self.end_y) / 2)
    
    # ============================================================================
    # 🔧 유틸리티 메서드들 (구 utility에서 이동)
    # ============================================================================
    
    def validate_color(self, color: str) -> bool:
        """색상 값의 유효성을 검증합니다"""
        if not color or not isinstance(color, str):
            return False
        
        color_patterns = [
            r'^#[0-9A-Fa-f]{3}$',      # #RGB
            r'^#[0-9A-Fa-f]{6}$',      # #RRGGBB
            r'^#[0-9A-Fa-f]{8}$',      # #RRGGBBAA
        ]
        
        return any(re.match(pattern, color) for pattern in color_patterns)
    
    def validate_coordinates(self, x: float, y: float) -> bool:
        """좌표의 유효성을 검증합니다"""
        return isinstance(x, (int, float)) and isinstance(y, (int, float))
    
    def validate_arrow_length(self) -> bool:
        """화살표 길이의 유효성을 검증합니다"""
        length = self.get_length()
        return self.MIN_ARROW_LENGTH <= length <= self.MAX_ARROW_LENGTH
    
    # SQLAlchemy 검증자들
    @validates('color')
    def validate_arrow_color(self, key, color):
        """색상 검증"""
        if not self.validate_color(color):
            raise ValueError(f"Invalid color: {color}")
        return color
    
    @validates('start_x', 'start_y', 'end_x', 'end_y')
    def validate_arrow_coordinates(self, key, value):
        """좌표 검증"""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid {key}: {value}")
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """화살표를 딕셔너리로 변환합니다"""
        return {
            "id": self.id,
            "type": self.type.value,
            "start_x": self.start_x,
            "start_y": self.start_y,
            "end_x": self.end_x,
            "end_y": self.end_y,
            "color": self.color,
            "width": self.width,
            "opacity": self.opacity,
            "canvas_id": self.canvas_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Arrow':
        """딕셔너리에서 화살표를 생성합니다"""
        arrow = cls(
            id=data["id"],
            type=ArrowType(data["type"]),
            start_x=data["start_x"],
            start_y=data["start_y"],
            end_x=data["end_x"],
            end_y=data["end_y"],
            color=data.get("color", "#000000"),
            width=data.get("width", 2.0),
            opacity=data.get("opacity", 1.0),
            canvas_id=data.get("canvas_id"),
            name=data.get("name", "Arrow"),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
        
        arrow.metadata = data.get("metadata", {})
        return arrow