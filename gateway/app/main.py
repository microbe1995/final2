"""
Gateway API 메인 파일 - 도메인 구조로 리팩토링
기존 코드를 도메인 레이어로 분리하여 유지보수성 향상
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# 도메인 레이어 import
from app.domain.controller.proxy_controller import proxy_router
from app.domain.service.proxy_service import ProxyService

# 환경 변수 로드 (.env는 로컬에서만 사용, Railway에선 대시보드 변수 사용)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🚀 Gateway API 시작 (도메인 구조 적용)")
    yield
    logger.info("🛑 Gateway API 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - 도메인 구조로 리팩토링됨",
    version="0.4.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# ---- CORS 설정 (환경변수 기반) ----
# Railway Variables 예시:
# CORS_URL = https://lca-final.vercel.app
allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
if not allowed_origins:
    # 안전한 기본값(필요 시 바꿔도 됨)
    allowed_origins = ["https://lca-final.vercel.app"]

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,    # "*" 금지 (credentials true일 때 규칙 위반)
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

logger.info(f"🔧 CORS origins={allowed_origins}, credentials={allow_credentials}")

# ---- 도메인 라우터 등록 ----
# 프록시 컨트롤러의 라우터를 등록
app.include_router(proxy_router)

# ---- 기본 엔드포인트 ----
@app.get("/", summary="Gateway 루트")
async def root():
    """Gateway API 루트 엔드포인트"""
    return {
        "message": "Gateway API - 도메인 구조로 리팩토링됨", 
        "version": "0.4.0",
        "architecture": "Domain-Driven Design",
        "docs": "/docs"
    }

@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root():
    """Gateway 서비스 상태 확인"""
    return {"status": "healthy", "service": "gateway", "version": "0.4.0"}

# ---- 요청 로깅 미들웨어 ----
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """모든 HTTP 요청을 로깅하는 미들웨어"""
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# ---- 예외 처리 핸들러 ----
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404 Not Found 예외 처리"""
    logger.error("🚨 404")
    return JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method, 
            "path": request.url.path,
            "architecture": "Domain-Driven Design"
        },
    )

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    """405 Method Not Allowed 예외 처리"""
    logger.error("🚨 405")
    return JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method, 
            "path": request.url.path,
            "architecture": "Domain-Driven Design"
        },
    )

# ---- 애플리케이션 실행 ----
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

# ============================================================================
# 🚫 기존 코드 (참고용으로 보존, 실제로는 사용되지 않음)
# ============================================================================
"""
기존 main.py의 코드를 도메인 구조로 분리한 내용:

1. ServiceProxyFactory 클래스 → domain/service/proxy_service.py로 이동
2. 프록시 라우터 → domain/controller/proxy_controller.py로 이동
3. CORS 처리 → domain/service/proxy_service.py의 handle_cors_preflight로 이동
4. 서비스 헬스 체크 → domain/service/proxy_service.py의 check_all_services_health로 이동

도메인 구조의 장점:
- 관심사 분리 (Separation of Concerns)
- 단일 책임 원칙 (Single Responsibility Principle)
- 코드 재사용성 향상
- 테스트 용이성 향상
- 유지보수성 향상

각 레이어의 역할:
- Controller: HTTP 요청/응답 처리
- Service: 비즈니스 로직 (서비스 디스커버리, 프록시 처리)
- Repository: 데이터 접근 로직 (서비스 정보 관리)
- Entity: 데이터 모델 (서비스 정보, 헬스 체크 결과)
- Schema: 데이터 검증 및 직렬화
"""
