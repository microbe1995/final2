# ============================================================================
# 📋 Constants - 공통 상수들
# ============================================================================

"""
공통 상수들

애플리케이션에서 사용되는 기본값, 제한값, 설정값 등을 정의합니다.
"""

# ============================================================================
# 🎨 색상 관련 상수
# ============================================================================

# 기본 색상 팔레트
DEFAULT_COLORS = {
    "primary": "#3B82F6",      # 파란색
    "secondary": "#6B7280",    # 회색
    "success": "#10B981",      # 초록색
    "warning": "#F59E0B",      # 주황색
    "danger": "#EF4444",       # 빨간색
    "info": "#06B6D4",         # 청록색
    "light": "#F3F4F6",        # 밝은 회색
    "dark": "#1F2937",         # 어두운 회색
    "white": "#FFFFFF",        # 흰색
    "black": "#000000",        # 검은색
    "transparent": "transparent"  # 투명
}

# 색상 그룹
COLOR_GROUPS = {
    "warm": ["#FF6B6B", "#FF8E53", "#FFA726", "#FFB74D", "#FFCC02"],
    "cool": ["#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"],
    "neutral": ["#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA", "#ADB5BD"]
}

# ============================================================================
# 📏 크기 및 차원 관련 상수
# ============================================================================

# 최대/최소 크기 제한
MAX_DIMENSIONS = {
    "width": 10000,
    "height": 10000,
    "min_width": 1,
    "min_height": 1
}

# 기본 Canvas 크기
DEFAULT_CANVAS_SIZES = {
    "small": {"width": 800, "height": 600},
    "medium": {"width": 1200, "height": 800},
    "large": {"width": 1600, "height": 1200},
    "extra_large": {"width": 2000, "height": 1500}
}

# 기본 도형 크기
DEFAULT_SHAPE_SIZES = {
    "small": {"width": 50, "height": 50},
    "medium": {"width": 100, "height": 100},
    "large": {"width": 200, "height": 200}
}

# ============================================================================
# 🔢 수치 관련 상수
# ============================================================================

# 각도 관련
ANGLE_LIMITS = {
    "min": -360,
    "max": 360,
    "default": 0
}

# 확대/축소 관련
ZOOM_LIMITS = {
    "min": 0.1,
    "max": 5.0,
    "default": 1.0,
    "step": 0.1
}

# 투명도 관련
OPACITY_LIMITS = {
    "min": 0.0,
    "max": 1.0,
    "default": 1.0,
    "step": 0.1
}

# ============================================================================
# 📁 파일 및 형식 관련 상수
# ============================================================================

# 지원되는 내보내기 형식
SUPPORTED_FORMATS = {
    "image": ["png", "jpg", "jpeg", "svg", "webp"],
    "document": ["pdf", "html"],
    "data": ["json", "xml", "csv"]
}

# 파일 크기 제한 (바이트)
FILE_SIZE_LIMITS = {
    "max_upload": 10 * 1024 * 1024,  # 10MB
    "max_export": 50 * 1024 * 1024,  # 50MB
    "max_import": 20 * 1024 * 1024   # 20MB
}

# 파일명 제한
FILENAME_LIMITS = {
    "max_length": 255,
    "allowed_chars": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
}

# ============================================================================
# ⚡ 성능 관련 상수
# ============================================================================

# 페이지네이션 기본값
PAGINATION_DEFAULTS = {
    "default_page": 1,
    "default_size": 20,
    "max_size": 100,
    "min_size": 1
}

# 캐시 관련
CACHE_SETTINGS = {
    "default_ttl": 300,        # 5분
    "max_ttl": 3600,          # 1시간
    "min_ttl": 60             # 1분
}

# 타임아웃 관련
TIMEOUT_SETTINGS = {
    "request_timeout": 30,     # 30초
    "database_timeout": 10,    # 10초
    "file_operation_timeout": 60  # 60초
}

# ============================================================================
# 🔐 보안 관련 상수
# ============================================================================

# API 키 관련
API_KEY_SETTINGS = {
    "min_length": 32,
    "max_length": 128,
    "expiration_days": 365
}

# 비밀번호 관련
PASSWORD_SETTINGS = {
    "min_length": 8,
    "max_length": 128,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special_chars": True
}

# ============================================================================
# 🌐 네트워크 관련 상수
# ============================================================================

# CORS 설정
CORS_SETTINGS = {
    "allowed_origins": ["*"],  # 프로덕션에서는 특정 도메인으로 제한
    "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allowed_headers": ["*"],
    "max_age": 86400  # 24시간
}

# 요청 제한
RATE_LIMIT_SETTINGS = {
    "requests_per_minute": 100,
    "requests_per_hour": 1000,
    "burst_limit": 20
}

# ============================================================================
# 📊 로깅 관련 상수
# ============================================================================

# 로그 레벨
LOG_LEVELS = {
    "debug": "DEBUG",
    "info": "INFO",
    "warning": "WARNING",
    "error": "ERROR",
    "critical": "CRITICAL"
}

# 로그 포맷
LOG_FORMATS = {
    "default": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    "simple": "{time:HH:mm:ss} | {level} | {message}",
    "json": '{"time": "{time:YYYY-MM-DD HH:mm:ss}", "level": "{level}", "message": "{message}"}'
}

# ============================================================================
# 🎯 비즈니스 로직 관련 상수
# ============================================================================

# 도형 타입별 기본 설정
SHAPE_DEFAULTS = {
    "rectangle": {
        "default_width": 100,
        "default_height": 100,
        "default_color": DEFAULT_COLORS["primary"]
    },
    "circle": {
        "default_radius": 50,
        "default_color": DEFAULT_COLORS["success"]
    },
    "triangle": {
        "default_width": 100,
        "default_height": 100,
        "default_color": DEFAULT_COLORS["warning"]
    }
}

# 화살표 타입별 기본 설정
ARROW_DEFAULTS = {
    "straight": {
        "default_stroke_width": 2,
        "default_color": DEFAULT_COLORS["danger"]
    },
    "curved": {
        "default_stroke_width": 2,
        "default_color": DEFAULT_COLORS["info"]
    }
}

# Canvas 템플릿 타입
CANVAS_TEMPLATES = {
    "flowchart": "플로우차트",
    "diagram": "다이어그램",
    "mindmap": "마인드맵",
    "network": "네트워크",
    "custom": "사용자 정의"
}
