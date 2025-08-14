"""
Auth Service 메인 파일 - 직접 엔드포인트 정의
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
    logger.info("🔐 Auth Service 시작 (직접 엔드포인트)")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="직접 엔드포인트를 정의하는 인증 서비스",
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
        "message": "Auth Service", 
        "version": "1.0.0", 
        "status": "running",
        "docs": "/docs",
        "mode": "direct-endpoints"
    }

@app.get("/health")
async def health_check():
    """메인 헬스 체크 엔드포인트"""
    logger.info("🔵 메인 /health 엔드포인트 호출됨")
    return {"status": "healthy", "service": "auth", "mode": "direct-endpoints"}

# 직접 엔드포인트 정의
@app.post("/register")
async def register_user(user_data: dict):
    """사용자 회원가입"""
    logger.info(f"🔵 /register 엔드포인트 호출됨")
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

@app.post("/auth/register")
async def register_user_via_gateway(user_data: dict):
    """Gateway를 통한 사용자 회원가입"""
    logger.info(f"🔵 /auth/register 엔드포인트 호출됨 (Gateway 프록시)")
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
    """사용자 로그인"""
    logger.info(f"🔵 /login 엔드포인트 호출됨")
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

@app.post("/auth/login")
async def login_user_via_gateway(user_credentials: dict):
    """Gateway를 통한 사용자 로그인"""
    logger.info(f"🔵 /auth/login 엔드포인트 호출됨 (Gateway 프록시)")
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

logger.info("🔧 Auth Service 설정 완료 - 직접 엔드포인트 정의됨")

# Docker 환경에서 포트 설정 (Railway 환경변수 사용)
if __name__ == "__main__":
    # Auth Service는 Gateway를 통해 프록시되므로 직접 실행하지 않음
    logger.info("🔧 Auth Service 설정 완료 - Gateway를 통해 프록시됨")
    logger.info("🔧 Gateway는 8080 포트, Auth Service는 8000 포트")
