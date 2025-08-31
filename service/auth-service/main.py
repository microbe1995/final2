from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
# 🔴 CORS 제거: Gateway에서만 CORS를 관리해야 함
# from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.common.settings import settings
from app.common.logger import LoggingMiddleware, auth_logger
from app.common.db import create_tables
from app.router import auth_router, sitemap_router
from app.www.errors import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

def log_routes(app: FastAPI) -> None:
    """등록된 라우트 테이블 로깅"""
    auth_logger.info("=== Registered Routes ===")
    for route in app.routes:
        try:
            methods = ",".join(sorted(route.methods)) if hasattr(route, 'methods') else "-"
            path = getattr(route, 'path', '-')
            name = getattr(route, 'name', '-')
            auth_logger.info(f"[ROUTE] path={path}, name={name}, methods={methods}")
        except Exception as e:
            auth_logger.warning(f"Route logging error: {str(e)}")
    auth_logger.info("=== End Routes ===")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리 - DDD Architecture"""
    # 시작 시
    auth_logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    auth_logger.info(f"Architecture: DDD (Domain-Driven Design)")
    auth_logger.info(f"Environment: {settings.ENVIRONMENT}")
    auth_logger.info(f"Port: {settings.PORT}")
    
    try:
        # 데이터베이스 테이블 생성
        create_tables()
        auth_logger.info("Database initialization completed")
        
        # DDD 도메인 서비스 초기화
        if settings.DOMAIN_EVENTS_ENABLED:
            auth_logger.info("Domain events system enabled")
        
        # 등록된 라우트 테이블 로깅
        log_routes(app)
        
        auth_logger.info("Service initialization completed successfully")
        
    except Exception as e:
        auth_logger.error(f"Service initialization failed: {str(e)}")
        raise
    
    yield
    
    # 종료 시
    auth_logger.info(f"Shutting down {settings.SERVICE_NAME}")

def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리 - DDD Architecture"""
    
    # FastAPI 애플리케이션 생성
    app = FastAPI(
        title=f"{settings.SERVICE_NAME} (DDD Architecture)",
        description="도메인 주도 설계(DDD)를 적용한 인증 서비스 - 회원가입, 로그인, 로그아웃, 스트림 이벤트 관리",
        version=settings.SERVICE_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None
    )
    
    # 🔴 CORS 제거: Gateway에서만 CORS를 관리해야 함
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=settings.origins_list,
    #     allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    #     expose_headers=["*"],
    #     max_age=3600
    # )
    
    # 로깅 미들웨어 추가
    app.add_middleware(LoggingMiddleware)
    
    # 예외 핸들러 등록
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # 라우터 등록 - 인증과 사이트맵만 (스트림 기능 제거)
    app.include_router(auth_router, tags=["identity-access"])
    app.include_router(sitemap_router, tags=["sitemap"])
    
    # 헬스 체크 엔드포인트
    @app.get("/health")
    async def health_check():
        """헬스 체크 엔드포인트 - DDD 서비스 상태"""
        return {
            "status": "ok",
            "service": settings.service_info,
            "timestamp": "2024-01-01T00:00:00Z",
            "architecture": "DDD (Domain-Driven Design)",
            "features": {
                "domain_events": settings.DOMAIN_EVENTS_ENABLED,

                "metrics": settings.ENABLE_METRICS
            }
        }
    
    # 서비스 정보 엔드포인트
    @app.get("/info")
    async def service_info():
        """서비스 정보 엔드포인트 - DDD 아키텍처 정보"""
        return {
            "service": settings.service_info,
            "architecture": {
                "pattern": "DDD (Domain-Driven Design)",
                "layers": ["www", "domain", "router", "common"],
                "domains": ["identity-access", "sitemap"],
                "aggregates": ["Company", "User"],
                "value_objects": ["Address", "BusinessNumber", "ContactInfo"]
            },
            "capabilities": {
                "authentication": True,
                "authorization": True,
                "domain_events": settings.DOMAIN_EVENTS_ENABLED,
                "metrics": settings.ENABLE_METRICS,
                "sitemap": True
            }
        }
    
    # 파비콘 엔드포인트
    @app.get("/favicon.ico")
    async def favicon():
        """파비콘 엔드포인트 (204 No Content)"""
        from fastapi.responses import Response
        return Response(status_code=204)
    
    return app

# 애플리케이션 인스턴스 생성
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
