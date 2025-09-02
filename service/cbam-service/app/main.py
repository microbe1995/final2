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
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 🔴 핵심 CBAM 도메인 라우터만 임포트 (실제 사용되는 기능)
from app.domain.calculation.calculation_controller import router as calculation_router
from app.domain.install.install_controller import router as install_router
from app.domain.product.product_controller import router as product_router
from app.domain.process.process_controller import router as process_router
from app.domain.edge.edge_controller import router as edge_router
from app.domain.mapping.mapping_controller import router as mapping_router
from app.domain.matdir.matdir_controller import router as matdir_router
from app.domain.fueldir.fueldir_controller import router as fueldir_router
from app.domain.productprocess.productprocess_controller import router as product_process_router
from app.domain.dummy.dummy_controller import router as dummy_router

# get_async_db 함수는 database_base.py에서 관리

# ============================================================================
# 🔧 설정 및 초기화
# ============================================================================

"""
Cal_boundary 서비스 메인 애플리케이션

CBAM 관련 HTTP API를 제공하는 FastAPI 애플리케이션입니다.
"""

# Railway 환경에서는 자동으로 환경변수가 설정됨

# 환경 변수 설정
APP_NAME = os.getenv("APP_NAME", "Cal_boundary Service")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "ReactFlow 기반 서비스")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# 전역 데이터베이스 엔진 및 세션 팩토리
async_engine = None
async_session_factory = None

# get_async_db 함수는 database_base.py에서 관리 (순환 참조 방지)

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
    """데이터베이스 URL 정리 및 asyncpg 형식으로 변환"""
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
    
    # postgresql:// -> postgresql+asyncpg:// 변환 (SQLAlchemy async 지원)
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        logger.info("✅ PostgreSQL URL을 asyncpg 형식으로 변환")
    
    return url

async def initialize_database():
    """비동기 데이터베이스 초기화 및 SQLAlchemy 엔진 설정"""
    global async_engine, async_session_factory
    
    try:
        database_url = get_database_url()
        if not database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            return
        
        clean_url = clean_database_url(database_url)
        
        # 비동기 SQLAlchemy 엔진 생성
        async_engine = create_async_engine(
            clean_url,
            echo=DEBUG_MODE,  # 디버그 모드에서만 SQL 로깅
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={
                'server_settings': {
                    'application_name': 'cbam-service-async',
                    'timezone': 'utc',
                    'client_encoding': 'utf8'
                }
            }
        )
        
        # 비동기 세션 팩토리 생성
        async_session_factory = sessionmaker(
            async_engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        logger.info("✅ 비동기 SQLAlchemy 엔진 및 세션 팩토리 생성 완료")
        
        # 연결 테스트
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 테스트 성공")
        
    except Exception as e:
        logger.error(f"❌ 비동기 데이터베이스 초기화 실패: {str(e)}")
        logger.warning("⚠️ 데이터베이스 연결 실패로 인해 일부 기능이 제한될 수 있습니다.")
        async_engine = None
        async_session_factory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    logger.info("🚀 Cal_boundary 서비스 시작 중...")
    
    # 비동기 데이터베이스 초기화
    await initialize_database()
    
    # ReactFlow 기반 서비스 초기화
    logger.info("✅ ReactFlow 기반 서비스 초기화")
    
    # SQLAlchemy 엔진 상태 확인
    if async_engine:
        logger.info("✅ SQLAlchemy 비동기 엔진 초기화 완료")
    else:
        logger.warning("⚠️ SQLAlchemy 엔진 초기화 실패 - Repository 자동 초기화에 의존")
    
    yield
    
    # 서비스 종료 시 정리 작업
    if async_engine:
        await async_engine.dispose()
        logger.info("✅ SQLAlchemy 엔진 정리 완료")
    
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
    lifespan=lifespan,
    redirect_slashes=False  # trailing slash 리다이렉트 방지
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

# CBAM 도메인 라우터들 등록 (MSA 원칙: Gateway가 경로를 관리)
# 중요: Gateway를 통해 접근하므로 prefix 없이 등록 (상대 경로 사용)

# 🔴 수정: 엔티티 의존성 순서를 고려한 라우터 등록 순서
# 1. 기본 엔티티 (의존성이 없는 것들)
app.include_router(install_router, prefix="/install")
app.include_router(product_router, prefix="/product")
app.include_router(process_router, prefix="/process")

# 2. 중간 테이블 (기본 엔티티에 의존)
app.include_router(product_process_router, prefix="/productprocess")

# 3. 계산 및 분석 관련 (중간 테이블에 의존)
app.include_router(calculation_router, prefix="/calculation")

# 4. 도메인별 관리
app.include_router(mapping_router, prefix="/mapping")
app.include_router(edge_router, prefix="/edge")
app.include_router(matdir_router, prefix="/matdir")
app.include_router(fueldir_router, prefix="/fueldir")
app.include_router(dummy_router, prefix="/dummy")

logger.info("✅ 모든 라우터 등록 완료 (엔티티 의존성 순서 고려)")
logger.info("🔗 기본 엔티티 → 중간 테이블 → 계산/분석 순서로 등록")

# ============================================================================
# 🏥 헬스체크 엔드포인트
# ============================================================================

@app.get("/", tags=["root"])
async def root():
    """서비스 루트 경로 (Gateway 호환성)"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "message": "CBAM Service is running",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs" if DEBUG_MODE else "disabled",
            "install": "/install",
            "product": "/product",
            "process": "/process"
        }
    }

@app.get("/health", tags=["health"])
async def health_check():
    """서비스 상태 확인"""
    # 🔴 데이터베이스 연결 상태 확인 제거 - 메인 라우터 역할에 맞지 않음
    # 각 Repository가 자체적으로 연결 상태를 관리함
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": time.time()
    }

@app.get("/debug/routes", tags=["debug"])
async def debug_routes():
    """등록된 라우트 정보 확인 (디버그용)"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            # 라우터 정보 추가
            route_info = {
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown'),
                "endpoint": str(route.endpoint) if hasattr(route, 'endpoint') else 'unknown'
            }
            
            # 동적 경로인지 확인
            if '{' in route.path:
                route_info["dynamic"] = True
                route_info["path_params"] = [param for param in route.path.split('/') if param.startswith('{') and param.endswith('}')]
            else:
                route_info["dynamic"] = False
                route_info["path_params"] = []
            
            routes.append(route_info)
    
    # 경로별로 정렬
    routes.sort(key=lambda x: (x["dynamic"], x["path"]))
    
    # 라우터별 그룹화
    router_groups = {}
    for route in routes:
        if route["path"] == "/":
            group = "root"
        elif route["path"].startswith("/install"):
            group = "install"
        elif route["path"].startswith("/product"):
            group = "product"
        elif route["path"].startswith("/process"):
            group = "process"
        elif route["path"].startswith("/calculation"):
            group = "calculation"
        else:
            group = "other"
        
        if group not in router_groups:
            router_groups[group] = []
        router_groups[group].append(route)
    
    return {
        "total_routes": len(routes),
        "router_groups": router_groups,
        "static_routes": [r for r in routes if not r["dynamic"]],
        "dynamic_routes": [r for r in routes if r["dynamic"]],
        "all_routes": routes,
        "install_routes": [r for r in routes if r["path"].startswith("/install")]
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
