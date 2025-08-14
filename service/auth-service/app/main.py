"""
Auth Service 메인 파일 - 서브라우터 사용
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import logging
import sys
from dotenv import load_dotenv

# 라우터 import
from .router.auth_router import auth_router

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
    logger.info("🔐 Auth Service 시작 (서브라우터 사용)")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service (Router)",
    description="서브라우터를 사용하는 인증 서비스",
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

# 기본 엔드포인트
@app.get("/")
async def root():
    """메인 루트 엔드포인트"""
    logger.info("🔵 메인 / 엔드포인트 호출됨")
    return {
        "message": "Auth Service Main", 
        "version": "1.0.0", 
        "status": "running",
        "docs": "/docs",
        "mode": "main-with-router",
        "router": "/auth"
    }

@app.get("/health")
async def health_check():
    """메인 헬스 체크 엔드포인트"""
    logger.info("🔵 메인 /health 엔드포인트 호출됨")
    return {"status": "healthy", "service": "auth-main", "mode": "main-with-router"}

# Auth 라우터 등록
app.include_router(auth_router)

logger.info("🔧 Auth Service 설정 완료 - 서브라우터 등록됨")

# Docker 환경에서 포트 설정 (Railway 환경변수 사용)
if __name__ == "__main__":
    import uvicorn
    import os
    
    # Auth Service는 8000 포트 고정 사용
    port = 8000
    logger.info(f"🚀 Auth Service 시작 - 포트: {port} (고정)")
    logger.info(f"🔧 Gateway는 8080 포트, Auth Service는 8000 포트")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
