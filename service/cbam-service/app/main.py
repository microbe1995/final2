# ============================================================================
# 📦 Import 모듈들
# ============================================================================

import time
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

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
from app.domain.processchain.processchain_controller import router as processchain_router
from app.domain.productprocess.productprocess_controller import router as product_process_router

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 함수"""
    logger.info("🚀 Cal_boundary 서비스 시작 중...")
    
    # ReactFlow 기반 서비스 초기화
    logger.info("✅ ReactFlow 기반 서비스 초기화")
    
    # 🔴 Repository 초기화 제거 - 각 도메인에서 필요할 때 자동으로 초기화됨
    # 각 Repository는 _ensure_pool_initialized()로 자동 초기화
    logger.info("ℹ️ Repository는 필요할 때 자동으로 초기화됩니다.")
    
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

# CBAM 도메인 라우터들 등록 (MSA 원칙: Gateway가 경로를 관리)
# 중요: Gateway를 통해 접근하므로 prefix 없이 등록 (상대 경로 사용)

# 모든 라우터를 루트 경로에 등록 (prefix 없음)
# 중요: install_router를 먼저 등록하여 /install 경로가 루트 경로와 충돌하지 않도록 함
app.include_router(install_router)  # /install 경로 (prefix 없음) - 먼저 등록
app.include_router(calculation_router)      # /calculation 경로
app.include_router(product_router)          # /product 경로
app.include_router(process_router)         # /process 경로
app.include_router(edge_router)            # /edge 경로
app.include_router(mapping_router)         # /mapping 경로
app.include_router(matdir_router)          # /matdir 경로
app.include_router(fueldir_router)         # /fueldir 경로
app.include_router(processchain_router)    # /processchain 경로
app.include_router(product_process_router) # /productprocess 경로

logger.info("✅ 모든 라우터 등록 완료 (install_router 내부 경로를 /install로 시작하여 경로 충돌 방지)")

# ============================================================================
# 🏥 헬스체크 엔드포인트
# ============================================================================

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
