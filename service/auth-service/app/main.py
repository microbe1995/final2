"""
Auth Service 메인 파일 - 서브라우터 역할
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
logger = logging.getLogger("auth_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🔐 Auth Service 시작 (서브라우터 모드)")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="사용자 인증 및 회원가입 서비스 (서브라우터)",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정 제거 - Gateway에서 모든 CORS 처리
# Auth Service는 내부 서비스로만 사용되므로 CORS 불필요

# 직접 엔드포인트 정의 (라우터 등록 없이)
@app.get("/")
async def root():
    """루트 엔드포인트"""
    logger.info("🔵 / 엔드포인트 호출됨")
    return {
        "message": "Auth Service (서브라우터)", 
        "version": "1.0.0", 
        "status": "running",
        "docs": "/docs",
        "mode": "sub-router"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("🔵 /health 엔드포인트 호출됨")
    return {"status": "healthy", "service": "auth", "mode": "sub-router"}

@app.post("/register")
async def register_user(user_data: dict):
    """사용자 회원가입 - Gateway에서 프록시된 요청"""
    logger.info(f"🔵 /register 엔드포인트 호출됨 (서브라우터)")
    logger.info(f"🔵 받은 데이터: {user_data}")
    
    try:
        # 간단한 응답 (실제로는 데이터베이스 처리)
        logger.info(f"✅ 회원가입 성공: {user_data.get('email', 'unknown')}")
        return {
            "message": "회원가입 성공",
            "user": {
                "username": user_data.get('username'),
                "email": user_data.get('email'),
                "full_name": user_data.get('full_name'),
                "id": "temp_id_123"  # 임시 ID
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 회원가입 실패: {str(e)}")
        return {"error": f"회원가입 실패: {str(e)}", "status": "error"}

@app.post("/login")
async def login_user(user_credentials: dict):
    """사용자 로그인 - Gateway에서 프록시된 요청"""
    logger.info(f"🔵 /login 엔드포인트 호출됨 (서브라우터)")
    logger.info(f"🔵 받은 데이터: {user_credentials}")
    
    try:
        # 간단한 응답 (실제로는 인증 처리)
        logger.info(f"✅ 로그인 성공: {user_credentials.get('email', 'unknown')}")
        return {
            "message": "로그인 성공",
            "user": {
                "email": user_credentials.get('email'),
                "token": "temp_token_123"  # 임시 토큰
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 로그인 실패: {str(e)}")
        return {"error": f"로그인 실패: {str(e)}", "status": "error"}

# Docker 환경에서 포트 설정 (8000으로 고정)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🚀 Auth Service 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
