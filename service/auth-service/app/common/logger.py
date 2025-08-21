import json
import logging
import logging.handlers
from typing import Any, Dict, List, Union
from app.common.settings import settings

# 민감한 키들 정의
SENSITIVE_KEYS = {
    "password", "passwd", "pwd", "secret", "token", 
    "authorization", "access_token", "refresh_token"
}

def mask_payload(data: Any) -> Any:
    """민감한 정보를 마스킹하는 함수 (재귀적 처리)"""
    if isinstance(data, dict):
        masked_data = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_KEYS:
                masked_data[key] = "***MASKED***"
            else:
                masked_data[key] = mask_payload(value)
        return masked_data
    elif isinstance(data, list):
        return [mask_payload(item) for item in data]
    else:
        return data

def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 생성"""
    logger = logging.getLogger(name)
    
    # 이미 핸들러가 설정되어 있으면 중복 설정 방지
    if logger.handlers:
        return logger
    
    # 로그 레벨 설정
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 스트림 핸들러 생성
    handler = logging.StreamHandler()
    
    # 포맷터 설정
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(handler)
    
    return logger

class LoggingMiddleware:
    """요청/응답 로깅 미들웨어"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("auth_service.middleware")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # HTTP 요청인 경우에만 로깅
            request = type('Request', (), {
                'method': scope.get('method', ''),
                'url': type('URL', (), {'path': scope.get('path', '')})(),
                'query_params': scope.get('query_string', b'').decode() if scope.get('query_string') else '',
                'headers': dict(scope.get('headers', []))
            })()
            
            # 요청 로깅
            self.log_request(request)
            
            # 응답 처리
            await self.app(scope, receive, send)
            
            # 응답 로깅 (간단한 형태)
            self.log_response_simple(scope.get('method', ''), scope.get('path', ''))
        else:
            # HTTP가 아닌 경우 (예: WebSocket) 직접 전달
            await self.app(scope, receive, send)
    
    def log_request(self, request):
        """요청 로깅"""
        try:
            # 쿼리 파라미터
            query_params = {}
            if request.query_params:
                # 간단한 쿼리 파라미터 파싱
                for param in request.query_params.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
            
            # 민감한 정보 마스킹
            masked_query = mask_payload(query_params)
            
            self.logger.info(
                f"REQUEST: {request.method} {request.url.path} | "
                f"Query: {masked_query}"
            )
        except Exception as e:
            self.logger.error(f"Request logging error: {str(e)}")
    
    def log_response_simple(self, method, path):
        """간단한 응답 로깅"""
        try:
            self.logger.info(f"RESPONSE: {method} {path}")
        except Exception as e:
            self.logger.error(f"Response logging error: {str(e)}")

# 전역 로거 인스턴스
auth_logger = get_logger("auth_service")
