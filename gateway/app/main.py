"""
Gateway API 메인 파일
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

# 서비스 맵 구성
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "https://auth-service-production-d3.up.railway.app")
CAL_BOUNDARY_URL = os.getenv("CAL_BOUNDARY_URL", "https://lcafinal-production.up.railway.app")

SERVICE_MAP = {
    "auth": AUTH_SERVICE_URL,
    "cbam": CAL_BOUNDARY_URL,
    "cal-boundary": CAL_BOUNDARY_URL,
    "cal_boundary": CAL_BOUNDARY_URL,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 시작")
    yield
    logger.info("🛑 Gateway API 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final - Railway 배포 버전",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# CORS 설정
cors_url_env = os.getenv("CORS_URL", "")
if cors_url_env and cors_url_env.strip():
    allowed_origins = [o.strip() for o in cors_url_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://envioatlas.cloud",
        "https://envioatlas.cloud",
        "https://final2-mu-seven.vercel.app",
        "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# OPTIONS 요청 처리 (CORS preflight)
@app.options("/{full_path:path}")
async def handle_options(full_path: str, request: Request):
    origin = request.headers.get('origin')
    
    response = Response(
        status_code=200,
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
    
    return response

# 프록시 유틸리티
async def proxy_request(service: str, path: str, request: Request) -> Response:
    base_url = SERVICE_MAP.get(service)
    if not base_url:
        logger.error(f"❌ Unknown service: {service}")
        return JSONResponse(status_code=404, content={"detail": f"Unknown service: {service}"})

    # 경로 정규화
    if not path or path == "":
        normalized_path = ""
    else:
        normalized_path = path

    # CBAM 서비스의 주요 경로에 슬래시 추가
    if service == "cbam" and path in ["install", "product", "process", "edge"]:
        normalized_path = path + '/'
    elif service == "cbam" and path.startswith(("install/", "product/", "process/", "edge/")):
        # 동적 경로는 슬래시 제거
        path_parts = path.split('/')
        if len(path_parts) == 2 and path_parts[1].isdigit():
            normalized_path = path.rstrip('/')

    target_url = f"{base_url.rstrip('/')}/{normalized_path}"
    
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    params = dict(request.query_params)
    body = await request.body()

    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        try:
            resp = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                params=params,
                content=body,
            )
            
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
    hop_by_hop_headers = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade", "host", "content-length"
    }
    
    response_headers = {k: v for k, v in resp.headers.items() 
                       if k.lower() not in hop_by_hop_headers}
    
    # HTTP → HTTPS 변환 (CSP 위반 방지)
    for header_name, header_value in response_headers.items():
        if isinstance(header_value, str) and 'http://' in header_value:
            https_value = header_value.replace('http://', 'https://')
            response_headers[header_name] = https_value
    
    # CORS 헤더 설정
    origin = request.headers.get('origin')
    if origin and origin in allowed_origins:
        response_headers["Access-Control-Allow-Origin"] = origin
        response_headers["Access-Control-Allow-Credentials"] = "true"
    else:
        response_headers["Access-Control-Allow-Origin"] = "*"
    
    response_headers.update({
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Expose-Headers": "*",
        "Access-Control-Max-Age": "86400"
    })
    
    return Response(
        content=resp.content, 
        status_code=resp.status_code, 
        headers=response_headers, 
        media_type=resp.headers.get("content-type")
    )

# 범용 프록시 라우트
@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    return await proxy_request(service, path, request)

# 루트 경로 핸들러
@app.get("/", summary="Gateway 루트")
async def root():
    return {
        "message": "🚀 LCA Final Gateway API",
        "description": "Microservices Gateway for LCA Final Project",
        "version": "1.0.0",
        "environment": "railway-production",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": "/api/v1/{service}/{path}"
        },
        "services": {
            "auth": "Authentication Service",
            "cbam": "CBAM Calculation Service",
            "cal-boundary": "CBAM Calculation Service (Legacy)"
        },
        "usage": "Use /api/v1/{service}/{path} to access microservices through Gateway"
    }

# 헬스 체크
@app.get("/health", summary="Gateway 헬스 체크")
async def health_check_root(request: Request):
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
    
    return JSONResponse(content=response_data)

# Favicon 처리
@app.get("/favicon.ico")
async def favicon():
    return Response(
        status_code=204,
        content="",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# 요청 로깅
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    if request.url.path != "/favicon.ico":
        logger.info(f"🌐 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    if request.url.path != "/favicon.ico":
        logger.info(f"🌐 응답: {response.status_code}")
    
    return response

# 예외 처리
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": f"Not Found: {request.url}"})

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    return JSONResponse(status_code=405, content={"detail": f"Method Not Allowed: {request.method} {request.url}"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Gateway API 시작 - 포트: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)