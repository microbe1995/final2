# ============================================================================
# 🎨 Canvas Entity - Canvas 엔티티 (SQLAlchemy 모델)
# ============================================================================

import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, validates
from app.common.database_base import Base

class Canvas(Base):
    """Canvas를 표현하는 엔티티 클래스 (SQLAlchemy 모델)"""
    __tablename__ = "canvases"

    # Canvas 관련 상수들 (구 utility/constants.py에서 이동)
    DEFAULT_COLORS = {
        "primary": "#3B82F6", "secondary": "#6B7280", "success": "#10B981",
        "warning": "#F59E0B", "danger": "#EF4444", "info": "#06B6D4",
        "light": "#F3F4F6", "dark": "#1F2937", "white": "#FFFFFF",
        "black": "#000000", "transparent": "transparent"
    }
    
    MAX_DIMENSIONS = {
        "width": 10000, "height": 10000,
        "min_width": 100, "min_height": 100
    }
    
    SUPPORTED_FORMATS = {
        "export": ["json", "png", "svg", "pdf"],
        "import": ["json", "svg"]
    }

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    width: Mapped[float] = mapped_column(Float, nullable=False, default=1200.0)
    height: Mapped[float] = mapped_column(Float, nullable=False, default=800.0)
    background_color: Mapped[str] = mapped_column(String(16), nullable=False, default="#FFFFFF")

    zoom_level: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    pan_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    pan_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ReactFlow 데이터를 JSON으로 저장
    nodes_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edges_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    viewport_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) 
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    @property
    def nodes(self) -> List[Dict[str, Any]]:
        """React Flow 노드 데이터"""
        if self.nodes_json:
            return json.loads(self.nodes_json)
        return []
    
    @nodes.setter
    def nodes(self, value: List[Dict[str, Any]]) -> None:
        """React Flow 노드 데이터 설정"""
        self.nodes_json = json.dumps(value) if value else None
    
    @property
    def edges(self) -> List[Dict[str, Any]]:
        """ReactFlow 엣지 데이터"""
        if self.edges_json:
            return json.loads(self.edges_json)
        return []
    
    @edges.setter
    def edges(self, value: List[Dict[str, Any]]) -> None:
        """ReactFlow 엣지 데이터 설정"""
        self.edges_json = json.dumps(value) if value else None
    
    @property
    def viewport(self) -> Dict[str, Any]:
        """ReactFlow 뷰포트 데이터"""
        if self.viewport_json:
            return json.loads(self.viewport_json)
        return {"x": 0, "y": 0, "zoom": 1}
    
    @viewport.setter
    def viewport(self, value: Dict[str, Any]) -> None:
        """ReactFlow 뷰포트 데이터 설정"""
        self.viewport_json = json.dumps(value) if value else None
    
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
    
    # ============================================================================
    # 🔧 유틸리티 메서드들 (구 utility/validators.py에서 이동)
    # ============================================================================
    
    def validate_color(self, color: str) -> bool:
        """색상 값의 유효성을 검증합니다"""
        if not color or not isinstance(color, str):
            return False
        
        # 색상 패턴 검증
        color_patterns = [
            r'^#[0-9A-Fa-f]{3}$',      # #RGB
            r'^#[0-9A-Fa-f]{6}$',      # #RRGGBB
            r'^#[0-9A-Fa-f]{8}$',      # #RRGGBBAA
            r'^transparent$',           # transparent
        ]
        
        return any(re.match(pattern, color) for pattern in color_patterns)
    
    def validate_dimensions(self, width: float, height: float) -> bool:
        """Canvas 크기의 유효성을 검증합니다"""
        return (self.MAX_DIMENSIONS["min_width"] <= width <= self.MAX_DIMENSIONS["width"] and
                self.MAX_DIMENSIONS["min_height"] <= height <= self.MAX_DIMENSIONS["height"])
    
    def validate_zoom_level(self, zoom: float) -> bool:
        """줌 레벨의 유효성을 검증합니다"""
        return 0.1 <= zoom <= 5.0
    
    # SQLAlchemy 검증자들
    @validates('background_color')
    def validate_background_color(self, key, color):
        """배경색 검증"""
        if not self.validate_color(color):
            raise ValueError(f"Invalid background color: {color}")
        return color
    
    @validates('width', 'height')
    def validate_canvas_dimensions(self, key, value):
        """Canvas 크기 검증"""
        if key == 'width':
            if not (self.MAX_DIMENSIONS["min_width"] <= value <= self.MAX_DIMENSIONS["width"]):
                raise ValueError(f"Invalid width: {value}")
        elif key == 'height':
            if not (self.MAX_DIMENSIONS["min_height"] <= value <= self.MAX_DIMENSIONS["height"]):
                raise ValueError(f"Invalid height: {value}")
        return value
    
    @validates('zoom_level')
    def validate_zoom(self, key, zoom):
        """줌 레벨 검증"""
        if not self.validate_zoom_level(zoom):
            raise ValueError(f"Invalid zoom level: {zoom}")
        return zoom

    def clear(self) -> None:
        """Canvas의 모든 요소를 제거합니다 - ReactFlow 지원"""
        # ReactFlow 데이터 정리
        self.nodes = []
        self.edges = []
        self.viewport = {"x": 0, "y": 0, "zoom": 1}
        self.updated_at = datetime.utcnow()
    
    def resize(self, new_width: float, new_height: float) -> None:
        """Canvas의 크기를 변경합니다"""
        self.width = new_width
        self.height = new_height
        self.updated_at = datetime.utcnow()
    
    def set_zoom(self, zoom_level: float) -> None:
        """확대/축소 레벨을 설정합니다"""
        self.zoom_level = max(0.1, min(5.0, zoom_level))  # 0.1x ~ 5.0x 제한
        self.updated_at = datetime.utcnow()
    
    def pan(self, dx: float, dy: float) -> None:
        """Canvas를 이동시킵니다"""
        self.pan_x += dx
        self.pan_y += dy
        self.updated_at = datetime.utcnow()
    
    def get_bounds(self) -> Dict[str, float]:
        """Canvas의 경계를 계산합니다 - React Flow 지원"""
        if not self.nodes and not self.edges:
            return {"min_x": 0, "min_y": 0, "max_x": self.width, "max_y": self.height}
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # React Flow 노드 경계 계산
        for node in self.nodes:
            if 'position' in node:
                pos = node['position']
                min_x = min(min_x, pos.get('x', 0))
                min_y = min(min_y, pos.get('y', 0))
                max_x = max(max_x, pos.get('x', 0) + 200)  # 노드 기본 너비
                max_y = max(max_y, pos.get('y', 0) + 100)  # 노드 기본 높이
        
        return {
            "min_x": min_x if min_x != float('inf') else 0,
            "min_y": min_y if min_y != float('inf') else 0,
            "max_x": max_x if max_x != float('-inf') else self.width,
            "max_y": max_y if max_y != float('-inf') else self.height
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Canvas를 딕셔너리로 변환합니다 - React Flow 지원"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "width": self.width,
            "height": self.height,
            "background_color": self.background_color,
            # React Flow 데이터
            "nodes": self.nodes,
            "edges": self.edges,
            "zoom_level": self.zoom_level,
            "pan_x": self.pan_x,
            "pan_y": self.pan_y,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Canvas':
        """딕셔너리에서 Canvas를 생성합니다 - React Flow 지원"""
        canvas = cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            width=data.get("width", 1200.0),
            height=data.get("height", 800.0),
            background_color=data.get("background_color", "#FFFFFF"),
            zoom_level=data.get("zoom_level", 1.0),
            pan_x=data.get("pan_x", 0.0),
            pan_y=data.get("pan_y", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
        
        # React Flow 데이터 설정
        canvas.nodes = data.get("nodes", [])
        canvas.edges = data.get("edges", [])
        canvas.metadata = data.get("metadata", {})
        
        return canvas