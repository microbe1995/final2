"""
JWT 인증 미들웨어
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 헬스체크와 루트 경로는 인증 제외
            if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
                return await self.app(scope, receive, send)
            
            # API 경로에서 인증 체크
            if request.url.path.startswith("/api/"):
                # JWT 토큰 검증 로직 (현재는 기본 구조만)
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    logger.warning("인증 헤더가 없습니다")
                    # 개발 중에는 인증을 우회
                    pass
                else:
                    # JWT 토큰 검증 로직 추가 예정
                    pass
            
        return await self.app(scope, receive, send)
