# ============================================================================
# 📦 Import 모듈들
# ============================================================================

import time
import logging
import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# CBAM 도메인 라우터
from app.domain.calculation.calculation_controller import router as calculation_router

# ReactFlow 기반 라우터들 (현재 CBAM 기능에서는 사용하지 않음)
# from app.domain.node.node_controller import node_router
# from app.domain.flow.flow_controller import flow_router
# from app.domain.edge.edge_controller import edge_router
# from app.domain.handle.handle_controller import handle_router
# from app.domain.Viewport.Viewport_controller import viewport_router

# ============================================================================
# 🔧 설정 및 초기화
# ============================================================================

"""
Cal_boundary 서비스 메인 애플리케이션

CBAM 관련 HTTP API를 제공하는 FastAPI 애플리케이션입니다.
"""

# 환경 변수 로드 (.env는 로컬에서만 사용)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 환경 변수 설정
APP_NAME = os.getenv("APP_NAME", "Cal_boundary Service")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "ReactFlow 기반 서비스")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# ============================================================================
# 🔄 애플리케이션 생명주기 관리
# ============================================================================

def get_database_url():
    """데이터베이스 URL 가져오기"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return None
    return database_url

def clean_database_url(url: str) -> str:
    """데이터베이스 URL 정리"""
    # Railway PostgreSQL에서 발생할 수 있는 잘못된 파라미터들 제거
    invalid_params = [
        'db_type', 'db_type=postgresql', 'db_type=postgres',
        'db_type=mysql', 'db_type=sqlite'
    ]
    
    for param in invalid_params:
        if param in url:
            url = url.replace(param, '')
            logger.warning(f"잘못된 데이터베이스 파라미터 제거: {param}")
    
    # 연속된 & 제거
    url = re.sub(r'&&+', '&', url)
    url = re.sub(r'&+$', '', url)
    
    if '?' in url and url.split('?')[1].startswith('&'):
        url = url.replace('?&', '?')
    
    return url

def initialize_database():
    """데이터베이스 초기화 및 마이그레이션"""
    try:
        database_url = get_database_url()
        if not database_url:
            logger.warning("데이터베이스 URL이 없어 마이그레이션을 건너뜁니다.")
            return
        
        clean_url = clean_database_url(database_url)
        
        # Railway PostgreSQL 최적화 설정
        engine_params = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 5,
            'max_overflow': 10,
            'echo': False,
            'connect_args': {
                'connect_timeout': 30,
                'application_name': 'cbam-service',
                'options': '-c timezone=utc -c client_encoding=utf8'
            }
        }
        
        # SSL 모드 설정
        if 'postgresql' in clean_url.lower():
            if '?' in clean_url:
                clean_url += "&sslmode=require"
            else:
                clean_url += "?sslmode=require"
        
        logger.info(f"데이터베이스 연결 시도: {clean_url.split('@')[1] if '@' in clean_url else clean_url}")
        
        engine = create_engine(clean_url, **engine_params)
        
        # 연결 테스트 및 테이블 생성
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 성공")
            
            # 제품 테이블 존재 확인 (실제 스키마는 별도로 생성됨)
            conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'product'
                );
            """))
            
            table_exists = conn.fetchone()[0]
            if table_exists:
                logger.info("✅ product 테이블이 이미 존재합니다")
            else:
                logger.warning("⚠️ product 테이블이 존재하지 않습니다. 수동으로 생성해주세요.")
            
            logger.info("✅ 데이터베이스 연결 확인 완료")
            
            conn.commit()
            logger.info("✅ 데이터베이스 마이그레이션 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 마이그레이션 실패: {str(e)}")
        # 치명적 오류가 아니므로 계속 진행

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    logger.info("🚀 Cal_boundary 서비스 시작 중...")
    
    # 데이터베이스 초기화 및 마이그레이션
    initialize_database()
    
    # ReactFlow 기반 서비스 초기화
    logger.info("✅ ReactFlow 기반 서비스 초기화")
    
    yield
    
    # 서비스 종료 시 정리 작업
    logger.info("✅ ReactFlow 기반 서비스 정리 완료")
    
    logger.info("🛑 Cal_boundary 서비스 종료 중...")

# ============================================================================
# 🚀 FastAPI 애플리케이션 생성
# ============================================================================

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    debug=DEBUG_MODE,
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    openapi_url="/openapi.json" if DEBUG_MODE else None,
    lifespan=lifespan
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

# ReactFlow 기반 라우터들 등록 (현재 CBAM 기능에서는 사용하지 않음)
# app.include_router(node_router, prefix="/api")
# app.include_router(flow_router, prefix="/api")
# app.include_router(edge_router, prefix="/api")
# app.include_router(handle_router, prefix="/api")
# app.include_router(viewport_router, prefix="/api")

# CBAM 도메인 라우터들 등록
app.include_router(calculation_router, prefix="/api")

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
# 📦 제품 데이터 엔드포인트는 calculation_controller.py에서 관리
# ============================================================================

# 제품 관련 엔드포인트는 /api/product로 접근 가능
# calculation_router가 /api prefix로 등록되어 있음

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
