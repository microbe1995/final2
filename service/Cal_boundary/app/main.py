# ============================================================================
# 🚀 Cal_boundary Main Application
# ============================================================================

"""
Cal_boundary 서비스 메인 애플리케이션

도형, 화살표, Canvas 등의 HTTP API를 제공하는 FastAPI 애플리케이션입니다.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time
import os

# 라우터 임포트
from .domain.controller import shape_router, arrow_router, canvas_router

# ============================================================================
# 🔧 애플리케이션 설정
# ============================================================================

# 환경 변수 설정
APP_NAME = os.getenv("APP_NAME", "Cal_boundary Service")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Canvas 기반 도형 및 화살표 관리 서비스")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ============================================================================
# 🎯 애플리케이션 생명주기 관리
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    # 시작 시
    logger.info("🚀 Cal_boundary 서비스 시작 중...")
    logger.info(f"📋 서비스 정보: {APP_NAME} v{APP_VERSION}")
    logger.info(f"🔧 디버그 모드: {DEBUG_MODE}")
    
    yield
    
    # 종료 시
    logger.info("🛑 Cal_boundary 서비스 종료 중...")

# ============================================================================
# 🚀 FastAPI 애플리케이션 생성
# ============================================================================

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    debug=DEBUG_MODE,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    openapi_url="/openapi.json" if DEBUG_MODE else None
)

# ============================================================================
# 🌐 CORS 미들웨어 설정
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 📊 요청/응답 로깅 미들웨어
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """HTTP 요청/응답 로깅"""
    start_time = time.time()
    
    # 요청 로깅
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    # 응답 처리
    response = await call_next(request)
    
    # 응답 로깅
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    
    return response

# ============================================================================
# 🎯 라우터 등록
# ============================================================================

# 도형 관련 API
app.include_router(shape_router, prefix="/api/v1")

# 화살표 관련 API
app.include_router(arrow_router, prefix="/api/v1")

# Canvas 관련 API
app.include_router(canvas_router, prefix="/api/v1")

# ============================================================================
# 🧪 테스트용 엔드포인트
# ============================================================================

@app.get("/test", tags=["test"])
async def test_endpoint():
    """테스트용 엔드포인트"""
    return {
        "message": "Cal_boundary 서비스가 정상적으로 작동 중입니다!",
        "status": "success",
        "timestamp": time.time()
    }

@app.get("/api/v1/test", tags=["test"])
async def test_api_endpoint():
    """API 테스트용 엔드포인트"""
    return {
        "message": "API v1 엔드포인트가 정상적으로 작동 중입니다!",
        "status": "success",
        "timestamp": time.time()
    }

# ============================================================================
# 🏠 루트 엔드포인트
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """서비스 루트 엔드포인트"""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "status": "running",
        "endpoints": {
            "shapes": "/api/v1/shapes",
            "arrows": "/api/v1/arrows",
            "canvas": "/api/v1/canvas",
            "docs": "/docs" if DEBUG_MODE else "disabled",
            "health": "/health"
        }
    }

# ============================================================================
# 🏥 헬스체크 엔드포인트
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": time.time()
    }

# ============================================================================
# 🔍 서비스 정보 엔드포인트
# ============================================================================

@app.get("/info", tags=["info"])
async def service_info():
    """서비스 상세 정보"""
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "debug_mode": DEBUG_MODE,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "api_version": "v1",
        "features": [
            "도형 관리 (생성, 조회, 수정, 삭제)",
            "화살표 관리 (생성, 조회, 수정, 삭제)",
            "Canvas 관리 (생성, 조회, 수정, 삭제)",
            "도형 및 화살표 검색 및 필터링",
            "Canvas 템플릿 및 내보내기/가져오기",
            "통계 및 분석 기능"
        ]
    }

# ============================================================================
# 🚨 예외 처리 핸들러
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리"""
    logger.error(f"❌ 예상치 못한 오류 발생: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "서버 내부 오류가 발생했습니다",
            "detail": str(exc) if DEBUG_MODE else "오류 세부 정보는 숨겨집니다"
        }
    )

# ============================================================================
# 🧪 개발용 디버그 엔드포인트
# ============================================================================

if DEBUG_MODE:
    @app.get("/debug/routes", tags=["debug"])
    async def debug_routes():
        """등록된 모든 라우트 정보"""
        routes = []
        for route in app.routes:
            if hasattr(route, "methods") and hasattr(route, "path"):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, "name", "Unknown")
                })
        return {"routes": routes}

# ============================================================================
# 🚀 애플리케이션 실행 (개발용)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 개발 모드로 서버 시작...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
