"""
Auth Service 메인 파일 - 완전 격리된 서브라우터
"""
from fastapi import FastAPI, Request
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
logger = logging.getLogger("auth_service_simple")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🔐 Auth Service 시작 (완전 격리된 서브라우터)")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service (Simple)",
    description="완전 격리된 인증 서비스 (서브라우터)",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# 직접 엔드포인트 정의 (완전 격리)
@app.get("/")
async def root():
    """루트 엔드포인트"""
    logger.info("🔵 / 엔드포인트 호출됨 (격리됨)")
    return {
        "message": "Auth Service (완전 격리된 서브라우터)", 
        "version": "1.0.0", 
        "status": "running",
        "docs": "/docs",
        "mode": "isolated-sub-router"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    logger.info("🔵 /health 엔드포인트 호출됨 (격리됨)")
    return {"status": "healthy", "service": "auth", "mode": "isolated-sub-router"}

@app.post("/register")
async def register_user(request: Request):
    """사용자 회원가입 - Gateway에서 프록시된 요청"""
    logger.info("🔵 /register 엔드포인트 호출됨 (격리됨)")
    
    try:
        # JSON 데이터 파싱
        user_data = await request.json()
        logger.info(f"🔵 받은 데이터: {user_data}")
        
        # 간단한 응답 (실제로는 데이터베이스 처리)
        username = user_data.get('username', 'unknown')
        email = user_data.get('email', 'unknown')
        full_name = user_data.get('full_name', 'unknown')
        
        logger.info(f"✅ 회원가입 성공: {email}")
        return {
            "message": "회원가입 성공",
            "user": {
                "username": username,
                "email": email,
                "full_name": full_name,
                "id": "temp_id_123"  # 임시 ID
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"❌ 회원가입 실패: {str(e)}")
        return {"error": f"회원가입 실패: {str(e)}", "status": "error"}

@app.post("/login")
async def login_user(request: Request):
    """사용자 로그인 - Gateway에서 프록시된 요청"""
    logger.info("🔵 /login 엔드포인트 호출됨 (격리됨)")
    
    try:
        # JSON 데이터 파싱
        user_credentials = await request.json()
        logger.info(f"🔵 받은 데이터: {user_credentials}")
        
        # 간단한 응답 (실제로는 인증 처리)
        email = user_credentials.get('email', 'unknown')
        
        logger.info(f"✅ 로그인 성공: {email}")
        return {
            "message": "로그인 성공",
            "user": {
                "email": email,
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
    # Railway 환경변수와 관계없이 8000 포트 강제 사용
    port = 8000
    logger.info(f"🚀 Auth Service 시작 - 포트: {port} (완전 격리, 강제 8000)")
    uvicorn.run(app, host="0.0.0.0", port=port)
