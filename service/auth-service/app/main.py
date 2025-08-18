"""
Auth Service 메인 파일 - 도메인 구조로 리팩토링
기존 코드를 도메인 레이어로 분리하여 유지보수성 향상

아키텍처:
- Controller: HTTP 요청/응답 처리 (인증 엔드포인트)
- Service: 비즈니스 로직 (사용자 인증, 회원가입)
- Repository: 데이터 접근 로직 (사용자 정보 저장/조회)
- Entity: 데이터 모델 (사용자 정보, 인증 데이터)
- Schema: 데이터 검증 및 직렬화 (회원가입/로그인 요청)
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
import logging
import sys
from dotenv import load_dotenv

# ============================================================================
# 🔧 환경 설정 및 초기화
# ============================================================================

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# 환경변수 디버깅 로그
logger = logging.getLogger("auth_service_main")
logger.info(f"🔧 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
logger.info(f"🔧 DATABASE_URL 설정됨: {'DATABASE_URL' in os.environ}")
if os.getenv("DATABASE_URL"):
    logger.info(f"🔧 DATABASE_URL: {os.getenv('DATABASE_URL')[:20]}...")
else:
    logger.warning("⚠️ DATABASE_URL 환경변수가 설정되지 않았습니다!")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("auth_service_main")

# ============================================================================
# 🚀 애플리케이션 생명주기 관리 -이건 메인라우터에만 (출입구 관리 ) - 수정하기
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🔐 Auth Service 시작 (도메인 구조 적용)")
    
    # 데이터베이스 연결 및 테이블 생성
    try:
        from app.common.database.database import database
        if database.database_url:
            success = database.create_tables()
            if success:
                logger.info("✅ 데이터베이스 테이블 생성/확인 완료")
            else:
                logger.warning("⚠️ 데이터베이스 테이블 생성 실패")
        else:
            logger.warning("⚠️ DATABASE_URL 미설정 - 메모리 저장소 사용")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 초기화 실패: {str(e)}")
    
    yield
    
    # 데이터베이스 연결 종료
    try:
        from app.common.database.database import database
        database.close()
        logger.info("🔌 데이터베이스 연결 종료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 종료 실패: {str(e)}")
    
    logger.info("🛑 Auth Service 종료")

# ============================================================================
# 🏗️ FastAPI 앱 생성 및 설정 - 남겨놓기
# ============================================================================

app = FastAPI(
    title="Auth Service",
    description="도메인 구조로 리팩토링된 인증 서비스",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan # 필요X
)

# NOTE: CORS는 오직 Gateway에서만 처리합니다. 개별 서비스에는 CORS 미들웨어를 두지 않습니다.

# ============================================================================
# 🚪 도메인 라우터 등록
# ============================================================================

# 인증 컨트롤러의 라우터를 등록
from app.domain.user.user_controller import auth_router

app.include_router(auth_router)

# ============================================================================
# 🏠 기본 엔드포인트
# ============================================================================
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
