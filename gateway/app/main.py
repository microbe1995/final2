"""
Gateway API 메인 파일
"""
from fastapi import APIRouter, FastAPI, Request, HTTPException, Body
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

# 환경 변수 로드
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
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

# FastAPI 앱 생성
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

# 메서드와 헤더를 리스트로 변환
ALLOWED_METHODS = [m.strip() for m in CORS_ALLOW_METHODS.split(",") if m.strip()]
ALLOWED_HEADERS = [h.strip() for h in CORS_ALLOW_HEADERS.split(",") if h.strip()]

# 허용할 origin들을 리스트로 설정
ALLOWED_ORIGINS = [
    FRONT_ORIGIN,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://lca-final.vercel.app",
    "https://lca-final-git-main-microbe95.vercel.app",
]

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["*"],
    max_age=86400,
)

# CORS OPTIONS 요청 처리
@app.options("/{path:path}")
async def any_options(path: str, request: Request):
    request_origin = request.headers.get("origin")
    
    if request_origin in ALLOWED_ORIGINS:
        allowed_origin = request_origin
    else:
        allowed_origin = FRONT_ORIGIN
    
    response = Response(content="OK", status_code=200)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Max-Age"] = "86400"
    
    return response

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 요청: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# Gateway 라우터 생성
gateway_router = APIRouter(tags=["Gateway API"], prefix="/api/v1")

# Auth Service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        
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
        logger.error(f"GET 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post_json(
    service: str,
    path: str,
    request: Request,
    payload: dict = Body(..., example={"email": "test@example.com", "password": "****"})
):
    try:
        headers = dict(request.headers)
        headers["content-type"] = "application/json"
        
        if "content-length" in headers:
            del headers["content-length"]
        
        body = json.dumps(payload)
        
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")

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

    except Exception as e:
        logger.error(f"POST 프록시 오류: {e}")
        return JSONResponse(
            content={"detail": f"Gateway error: {str(e)}"},
            status_code=500
        )

@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        body = await request.body()

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
        logger.error(f"PUT 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)

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
        logger.error(f"DELETE 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    try:
        headers = dict(request.headers)
        body = await request.body()

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
        logger.error(f"PATCH 프록시 오류: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 라우터 등록
app.include_router(gateway_router)

# 기본 엔드포인트들
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

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