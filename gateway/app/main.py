"""
gateway-router 메인 파일
"""
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import httpx

print("=" * 60)
print("Gateway API 서비스 시작 - Railway 디버깅 모드")
print("=" * 60)
print(f"작업 디렉토리: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '설정되지 않음')}")
print("=" * 60)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("gateway_api")

if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for LCA Final",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정 - 환경변수 기반
FRONT_ORIGIN = os.getenv("FRONT_ORIGIN", "https://lca-final.vercel.app").strip()
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers")

# 메서드와 헤더를 리스트로 변환 (공백 제거)
ALLOWED_METHODS = [m.strip() for m in CORS_ALLOW_METHODS.split(",") if m.strip()]
ALLOWED_HEADERS = [h.strip() for h in CORS_ALLOW_HEADERS.split(",") if h.strip()]

# 허용할 origin들을 리스트로 설정 (개발 및 프로덕션 환경 모두 지원)
ALLOWED_ORIGINS = [
    FRONT_ORIGIN,  # 기본 Vercel 프론트엔드
    "http://localhost:3000",  # 로컬 개발
    "http://127.0.0.1:3000",  # 로컬 IP
    "https://lca-final.vercel.app",  # Vercel 프로덕션
    "https://lca-final-git-main-microbe95.vercel.app",  # Vercel 프리뷰
]

# CORS 설정 로그 출력
print(f"🔧 CORS 설정 확인:")
print(f"  - FRONT_ORIGIN: '{FRONT_ORIGIN}'")
print(f"  - ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
print(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print(f"  - ALLOWED_METHODS: {ALLOWED_METHODS}")
print(f"  - ALLOWED_HEADERS: {ALLOWED_HEADERS}")
print("=" * 60)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # 여러 origin 허용
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["*"],
    max_age=86400,
)

@app.options("/{path:path}")
async def any_options(path: str, request: Request):
    # 요청의 origin을 확인
    request_origin = request.headers.get("origin")
    
    # origin이 허용된 목록에 있는지 확인
    if request_origin in ALLOWED_ORIGINS:
        allowed_origin = request_origin
    else:
        allowed_origin = FRONT_ORIGIN  # 기본값 사용
    
    response = Response(content="OK", status_code=200)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Max-Age"] = "86400"
    
    # CORS preflight 로깅
    print(f"🔍 CORS OPTIONS 요청 처리:")
    print(f"  - Path: {path}")
    print(f"  - Request Origin: {request_origin}")
    print(f"  - Allowed Origin: {allowed_origin}")
    print(f"  - Methods: {', '.join(ALLOWED_METHODS)}")
    print(f"  - Headers: {', '.join(ALLOWED_HEADERS)}")
    
    return response

# 모든 요청 로깅 미들웨어 추가
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 모든 요청 로깅: {request.method} {request.url.path}")
    logger.info(f"🌐 요청 헤더: {dict(request.headers)}")
    
    # 응답 처리
    response = await call_next(request)
    
    logger.info(f"🌐 응답 상태: {response.status_code}")
    return response

# ===== [여기부터 핵심 수정] 내부 서비스로 넘길 때 붙일 기본 prefix =====
FORWARD_BASE_PATH = "api/v1"
# ================================================================

# 라우터 생성
logger.info("🔧 Gateway 라우터 생성 시작...")

gateway_router = APIRouter(tags=["Gateway API"], prefix="/api/v1")

# 라우터 등록 확인 로그
logger.info("🔧 Gateway 라우터 생성 완료")
logger.info(f"🔧 라우터 prefix: {gateway_router.prefix}")
logger.info(f"🔧 라우터 tags: {gateway_router.tags}")

# Auth Service URL - 로컬 개발 환경
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: str, 
    path: str, 
    request: Request
):
    logger.info("🚀 GET 프록시 함수 시작!")
    try:
        headers = dict(request.headers)
        
        # auth-service로 요청 전달
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(target_url, headers=headers, timeout=30.0)
                
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        else:
            return JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error in GET proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.post("/{service}/{path:path}", summary="POST 프록시 (JSON 전용)")
async def proxy_post_json(
    service: str,
    path: str,
    request: Request,
    # ✅ JSON 전용 바디 선언 → Swagger에 JSON 에디터 표시
    payload: Dict[str, Any] = Body(
        ...,  # required
        example={"email": "test@example.com", "password": "****"}
    ),
):
    logger.info(f"🚀 POST 프록시(JSON) 시작: service={service}, path={path}")
    logger.info(f"🚀 요청 URL: {request.url}")

    try:
        headers = dict(request.headers)
        headers["content-type"] = "application/json"
        
        # Content-Length 헤더 제거 (자동 계산되도록)
        if "content-length" in headers:
            del headers["content-length"]
        
        body = json.dumps(payload)
        
        # auth-service로 요청 전달
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")
            logger.info(f"🔧 전달할 body 크기: {len(body) if body else 0} bytes")
            logger.info(f"🔧 전달할 headers: {headers}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    target_url, 
                    content=body,
                    headers=headers, 
                    timeout=30.0
                )
                
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        else:
            return JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )

    except HTTPException as he:
        return JSONResponse(content={"detail": he.detail}, status_code=he.status_code)
    except Exception as e:
        logger.error(f"🚨 POST(JSON) 처리 중 오류: {e}", exc_info=True)
        return JSONResponse(
            content={"detail": f"Gateway error: {str(e)}", "error_type": type(e).__name__},
            status_code=500
        )

@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        body = await request.body()

        # auth-service로 요청 전달
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    target_url, 
                    content=body,
                    headers=headers, 
                    timeout=30.0
                )
                
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        else:
            return JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error in PUT proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        body = await request.body()

        # auth-service로 요청 전달
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    target_url, 
                    headers=headers, 
                    timeout=30.0
                )
                
                return JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        else:
            return JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error in DELETE proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        body = await request.body()

        # auth-service로 요청 전달
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    target_url, 
                    content=body,
                    headers=headers, 
                    timeout=30.0
                )
                
                return JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        else:
            return JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            
    except Exception as e:
        logger.error(f"Error in PATCH proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 라우터 등록 (모든 엔드포인트 정의 후)
logger.info("🔧 라우터 등록 중...")
app.include_router(gateway_router)
logger.info("✅ Gateway 라우터 등록 완료")

# 라우트 등록 확인 (모든 라우트 함수 정의 후)
logger.info("🔍 등록된 라우트들:")
post_routes_found = 0
for route in app.routes:
    if hasattr(route, 'path'):
        logger.info(f"  - {route.methods} {route.path}")
        if 'POST' in route.methods and '{service}' in route.path:
            post_routes_found += 1
            logger.info(f"🎯 POST 동적 라우트 발견: {route.path}")
            logger.info(f"🎯 라우트 함수: {route.endpoint.__name__ if hasattr(route, 'endpoint') else 'Unknown'}")

logger.info(f"🎯 총 POST 동적 라우트 개수: {post_routes_found}")

logger.info(f"🔍 gateway_router.routes 개수: {len(gateway_router.routes)}")
for route in gateway_router.routes:
    if hasattr(route, 'path'):
        logger.info(f"  - {route.methods} {route.path}")

logger.info("🎯 라우트 매칭 테스트:")
test_path = "/api/v1/auth/login"
logger.info(f"🎯 테스트 경로: {test_path}")
logger.info(f"🎯 경로에서 service 추출: {test_path.split('/')[3] if len(test_path.split('/')) > 3 else 'N/A'}")
logger.info(f"🔍 경로에서 path 추출: {test_path.split('/')[4:] if len(test_path.split('/')) > 4 else 'N/A'}")

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"🚨 404 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 요청 쿼리: {request.query_params}")
    logger.error(f"🚨 요청 헤더: {dict(request.headers)}")
    
    path_parts = request.url.path.split('/')
    logger.error(f"🎯 경로 파싱: {path_parts}")
    if len(path_parts) >= 5:
        logger.error(f"🎯 추출된 service: {path_parts[3]}")
        logger.error(f"🚨 추출된 path: {path_parts[4:]}")
    
    logger.error(f"🚨 등록된 라우트들:")
    for route in app.routes:
        if hasattr(route, 'path'):
            logger.error(f"  - {route.methods} {route.path}")
    
    logger.error(f"🚨 gateway_router 라우트들:")
    for route in gateway_router.routes:
        if hasattr(route, 'path'):
            logger.error(f"  - {route.methods} {route.path}")
    
    return JSONResponse(
        status_code=404,
        content={"detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}"}
    )

@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

@app.get("/health")
async def health_check_root():
    logger.info("🔍😁😁😁😁😁 루트 헬스 체크는 성공 !!!! ")
    return {"status": "healthy", "service": "gateway", "path": "root"}

@app.get("/health/db")
async def health_check_db():
    return {
        "status": "healthy",
        "service": "gateway",
        "message": "Database health check delegated to auth-service"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 