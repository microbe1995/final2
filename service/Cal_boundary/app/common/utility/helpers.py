# ============================================================================
# 🛠️ Helpers - 공통 헬퍼 함수들
# ============================================================================

"""
공통 헬퍼 함수들

UUID 생성, 타임스탬프 포맷팅, 파일명 정리 등의 기능을 제공합니다.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from loguru import logger

def generate_uuid() -> str:
    """
    새로운 UUID를 생성합니다
    
    Returns:
        str: 생성된 UUID 문자열
    """
    return str(uuid.uuid4())

def format_timestamp(timestamp: Optional[datetime] = None, 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    타임스탬프를 포맷팅합니다
    
    Args:
        timestamp: 포맷팅할 타임스탬프 (None이면 현재 시간)
        format_str: 포맷 문자열
    
    Returns:
        str: 포맷팅된 타임스탬프 문자열
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    try:
        return timestamp.strftime(format_str)
    except Exception as e:
        logger.error(f"❌ 타임스탬프 포맷팅 실패: {str(e)}")
        return str(timestamp)

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    파일명을 정리하고 안전하게 만듭니다
    
    Args:
        filename: 정리할 파일명
        max_length: 최대 길이
    
    Returns:
        str: 정리된 파일명
    """
    if not filename:
        return "untitled"
    
    # 금지된 문자를 언더스코어로 대체
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 연속된 언더스코어를 하나로
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # 앞뒤 공백 및 언더스코어 제거
    sanitized = sanitized.strip(' _')
    
    # 길이 제한
    if len(sanitized) > max_length:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        if ext:
            sanitized = name[:max_length-len(ext)-1] + '.' + ext
        else:
            sanitized = sanitized[:max_length]
    
    return sanitized or "untitled"

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    두 점 사이의 유클리드 거리를 계산합니다
    
    Args:
        x1, y1: 첫 번째 점의 좌표
        x2, y2: 두 번째 점의 좌표
    
    Returns:
        float: 두 점 사이의 거리
    """
    try:
        import math
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    except Exception as e:
        logger.error(f"❌ 거리 계산 실패: {str(e)}")
        return 0.0

def normalize_angle(angle: float) -> float:
    """
    각도를 0~360도 범위로 정규화합니다
    
    Args:
        angle: 정규화할 각도 (도 단위)
    
    Returns:
        float: 정규화된 각도 (0~360도)
    """
    try:
        normalized = angle % 360
        return normalized if normalized >= 0 else normalized + 360
    except Exception as e:
        logger.error(f"❌ 각도 정규화 실패: {str(e)}")
        return 0.0

def interpolate_color(color1: str, color2: str, ratio: float) -> str:
    """
    두 색상 사이를 보간합니다
    
    Args:
        color1: 첫 번째 색상 (#RRGGBB)
        color2: 두 번째 색상 (#RRGGBB)
        ratio: 보간 비율 (0.0 ~ 1.0)
    
    Returns:
        str: 보간된 색상 (#RRGGBB)
    """
    try:
        # 색상 문자열을 RGB 값으로 변환
        def hex_to_rgb(hex_color: str) -> List[int]:
            hex_color = hex_color.lstrip('#')
            return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        
        def rgb_to_hex(rgb: List[int]) -> str:
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        # 색상 변환
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # 보간 계산
        interpolated = [
            int(rgb1[i] + (rgb2[i] - rgb1[i]) * ratio)
            for i in range(3)
        ]
        
        return rgb_to_hex(interpolated)
        
    except Exception as e:
        logger.error(f"❌ 색상 보간 실패: {str(e)}")
        return color1

def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    두 딕셔너리를 깊게 병합합니다
    
    Args:
        dict1: 첫 번째 딕셔너리
        dict2: 두 번째 딕셔너리
    
    Returns:
        Dict[str, Any]: 병합된 딕셔너리
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    리스트를 지정된 크기의 청크로 나눕니다
    
    Args:
        lst: 나눌 리스트
        chunk_size: 청크 크기
    
    Returns:
        List[List[Any]]: 청크로 나뉜 리스트
    """
    if chunk_size <= 0:
        return [lst]
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    안전한 나눗셈을 수행합니다 (0으로 나누기 방지)
    
    Args:
        numerator: 분자
        denominator: 분모
        default: 0으로 나눌 때 반환할 기본값
    
    Returns:
        float: 나눗셈 결과 또는 기본값
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception as e:
        logger.error(f"❌ 나눗셈 실패: {str(e)}")
        return default
