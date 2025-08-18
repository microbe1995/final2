# ============================================================================
# ➡️ Arrow Entity - 화살표 엔티티
# ============================================================================

from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

class ArrowType(str, Enum):
    """화살표 타입 열거형"""
    STRAIGHT = "straight"      # 직선 화살표
    CURVED = "curved"          # 곡선 화살표
    BIDIRECTIONAL = "bidirectional"  # 양방향 화살표
    DASHED = "dashed"          # 점선 화살표

class Arrow:
    """화살표를 표현하는 엔티티 클래스"""
    
    def __init__(
        self,
        id: str,
        type: ArrowType,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        color: str = "#EF4444",
        stroke_width: int = 3,
        arrow_size: float = 10.0,
        is_dashed: bool = False,
        dash_pattern: Optional[List[float]] = None,
        control_points: Optional[List[Tuple[float, float]]] = None,
        canvas_id: str = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.type = type
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.color = color
        self.stroke_width = stroke_width
        self.arrow_size = arrow_size
        self.is_dashed = is_dashed
        self.dash_pattern = dash_pattern or [5, 5]
        self.control_points = control_points or []
        self.canvas_id = canvas_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
    
    def move(self, dx: float, dy: float) -> None:
        """화살표를 이동시킵니다"""
        self.start_x += dx
        self.start_y += dy
        self.end_x += dx
        self.end_y += dy
        self.updated_at = datetime.utcnow()
    
    def resize(self, new_start_x: float, new_start_y: float, 
               new_end_x: float, new_end_y: float) -> None:
        """화살표의 크기와 위치를 변경합니다"""
        self.start_x = new_start_x
        self.start_y = new_start_y
        self.end_x = new_end_x
        self.end_y = new_end_y
        self.updated_at = datetime.utcnow()
    
    def change_color(self, new_color: str) -> None:
        """화살표의 색상을 변경합니다"""
        self.color = new_color
        self.updated_at = datetime.utcnow()
    
    def get_length(self) -> float:
        """화살표의 길이를 계산합니다"""
        import math
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return math.sqrt(dx * dx + dy * dy)
    
    def get_angle(self) -> float:
        """화살표의 각도를 계산합니다 (라디안)"""
        import math
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return math.atan2(dy, dx)
    
    def get_center(self) -> Tuple[float, float]:
        """화살표의 중심점을 반환합니다"""
        return ((self.start_x + self.end_x) / 2, (self.start_y + self.end_y) / 2)
    
    def add_control_point(self, x: float, y: float) -> None:
        """곡선 화살표에 제어점을 추가합니다"""
        if self.type == ArrowType.CURVED:
            self.control_points.append((x, y))
            self.updated_at = datetime.utcnow()
    
    def set_dash_pattern(self, pattern: List[float]) -> None:
        """점선 패턴을 설정합니다"""
        self.dash_pattern = pattern
        self.is_dashed = True
        self.updated_at = datetime.utcnow()
    
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
            "stroke_width": self.stroke_width,
            "arrow_size": self.arrow_size,
            "is_dashed": self.is_dashed,
            "dash_pattern": self.dash_pattern,
            "control_points": self.control_points,
            "canvas_id": self.canvas_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Arrow':
        """딕셔너리에서 화살표를 생성합니다"""
        return cls(
            id=data["id"],
            type=ArrowType(data["type"]),
            start_x=data["start_x"],
            start_y=data["start_y"],
            end_x=data["end_x"],
            end_y=data["end_y"],
            color=data.get("color", "#EF4444"),
            stroke_width=data.get("stroke_width", 3),
            arrow_size=data.get("arrow_size", 10.0),
            is_dashed=data.get("is_dashed", False),
            dash_pattern=data.get("dash_pattern", [5, 5]),
            control_points=data.get("control_points", []),
            canvas_id=data.get("canvas_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            metadata=data.get("metadata", {})
        )
