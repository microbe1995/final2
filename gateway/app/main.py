"""
Gateway API 메인 파일 (단일 파일 통합 버전)
- CORS 설정
- 헬스 체크
- 범용 프록시(/api/v1/{service}/{path})
- 서비스 디스커버리 기능(환경변수 기반)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx

# 환경 변수 로드 (.env는 로컬에서만 사용)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

# 서비스 맵 구성 (MSA 원칙: 각 서비스는 독립적인 URL을 가져야 함)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "https://auth-service-production-d3.up.railway.app")
CAL_BOUNDARY_URL = os.getenv("CAL_BOUNDARY_URL", "https://lcafinal-production.up.railway.app")

# Railway 배포 현황: CBAM 서비스가 통합되어 있음
# 모든 CBAM 관련 도메인은 하나의 서비스에서 처리

# 환경변수 디버깅 로그
logger.info(f"🔧 환경변수 확인:")
logger.info(f"   CAL_BOUNDARY_URL: {CAL_BOUNDARY_URL}")
logger.info(f"   AUTH_SERVICE_URL: {AUTH_SERVICE_URL}")
logger.info(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not Set')}")

SERVICE_MAP = {
    "auth": AUTH_SERVICE_URL,
    # CBAM 서비스 (통합 서비스) - 모든 도메인을 처리
    "boundary": CAL_BOUNDARY_URL,
    # 프론트엔드 호환용 별칭
    "cal-boundary": CAL_BOUNDARY_URL,
    "cal_boundary": CAL_BOUNDARY_URL,
    # 국가/지역 관련 서비스 (boundary 서비스에서 처리)
    "countries": CAL_BOUNDARY_URL,
    # Material Directory 서비스 (CBAM 서비스에서 처리)
    "matdir": CAL_BOUNDARY_URL,
    # Process Chain 서비스 (CBAM 서비스에서 처리)
    "processchain": CAL_BOUNDARY_URL,
    # 기타 CBAM 관련 서비스들
    "product": CAL_BOUNDARY_URL,
    "process": CAL_BOUNDARY_URL,
    "edge": CAL_BOUNDARY_URL,
    "mapping": CAL_BOUNDARY_URL,
    "fueldir": CAL_BOUNDARY_URL,
    "productprocess": CAL_BOUNDARY_URL,
    "calculation": CAL_BOUNDARY_URL,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 시작 (단일 파일 통합)")
    logger.info(f"🔗 SERVICE_MAP: {SERVICE_MAP}")
    yield
    logger.info("🛑 Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - Railway 배포 버전 (MSA 아키텍처)",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS 설정 - 프론트엔드 오리진만 허용 (게이트웨이 자기 자신은 제외)
allowed_origins = [o.strip() for o in os.getenv("CORS_URL", "").split(",") if o.strip()]
if not allowed_origins:
    allowed_origins = [
        "https://lca-final.vercel.app",  # Vercel 프로덕션 프론트엔드
        "http://localhost:3000",  # 로컬 개발 환경
    ]
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=allow_headers,
)

logger.info(f"🔧 CORS 설정 완료:")
logger.info(f"   허용된 오리진: {allowed_origins}")
logger.info(f"   자격증명 허용: {allow_credentials}")
logger.info(f"   허용된 메서드: {allow_methods}")
logger.info(f"   허용된 헤더: {allow_headers}")

# 프록시 유틸리티
async def proxy_request(service: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        logger.error(f"❌ Unknown service: {service}")
        return JSONResponse(status_code=404, content={"detail": f"Unknown service: {service}"})

    # MSA 원칙: 각 서비스는 자체 경로 구조를 가져야 함
    # Gateway는 단순히 요청을 전달만 함 (경로 조작 금지)
    normalized_path = path

    target_url = f"{base_url.rstrip('/')}/{normalized_path}"
    
    # 라우팅 정보 로깅
    logger.info(f"🔄 프록시 라우팅: {service} -> {target_url}")
    logger.info(f"   원본 경로: {path}")
    logger.info(f"   정규화된 경로: {normalized_path}")
    logger.info(f"   서비스: {service}")
    logger.info(f"   기본 URL: {base_url}")
    
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    params = dict(request.query_params)
    body = await request.body()

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=params,
                content=body,
            )
            
            # 응답 상태 코드 로깅
            logger.info(f"✅ 프록시 응답: {method} {target_url} -> {resp.status_code}")
            
        except httpx.RequestError as e:
            logger.error(f"❌ Upstream request error: {e}")
            return JSONResponse(
                status_code=502, 
                content={
                    "detail": "Bad Gateway", 
                    "error": str(e),
                    "service": service,
                    "target_url": target_url
                }
            )
        except httpx.TimeoutException as e:
            logger.error(f"❌ Upstream timeout: {e}")
            return JSONResponse(
                status_code=504, 
                content={
                    "detail": "Gateway Timeout", 
                    "error": str(e),
                    "service": service,
                    "target_url": target_url
                }
            )
        except Exception as e:
            logger.error(f"❌ Unexpected proxy error: {e}")
            return JSONResponse(
                status_code=500, 
                content={
                    "detail": "Internal Gateway Error", 
                    "error": str(e),
                    "service": service,
                    "target_url": target_url
                }
            )

    # 응답 헤더 정리
    response_headers = {k: v for k, v in resp.headers.items() 
                       if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}}
    
    return Response(
        content=resp.content, 
        status_code=resp.status_code, 
        headers=response_headers, 
        media_type=resp.headers.get("content-type")
    )

# 범용 프록시 라우트 (메인 라우팅 역할)
@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy(service: str, path: str, request: Request):
    # OPTIONS 요청은 CORS preflight이므로 Gateway에서 직접 처리
    if request.method == "OPTIONS":
        # CORS 헤더를 일관되게 설정
        origin = request.headers.get("origin", "")
        logger.info(f"🔍 CORS preflight 요청 - origin: {origin}, 허용된 origins: {allowed_origins}")
        
        if origin in allowed_origins:
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Max-Age": "86400",
                }
            )
        else:
            logger.warning(f"🚫 CORS origin 거부: {origin}")
            return Response(
                status_code=400,
                content={"detail": "Origin not allowed", "requested_origin": origin, "allowed_origins": allowed_origins},
                headers={"Access-Control-Allow-Origin": allowed_origins[0] if allowed_origins else ""}
            )
    
    return await proxy_request(service, path, request)



# 헬스 체크
@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root():
    return {
        "status": "healthy", 
        "service": "gateway", 
        "version": "1.0.0",
        "environment": "railway-production",
        "services": {
            "auth": AUTH_SERVICE_URL,
            "cbam": CAL_BOUNDARY_URL,
            "database": "postgres-production-0d25.up.railway.app"
        }
    }

# 요청 로깅
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# 예외 처리
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error("🚨 404")
    return JSONResponse(status_code=404, content={"detail": f"Not Found: {request.url}", "path": request.url.path})

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error("🚨 405")
    return JSONResponse(status_code=405, content={"detail": f"Method Not Allowed: {request.method} {request.url}"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
