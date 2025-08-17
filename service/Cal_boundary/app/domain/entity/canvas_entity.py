# ============================================================================
# 🎨 Canvas Entity - Canvas 엔티티
# ============================================================================

from datetime import datetime
from typing import Optional, Dict, Any, List
from .shape_entity import Shape
from .arrow_entity import Arrow

class Canvas:
    """Canvas를 표현하는 엔티티 클래스"""
    
    def __init__(
        self,
        id: str,
        name: str,
        width: float = 800.0,
        height: float = 600.0,
        background_color: str = "#FFFFFF",
        shapes: Optional[List[Shape]] = None,
        arrows: Optional[List[Arrow]] = None,
        # React Flow 데이터 지원
        nodes: Optional[List[Dict[str, Any]]] = None,
        edges: Optional[List[Dict[str, Any]]] = None,
        zoom_level: float = 1.0,
        pan_x: float = 0.0,
        pan_y: float = 0.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.background_color = background_color
        self.shapes = shapes or []
        self.arrows = arrows or []
        # React Flow 데이터
        self.nodes = nodes or []
        self.edges = edges or []
        self.zoom_level = zoom_level
        self.pan_x = pan_x
        self.pan_y = pan_y
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.metadata = metadata or {}
    
    def add_shape(self, shape: Shape) -> None:
        """Canvas에 도형을 추가합니다"""
        shape.canvas_id = self.id
        self.shapes.append(shape)
        self.updated_at = datetime.utcnow()
    
    def remove_shape(self, shape_id: str) -> bool:
        """Canvas에서 도형을 제거합니다"""
        for i, shape in enumerate(self.shapes):
            if shape.id == shape_id:
                del self.shapes[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def add_arrow(self, arrow: Arrow) -> None:
        """Canvas에 화살표를 추가합니다"""
        arrow.canvas_id = self.id
        self.arrows.append(arrow)
        self.updated_at = datetime.utcnow()
    
    def remove_arrow(self, arrow_id: str) -> bool:
        """Canvas에서 화살표를 제거합니다"""
        for i, arrow in enumerate(self.arrows):
            if arrow.id == arrow_id:
                del self.arrows[i]
                self.updated_at = datetime.utcnow()
                return True
        return False
    
    def get_shape_by_id(self, shape_id: str) -> Optional[Shape]:
        """ID로 도형을 찾습니다"""
        for shape in self.shapes:
            if shape.id == shape_id:
                return shape
        return None
    
    def get_arrow_by_id(self, arrow_id: str) -> Optional[Arrow]:
        """ID로 화살표를 찾습니다"""
        for arrow in self.arrows:
            if arrow.id == arrow_id:
                return arrow
        return None
    
    def get_elements_at_point(self, x: float, y: float) -> List[Any]:
        """주어진 점에 있는 모든 요소를 반환합니다"""
        elements = []
        
        # 도형 검사
        for shape in self.shapes:
            if shape.contains_point(x, y):
                elements.append(shape)
        
        # 화살표 검사 (간단한 거리 기반)
        for arrow in self.arrows:
            if self._point_near_line(x, y, arrow):
                elements.append(arrow)
        
        return elements
    
    def _point_near_line(self, x: float, y: float, arrow: Arrow, threshold: float = 5.0) -> bool:
        """점이 선 근처에 있는지 확인합니다"""
        import math
        
        # 선분과 점 사이의 최단 거리 계산
        A = x - arrow.start_x
        B = y - arrow.start_y
        C = arrow.end_x - arrow.start_x
        D = arrow.end_y - arrow.start_y
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            # 시작점과 끝점이 같은 경우
            return math.sqrt(A * A + B * B) <= threshold
        
        param = dot / len_sq
        
        if param < 0:
            xx, yy = arrow.start_x, arrow.start_y
        elif param > 1:
            xx, yy = arrow.end_x, arrow.end_y
        else:
            xx = arrow.start_x + param * C
            yy = arrow.start_y + param * D
        
        dx = x - xx
        dy = y - yy
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= threshold
    
    def clear(self) -> None:
        """Canvas의 모든 요소를 제거합니다 - React Flow 지원"""
        self.shapes.clear()
        self.arrows.clear()
        # React Flow 데이터 정리
        self.nodes.clear()
        self.edges.clear()
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
        if not self.shapes and not self.arrows and not self.nodes and not self.edges:
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
        
        # React Flow 엣지 경계 계산
        for edge in self.edges:
            # 엣지는 노드 위치에 따라 경계가 결정되므로 별도 계산 불필요
            pass
        
        # 도형 경계 계산 (하위 호환성)
        for shape in self.shapes:
            min_x = min(min_x, shape.x)
            min_y = min(min_y, shape.y)
            max_x = max(max_x, shape.x + shape.width)
            max_y = max(max_y, shape.y + shape.height)
        
        # 화살표 경계 계산 (하위 호환성)
        for arrow in self.arrows:
            min_x = min(min_x, arrow.start_x, arrow.end_x)
            min_y = min(min_y, arrow.start_y, arrow.end_y)
            max_x = max(max_x, arrow.start_x, arrow.end_x)
            max_y = max(max_y, arrow.start_y, arrow.end_y)
        
        return {
            "min_x": min_x,
            "min_y": min_y,
            "max_x": max_x,
            "max_y": max_y
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Canvas를 딕셔너리로 변환합니다 - React Flow 지원"""
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "background_color": self.background_color,
            # React Flow 데이터
            "nodes": self.nodes,
            "edges": self.edges,
            # 기존 데이터 (하위 호환성)
            "shapes": [shape.to_dict() for shape in self.shapes],
            "arrows": [arrow.to_dict() for arrow in self.arrows],
            "zoom_level": self.zoom_level,
            "pan_x": self.pan_x,
            "pan_y": self.pan_y,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Canvas':
        """딕셔너리에서 Canvas를 생성합니다 - React Flow 지원"""
        from .shape_entity import Shape
        from .arrow_entity import Arrow
        
        return cls(
            id=data["id"],
            name=data["name"],
            width=data.get("width", 800.0),
            height=data.get("height", 600.0),
            background_color=data.get("background_color", "#FFFFFF"),
            # React Flow 데이터
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            # 기존 데이터 (하위 호환성)
            shapes=[Shape.from_dict(shape_data) for shape_data in data.get("shapes", [])],
            arrows=[Arrow.from_dict(arrow_data) for arrow_data in data.get("arrows", [])],
            zoom_level=data.get("zoom_level", 1.0),
            pan_x=data.get("pan_x", 0.0),
            pan_y=data.get("pan_y", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            metadata=data.get("metadata", {})
        )
