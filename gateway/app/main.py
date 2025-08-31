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

# 환경변수 디버깅 로그
logger.info(f"🔧 환경변수 확인:")
logger.info(f"   CAL_BOUNDARY_URL: {CAL_BOUNDARY_URL}")
logger.info(f"   AUTH_SERVICE_URL: {AUTH_SERVICE_URL}")
logger.info(f"   RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not Set')}")

SERVICE_MAP = {
    "auth": AUTH_SERVICE_URL,
    # CBAM 서비스 (통합 서비스) - 모든 도메인을 처리
    "cal-boundary": CAL_BOUNDARY_URL,
    "cal_boundary": CAL_BOUNDARY_URL,
    "boundary": CAL_BOUNDARY_URL,
    "countries": CAL_BOUNDARY_URL,
    "matdir": CAL_BOUNDARY_URL,
    "processchain": CAL_BOUNDARY_URL,
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
    logger.info("🚀 Gateway API 시작")
    
    # 필수 환경변수 확인
    required_envs = {
        "AUTH_SERVICE_URL": AUTH_SERVICE_URL,
        "CAL_BOUNDARY_URL": CAL_BOUNDARY_URL,
    }
    
    for env_name, env_value in required_envs.items():
        if env_value and env_value.startswith("https://"):
            logger.info(f"   ✅ {env_name}: {env_value}")
        else:
            logger.warning(f"   ⚠️ {env_name}: {env_value}")
    
    # CORS 설정 확인
    if not allowed_origins:
        logger.warning("   ⚠️ CORS 허용 오리진이 설정되지 않았습니다")
    else:
        logger.info(f"   ✅ CORS 허용 오리진: {len(allowed_origins)}개")
    
    logger.info("🔗 등록된 서비스 목록:")
    for service_name, service_url in SERVICE_MAP.items():
        logger.info(f"   {service_name}: {service_url}")
    
    yield
    logger.info("🛑 Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - Railway 배포 버전 (MSA 아키텍처)",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS 설정 - 프론트엔드 오리진만 허용
cors_url_env = os.getenv("CORS_URL", "")
if cors_url_env and cors_url_env.strip():
    allowed_origins = [o.strip() for o in cors_url_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "https://lca-final.vercel.app",  # Vercel 프로덕션 프론트엔드
        "https://greensteel.site",       # 커스텀 도메인 (있다면)
        "http://localhost:3000",         # 로컬 개발 환경
    ]

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
allow_methods = [m.strip() for m in os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")]
allow_headers = [h.strip() for h in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")]

# CORS 설정 전 로깅
logger.info(f"🔧 CORS 설정 준비:")
logger.info(f"   환경변수 CORS_URL: {os.getenv('CORS_URL', 'Not Set')}")
logger.info(f"   최종 허용된 오리진: {allowed_origins}")
logger.info(f"   자격증명 허용: {allow_credentials}")
logger.info(f"   허용된 메서드: {allow_methods}")
logger.info(f"   허용된 헤더: {allow_headers}")

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

# OPTIONS 요청 처리 (CORS preflight)
@app.options("/{full_path:path}")
async def handle_options(full_path: str, request: Request):
    origin = request.headers.get('origin')
    logger.info(f"🌐 OPTIONS {full_path} origin={origin}")
    
    # CORS preflight 응답 - 항상 성공
    response = Response(
        status_code=200,  # 🔴 수정: 항상 200 OK 반환
        content="",
        headers={
            "Access-Control-Allow-Origin": origin if origin and origin in allowed_origins else allowed_origins[0] if allowed_origins else "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
            "Access-Control-Allow-Credentials": "true",
            "Content-Type": "text/plain",
        }
    )
    
    logger.info(f"🌐 응답: 200 (OPTIONS) - CORS 허용: {origin}")
    return response

# 프록시 유틸리티
async def proxy_request(service: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        logger.error(f"❌ Unknown service: {service}")
        return JSONResponse(status_code=404, content={"detail": f"Unknown service: {service}"})

    # 빈 경로 처리
    if not path or path == "":
        if service == "install":
            normalized_path = "install"
            logger.info(f"🔍 Install 서비스 빈 경로 감지 → /install으로 매핑")
        else:
            normalized_path = ""
            logger.info(f"🔍 빈 경로 감지: service={service}, path='{path}' → 루트 경로로 전달")
    else:
        normalized_path = path

    target_url = f"{base_url.rstrip('/')}/{normalized_path}".rstrip('/')
    
    # 라우팅 정보 로깅
    logger.info(f"🔄 프록시 라우팅: {service} -> {target_url}")
    
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
                    "target_url": target_url
                }
            )

    # 응답 헤더 정리
    response_headers = {k: v for k, v in resp.headers.items() 
                       if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}}
    
    # CORS 헤더 설정
    origin = request.headers.get('origin')
    if origin and origin in allowed_origins:
        response_headers["Access-Control-Allow-Origin"] = origin
        response_headers["Access-Control-Allow-Credentials"] = "true"
    
    return Response(
        content=resp.content, 
        status_code=resp.status_code, 
        headers=response_headers, 
        media_type=resp.headers.get("content-type")
    )

# 범용 프록시 라우트 (메인 라우팅 역할)
@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    return await proxy_request(service, path, request)

# 헬스 체크
@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root(request: Request):
    origin = request.headers.get('origin')
    response_data = {
        "status": "healthy", 
        "service": "gateway", 
        "version": "1.0.0",
        "environment": "railway-production",
        "services": {
            "auth": AUTH_SERVICE_URL,
            "cbam": CAL_BOUNDARY_URL,
        }
    }
    
    response = JSONResponse(content=response_data)
    
    # 🔴 추가: CORS 헤더 설정
    if origin and origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Favicon 처리 (브라우저 자동 요청 방지)
@app.get("/favicon.ico")
async def favicon():
    return Response(
        status_code=204,  # No Content
        content="",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# 요청 로깅
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    # favicon.ico 요청은 로깅에서 제외
    if request.url.path != "/favicon.ico":
        logger.info(f"🌐 {request.method} {request.url.path} origin={request.headers.get('origin','N/A')}")
    
    response = await call_next(request)
    
    # favicon.ico 응답은 로깅에서 제외
    if request.url.path != "/favicon.ico":
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
