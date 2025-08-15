"""
Auth Service 메인 파일 - 도메인 구조로 리팩토링
기존 코드를 도메인 레이어로 분리하여 유지보수성 향상
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import logging
import sys
from dotenv import load_dotenv

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("auth_service_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🔐 Auth Service 시작 (도메인 구조 적용)")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="도메인 구조로 리팩토링된 인증 서비스",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 미들웨어 추가 - 모든 출처 허용
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# ---- 도메인 라우터 등록 ----
# 인증 컨트롤러의 라우터를 등록
from app.domain.controller.auth_controller import auth_router

app.include_router(auth_router)

# ---- 기본 엔드포인트 ----
@app.get("/", summary="Auth Service 루트")
async def root():
    """Auth Service 루트 엔드포인트"""
    return {
        "message": "Auth Service - 도메인 구조로 리팩토링됨", 
        "version": "1.0.0",
        "architecture": "Domain-Driven Design",
        "docs": "/docs",
        "endpoints": {
            "auth": "/auth",
            "health": "/health"
        }
    }

@app.get("/health", summary="Auth Service 헬스 체크")
async def health_check_root():
    """Auth Service 상태 확인"""
    return {"status": "healthy", "service": "auth", "version": "1.0.0"}

logger.info("🔧 Auth Service 설정 완료 - 도메인 구조 적용됨")

# Docker 환경에서 포트 설정 (Railway 환경변수 사용)
if __name__ == "__main__":
    # Auth Service는 Gateway를 통해 프록시되므로 직접 실행하지 않음
    logger.info("🔧 Auth Service 설정 완료 - Gateway를 통해 프록시됨")
    logger.info("🔧 Gateway는 8080 포트, Auth Service는 8000 포트")
