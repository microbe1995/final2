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

# 허용할 도메인 목록
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # 로컬 개발
    "https://lca-final.vercel.app",  # Vercel 배포
    "https://*.vercel.app",  # Vercel 서브도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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

# 도형 관련 API (prefix 제거 - Gateway에서 이미 /api/v1을 처리)
app.include_router(shape_router)

# 화살표 관련 API (prefix 제거 - Gateway에서 이미 /api/v1을 처리)
app.include_router(arrow_router)

# Canvas 관련 API (prefix 제거 - Gateway에서 이미 /api/v1을 처리)
app.include_router(canvas_router)

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
