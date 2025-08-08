"""
Auth Service 메인 파일
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
import logging
import sys
from dotenv import load_dotenv

from models.user import User, UserCreate, UserLogin, UserResponse, Token
from services.auth_service import AuthService

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

# 보안 스키마
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🔐 Auth Service 시작")
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="사용자 인증 및 회원가입 서비스",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 프론트엔드
        "http://127.0.0.1:3000",
        "https://lca-final.vercel.app",  # Vercel 프론트엔드
        "http://gateway:8080",  # Gateway 서비스
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth 서비스 인스턴스
auth_service = AuthService()

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Auth Service", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "auth"}

@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """사용자 회원가입"""
    try:
        logger.info(f"회원가입 요청: {user_data.email}")
        user = await auth_service.create_user(user_data)
        logger.info(f"회원가입 성공: {user.email}")
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except ValueError as e:
        logger.error(f"회원가입 실패: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"회원가입 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="회원가입 중 오류가 발생했습니다.")

@app.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """사용자 로그인"""
    try:
        logger.info(f"로그인 시도: {user_credentials.email}")
        token = await auth_service.authenticate_user(
            user_credentials.email, 
            user_credentials.password
        )
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"로그인 성공: {user_credentials.email}")
        return Token(access_token=token, token_type="bearer")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다.")

@app.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 사용자 정보 조회"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 정보 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="사용자 정보 조회 중 오류가 발생했습니다.")

@app.post("/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """토큰 검증"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )
        return {"valid": True, "user_id": user.id, "email": user.email}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 검증 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="토큰 검증 중 오류가 발생했습니다.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
