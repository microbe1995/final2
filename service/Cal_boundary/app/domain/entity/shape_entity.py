# ============================================================================
# 🎨 Shape Entity - 도형 엔티티
# ============================================================================

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class ShapeType(str, Enum):
    """도형 타입 열거형"""
    RECTANGLE = "rectangle"    # 사각형
    CIRCLE = "circle"          # 원
    TRIANGLE = "triangle"      # 삼각형
    ELLIPSE = "ellipse"        # 타원
    POLYGON = "polygon"        # 다각형

class Shape:
    """도형을 표현하는 엔티티 클래스"""
    
    def __init__(
        self,
        id: str,
        type: ShapeType,
        x: float,
        y: float,
        width: float,
        height: float,
        color: str = "#3B82F6",
        stroke_width: int = 2,
        fill_color: Optional[str] = None,
        rotation: float = 0.0,
        opacity: float = 1.0,
        canvas_id: str = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.stroke_width = stroke_width
        self.fill_color = fill_color or color
        self.rotation = rotation
        self.opacity = opacity
        self.canvas_id = canvas_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
    
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
    
    def change_color(self, new_color: str) -> None:
        """도형의 색상을 변경합니다"""
        self.color = new_color
        self.updated_at = datetime.utcnow()
    
    def get_center(self) -> tuple[float, float]:
        """도형의 중심점을 반환합니다"""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def contains_point(self, point_x: float, point_y: float) -> bool:
        """주어진 점이 도형 내부에 있는지 확인합니다"""
        return (self.x <= point_x <= self.x + self.width and 
                self.y <= point_y <= self.y + self.height)
    
    def to_dict(self) -> Dict[str, Any]:
        """도형을 딕셔너리로 변환합니다"""
        return {
            "id": self.id,
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
            "stroke_width": self.stroke_width,
            "fill_color": self.fill_color,
            "rotation": self.rotation,
            "opacity": self.opacity,
            "canvas_id": self.canvas_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shape':
        """딕셔너리에서 도형을 생성합니다"""
        return cls(
            id=data["id"],
            type=ShapeType(data["type"]),
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            color=data.get("color", "#3B82F6"),
            stroke_width=data.get("stroke_width", 2),
            fill_color=data.get("fill_color"),
            rotation=data.get("rotation", 0.0),
            opacity=data.get("opacity", 1.0),
            canvas_id=data.get("canvas_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            metadata=data.get("metadata", {})
        )
