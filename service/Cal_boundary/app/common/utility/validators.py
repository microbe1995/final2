# ============================================================================
# ✅ Validators - 데이터 검증 유틸리티
# ============================================================================

"""
데이터 검증을 위한 유틸리티 함수들

색상, 좌표, 크기 등의 데이터 유효성을 검증합니다.
"""

import re
from typing import Tuple, Union
from loguru import logger

def validate_color(color: str) -> bool:
    """
    색상 값의 유효성을 검증합니다
    
    Args:
        color: 검증할 색상 값 (#RGB, #RRGGBB, #RRGGBBAA)
    
    Returns:
        bool: 유효한 색상이면 True, 아니면 False
    """
    if not color or not isinstance(color, str):
        return False
    
    # 색상 패턴 검증
    color_patterns = [
        r'^#[0-9A-Fa-f]{3}$',      # #RGB
        r'^#[0-9A-Fa-f]{6}$',      # #RRGGBB
        r'^#[0-9A-Fa-f]{8}$',      # #RRGGBBAA
    ]
    
    for pattern in color_patterns:
        if re.match(pattern, color):
            return True
    
    # CSS 색상 이름도 허용
    css_colors = {
        'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'black', 'white',
        'gray', 'grey', 'orange', 'purple', 'pink', 'brown', 'navy', 'teal'
    }
    
    if color.lower() in css_colors:
        return True
    
    logger.warning(f"⚠️ 잘못된 색상 형식: {color}")
    return False

def validate_coordinates(x: Union[int, float], y: Union[int, float]) -> bool:
    """
    좌표 값의 유효성을 검증합니다
    
    Args:
        x: X 좌표
        y: Y 좌표
    
    Returns:
        bool: 유효한 좌표이면 True, 아니면 False
    """
    try:
        x_val = float(x)
        y_val = float(y)
        
        # 좌표 범위 검증 (실용적인 범위)
        if not (-10000 <= x_val <= 10000) or not (-10000 <= y_val <= 10000):
            logger.warning(f"⚠️ 좌표 범위 초과: ({x_val}, {y_val})")
            return False
        
        return True
        
    except (ValueError, TypeError):
        logger.warning(f"⚠️ 잘못된 좌표 형식: ({x}, {y})")
        return False

def validate_dimensions(width: Union[int, float], height: Union[int, float]) -> bool:
    """
    크기 값의 유효성을 검증합니다
    
    Args:
        width: 너비
        height: 높이
    
    Returns:
        bool: 유효한 크기이면 True, 아니면 False
    """
    try:
        w_val = float(width)
        h_val = float(height)
        
        # 최소/최대 크기 검증
        if w_val <= 0 or h_val <= 0:
            logger.warning(f"⚠️ 크기는 0보다 커야 합니다: {w_val}x{h_val}")
            return False
        
        if w_val > 10000 or h_val > 10000:
            logger.warning(f"⚠️ 크기가 너무 큽니다: {w_val}x{h_val}")
            return False
        
        return True
        
    except (ValueError, TypeError):
        logger.warning(f"⚠️ 잘못된 크기 형식: {width}x{height}")
        return False

def validate_angle(angle: Union[int, float]) -> bool:
    """
    각도 값의 유효성을 검증합니다
    
    Args:
        angle: 검증할 각도 (도 단위)
    
    Returns:
        bool: 유효한 각도이면 True, 아니면 False
    """
    try:
        angle_val = float(angle)
        
        # 각도 범위 검증 (-360 ~ 360도)
        if not (-360 <= angle_val <= 360):
            logger.warning(f"⚠️ 각도 범위 초과: {angle_val}도")
            return False
        
        return True
        
    except (ValueError, TypeError):
        logger.warning(f"⚠️ 잘못된 각도 형식: {angle}")
        return False

def validate_uuid(uuid_str: str) -> bool:
    """
    UUID 문자열의 유효성을 검증합니다
    
    Args:
        uuid_str: 검증할 UUID 문자열
    
    Returns:
        bool: 유효한 UUID이면 True, 아니면 False
    """
    if not uuid_str or not isinstance(uuid_str, str):
        return False
    
    # UUID v4 패턴 검증
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    
    if re.match(uuid_pattern, uuid_str.lower()):
        return True
    
    logger.warning(f"⚠️ 잘못된 UUID 형식: {uuid_str}")
    return False

def validate_filename(filename: str) -> bool:
    """
    파일명의 유효성을 검증합니다
    
    Args:
        filename: 검증할 파일명
    
    Returns:
        bool: 유효한 파일명이면 True, 아니면 False
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # 금지된 문자들
    forbidden_chars = r'[<>:"/\\|?*]'
    
    if re.search(forbidden_chars, filename):
        logger.warning(f"⚠️ 파일명에 금지된 문자가 포함됨: {filename}")
        return False
    
    # 길이 제한
    if len(filename) > 255:
        logger.warning(f"⚠️ 파일명이 너무 깁니다: {len(filename)}자")
        return False
    
    return True
