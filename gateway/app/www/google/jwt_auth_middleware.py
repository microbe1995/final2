"""
JWT Auth Middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # JWT 토큰 검증 로직 (현재는 기본 구현)
        # TODO: 실제 JWT 검증 로직 구현
        
        # 요청에 사용자 ID 헤더 추가 (기본값: anonymous)
        request.headers.__dict__["_list"].append(
            (b"x-user-id", b"anonymous")
        )
        
        response = await call_next(request)
        return response 