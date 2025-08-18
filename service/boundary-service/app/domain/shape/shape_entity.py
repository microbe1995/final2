# ============================================================================
# 🎨 Shape Entity - 도형 엔티티 (SQLAlchemy 모델)
# ============================================================================

import json
import re
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import String, Float, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.common.database_base import Base

class ShapeType(str, Enum):
    """도형 타입 열거형"""
    RECTANGLE = "rectangle"    # 사각형
    CIRCLE = "circle"          # 원
    TRIANGLE = "triangle"      # 삼각형
    ELLIPSE = "ellipse"        # 타원
    POLYGON = "polygon"        # 다각형

class Shape(Base):
    """도형을 표현하는 엔티티 클래스 (SQLAlchemy 모델)"""
    __tablename__ = "shapes"
    
    # Shape 관련 상수들 (구 utility에서 이동)
    SHAPE_COLORS = {
        "fill": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
        "stroke": ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"]
    }
    
    MAX_SHAPE_SIZE = {
        "width": 2000, "height": 2000,
        "min_width": 1, "min_height": 1
    }
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    type: Mapped[ShapeType] = mapped_column(SQLEnum(ShapeType), nullable=False)
    
    # 위치 및 크기
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    
    # 스타일
    fill_color: Mapped[str] = mapped_column(String(16), nullable=False, default="#FFFFFF")
    stroke_color: Mapped[str] = mapped_column(String(16), nullable=False, default="#000000")
    stroke_width: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    opacity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # 회전 및 변형
    rotation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    scale_x: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    scale_y: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    # 관련 정보
    canvas_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Shape")
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
        """도형을 이동시킵니다"""
        self.x += dx
        self.y += dy
        self.updated_at = datetime.utcnow()
    
    def resize(self, new_width: float, new_height: float) -> None:
        """도형의 크기를 변경합니다"""
        self.width = new_width
        self.height = new_height
        self.updated_at = datetime.utcnow()
    
    def rotate(self, angle: float) -> None:
        """도형을 회전시킵니다"""
        self.rotation = (self.rotation + angle) % 360
        self.updated_at = datetime.utcnow()
    
    def scale(self, scale_x: float, scale_y: float) -> None:
        """도형을 확대/축소합니다"""
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.updated_at = datetime.utcnow()
    
    def contains_point(self, point_x: float, point_y: float) -> bool:
        """점이 도형 내부에 있는지 확인합니다"""
        return (self.x <= point_x <= self.x + self.width and 
                self.y <= point_y <= self.y + self.height)
    
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
            r'^transparent$',           # transparent
        ]
        
        return any(re.match(pattern, color) for pattern in color_patterns)
    
    def validate_coordinates(self, x: float, y: float) -> bool:
        """좌표의 유효성을 검증합니다"""
        return isinstance(x, (int, float)) and isinstance(y, (int, float))
    
    def validate_shape_dimensions(self, width: float, height: float) -> bool:
        """도형 크기의 유효성을 검증합니다"""
        return (self.MAX_SHAPE_SIZE["min_width"] <= width <= self.MAX_SHAPE_SIZE["width"] and
                self.MAX_SHAPE_SIZE["min_height"] <= height <= self.MAX_SHAPE_SIZE["height"])
    
    # SQLAlchemy 검증자들
    @validates('fill_color', 'stroke_color')
    def validate_colors(self, key, color):
        """색상 검증"""
        if not self.validate_color(color):
            raise ValueError(f"Invalid {key}: {color}")
        return color
    
    @validates('x', 'y')
    def validate_position(self, key, value):
        """위치 검증"""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid {key}: {value}")
        return value
    
    @validates('width', 'height')
    def validate_size(self, key, value):
        """크기 검증"""
        if key == 'width':
            if not (self.MAX_SHAPE_SIZE["min_width"] <= value <= self.MAX_SHAPE_SIZE["width"]):
                raise ValueError(f"Invalid width: {value}")
        elif key == 'height':
            if not (self.MAX_SHAPE_SIZE["min_height"] <= value <= self.MAX_SHAPE_SIZE["height"]):
                raise ValueError(f"Invalid height: {value}")
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """도형을 딕셔너리로 변환합니다"""
        return {
            "id": self.id,
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "fill_color": self.fill_color,
            "stroke_color": self.stroke_color,
            "stroke_width": self.stroke_width,
            "opacity": self.opacity,
            "rotation": self.rotation,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "canvas_id": self.canvas_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shape':
        """딕셔너리에서 도형을 생성합니다"""
        shape = cls(
            id=data["id"],
            type=ShapeType(data["type"]),
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            fill_color=data.get("fill_color", "#FFFFFF"),
            stroke_color=data.get("stroke_color", "#000000"),
            stroke_width=data.get("stroke_width", 1.0),
            opacity=data.get("opacity", 1.0),
            rotation=data.get("rotation", 0.0),
            scale_x=data.get("scale_x", 1.0),
            scale_y=data.get("scale_y", 1.0),
            canvas_id=data.get("canvas_id"),
            name=data.get("name", "Shape"),
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
        
        shape.metadata = data.get("metadata", {})
        return shape