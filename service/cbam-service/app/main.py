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
from sqlalchemy import create_engine, text

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# CBAM 도메인 라우터
from app.domain.calculation.calculation_controller import router as calculation_router
from app.domain.install.install_controller import router as install_router
from app.domain.product.product_controller import router as product_router
from app.domain.process.process_controller import router as process_router
from app.domain.edge.edge_controller import router as edge_router
from app.domain.mapping.mapping_controller import router as mapping_router
from app.domain.matdir.matdir_controller import router as matdir_router
from app.domain.fueldir.fueldir_controller import router as fueldir_router
from app.domain.processchain.processchain_controller import router as processchain_router
from app.domain.productprocess.productprocess_controller import router as product_process_router

# 엔티티 임포트 (순환 참조 방지를 위해 라우터 등록 전에 임포트)
from app.domain.productprocess.productprocess_entity import ProductProcess
from app.domain.install.install_entity import Install
from app.domain.product.product_entity import Product
from app.domain.process.process_entity import Process
from app.domain.matdir.matdir_entity import MatDir
from app.domain.fueldir.fueldir_entity import FuelDir
from app.domain.processchain.processchain_entity import ProcessChain, ProcessChainLink

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
                'options': '-c timezone=utc -c client_encoding=utf8 -c log_min_messages=error -c log_statement=none'
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
    
    # 각 Repository의 데이터베이스 연결 풀 초기화 (선택적)
    try:
        from app.domain.calculation.calculation_repository import CalculationRepository
        calc_repo = CalculationRepository()
        await calc_repo.initialize()
        logger.info("✅ CalculationRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ CalculationRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.install.install_repository import InstallRepository
        install_repo = InstallRepository()
        await install_repo.initialize()
        logger.info("✅ InstallRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ InstallRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.product.product_repository import ProductRepository
        product_repo = ProductRepository()
        await product_repo.initialize()
        logger.info("✅ ProductRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ ProductRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")

    try:
        from app.domain.process.process_repository import ProcessRepository
        process_repo = ProcessRepository()
        await process_repo.initialize()
        logger.info("✅ ProcessRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ ProcessRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.edge.edge_repository import EdgeRepository
        edge_repo = EdgeRepository()
        await edge_repo.initialize()
        logger.info("✅ EdgeRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ EdgeRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.mapping.mapping_repository import HSCNMappingRepository
        mapping_repo = HSCNMappingRepository()
        await mapping_repo.initialize()
        logger.info("✅ MappingRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ MappingRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.matdir.matdir_repository import MatDirRepository
        matdir_repo = MatDirRepository()
        await matdir_repo.initialize()
        logger.info("✅ MatDirRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ MatDirRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.fueldir.fueldir_repository import FuelDirRepository
        fueldir_repo = FuelDirRepository()
        await fueldir_repo.initialize()
        logger.info("✅ FuelDirRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ FuelDirRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
    try:
        from app.domain.processchain.processchain_repository import ProcessChainRepository
        processchain_repo = ProcessChainRepository()
        await processchain_repo.initialize()
        logger.info("✅ ProcessChainRepository 데이터베이스 연결 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ ProcessChainRepository 초기화 실패 (서비스는 계속 실행): {e}")
        logger.info("ℹ️ 데이터베이스 연결은 필요할 때 자동으로 초기화됩니다.")
    
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

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

# CBAM 도메인 라우터들 등록 (MSA 원칙: 각 서비스는 자체 경로 구조를 가짐)
# 중요: 더 구체적인 경로를 가진 라우터를 먼저 등록 (FastAPI 라우팅 우선순위)
app.include_router(calculation_router)  # /calculation 경로
app.include_router(product_router)      # /product 경로
app.include_router(process_router)     # /process 경로
app.include_router(edge_router)        # /edge 경로
app.include_router(mapping_router)     # /mapping 경로
app.include_router(matdir_router)      # /matdir 경로
app.include_router(fueldir_router)     # /fueldir 경로
app.include_router(processchain_router) # /processchain 경로
app.include_router(product_process_router) # /productprocess 경로
app.include_router(install_router)     # /install 경로 (마지막에 등록 - 동적 경로 포함)

# ============================================================================
# 🏥 헬스체크 엔드포인트
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """서비스 상태 확인"""
    # 데이터베이스 연결 상태 확인
    db_status = "unknown"
    try:
        from app.domain.calculation.calculation_service import CalculationService
        calc_service = CalculationService()
        if calc_service.calc_repository.pool:
            db_status = "connected"
        else:
            db_status = "not_initialized"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "database": db_status,
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
    
    return {
        "total_routes": len(routes),
        "static_routes": [r for r in routes if not r["dynamic"]],
        "dynamic_routes": [r for r in routes if r["dynamic"]],
        "all_routes": routes
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
