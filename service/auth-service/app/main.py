from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn

from app.common.db import create_tables, test_database_connection
from app.common.logger import auth_logger
from app.router.auth import router as auth_router
from app.router.country import router as country_router

def log_routes(app: FastAPI) -> None:
    """등록된 라우트 테이블 로깅"""
    auth_logger.info("=== Registered Routes ===")
    auth_logger.info(f"Total routes: {len(app.routes)}")
    
    for i, route in enumerate(app.routes, 1):
        try:
            methods = ",".join(sorted(route.methods)) if hasattr(route, 'methods') else "-"
            path = getattr(route, 'path', '-')
            name = getattr(route, 'name', '-')
            endpoint = str(getattr(route, 'endpoint', '-'))
            
            auth_logger.info(f"[ROUTE {i:2d}] path={path}, name={name}, methods={methods}")
            auth_logger.info(f"         endpoint={endpoint}")
            
        except Exception as e:
            auth_logger.warning(f"Route logging error: {str(e)}")
    
    auth_logger.info("=== End Routes ===")
    
    # 특정 경로 존재 여부 확인
    search_paths = [
        "/api/v1/countries/search",
        "/api/v1/countries",
        "/api/v1/auth",
        "/health"
    ]
    
    auth_logger.info("=== Critical Paths Check ===")
    for search_path in search_paths:
        exists = any(
            hasattr(route, 'path') and 
            getattr(route, 'path', '') == search_path 
            for route in app.routes
        )
        auth_logger.info(f"Path {search_path}: {'✅ EXISTS' if exists else '❌ MISSING'}")
    auth_logger.info("=== End Critical Paths Check ===")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    auth_logger.info("Auth Service 시작 중...")
    
    # 데이터베이스 연결 테스트
    try:
        if test_database_connection():
            auth_logger.info("데이터베이스 연결 확인 완료")
        else:
            auth_logger.warning("데이터베이스 연결 실패 - 폴백 모드로 진행")
    except Exception as e:
        auth_logger.error(f"데이터베이스 연결 테스트 중 오류: {str(e)}")
    
    # 데이터베이스 테이블 생성
    try:
        create_tables()
        auth_logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        auth_logger.error(f"데이터베이스 테이블 생성 실패: {str(e)}")
        # 테이블 생성 실패해도 서비스는 계속 실행
        auth_logger.warning("테이블 생성 실패했지만 서비스를 계속 실행합니다")
    
    auth_logger.info("Auth Service 시작 완료")
    
    yield
    
    # 종료 시
    auth_logger.info("Auth Service 종료 중...")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="인증 서비스 - 기업 및 사용자 관리",
    version="1.0.0",
    lifespan=lifespan
)

# 라우터 등록
app.include_router(auth_router, prefix="/api/v1")
app.include_router(country_router, prefix="/api/v1/countries")

@app.get("/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {"message": "Test endpoint working", "status": "ok"}

@app.get("/test/countries")
async def test_countries():
    """Countries 테스트 엔드포인트"""
    return {"message": "Countries test endpoint", "status": "ok"}

@app.get("/debug/countries")
async def debug_countries():
    """Countries 라우터 상태를 확인합니다."""
    try:
        # countries 라우터의 모든 엔드포인트 확인
        country_routes = []
        for route in country_router.routes:
            if hasattr(route, 'path'):
                route_info = {
                    "path": route.path,
                    "name": route.name,
                    "methods": list(route.methods) if hasattr(route, 'methods') else [],
                    "endpoint": str(route.endpoint) if hasattr(route, 'endpoint') else None
                }
                country_routes.append(route_info)
        
        return {
            "country_router_status": "loaded",
            "total_country_routes": len(country_routes),
            "country_routes": country_routes,
            "router_prefix": "/api/v1/countries",
            "full_paths": [f"/api/v1/countries{route['path']}" for route in country_routes]
        }
    except Exception as e:
        return {
            "error": str(e),
            "country_router_status": "error"
        }

@app.get("/debug/routes")
async def debug_routes():
    """등록된 모든 라우터 정보를 반환합니다."""
    routes = []
    
    for route in app.routes:
        if hasattr(route, 'path'):
            route_info = {
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, 'methods') else [],
                "endpoint": str(route.endpoint) if hasattr(route, 'endpoint') else None
            }
            routes.append(route_info)
    
    return {
        "total_routes": len(routes),
        "routes": routes,
        "app_info": {
            "title": app.title,
            "version": app.version,
            "openapi_url": app.openapi_url
        }
    }

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Auth Service API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        # 데이터베이스 연결 상태 확인
        db_status = test_database_connection()
        return {
            "status": "healthy" if db_status else "degraded",
            "service": "auth-service",
            "version": "1.0.0",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "auth-service",
            "version": "1.0.0",
            "database": "error",
            "error": str(e)
        }

@app.get("/debug/db")
async def debug_database():
    """데이터베이스 디버그 정보 (개발용)"""
    try:
        from app.common.settings import settings
        from app.common.db import engine
        
        # 데이터베이스 URL 정보 (민감한 정보 제거)
        db_url = settings.DATABASE_URL
        if '@' in db_url:
            # 사용자명과 비밀번호 제거
            parts = db_url.split('@')
            if len(parts) == 2:
                db_url = f"***:***@{parts[1]}"
        
        return {
            "database_url": db_url,
            "ssl_mode": settings.DATABASE_SSL_MODE,
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
