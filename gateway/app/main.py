"""
Gateway API 메인 파일
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import os
import logging
import sys
import json
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

# 기본 엔드포인트들 (정적 경로를 먼저 등록)
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

# Auth Service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

# 동적 프록시 엔드포인트들
@app.get("/api/v1/{service}/{path:path}")
async def proxy_get(service: str, path: str, request: Request):
    logger.info(f"🎯 GET 프록시 호출: service={service}, path={path}")
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

@app.post("/api/v1/{service}/{path:path}")
async def proxy_post_json(
    service: str,
    path: str,
    request: Request
):
    logger.info(f"🎯 POST 프록시 호출됨!")
    logger.info(f"🎯 service: {service}")
    logger.info(f"🎯 path: {path}")
    logger.info(f"🎯 전체 경로: /api/v1/{service}/{path}")
    logger.info(f"🎯 요청 URL: {request.url}")
    
    try:
        headers = dict(request.headers)
        body = await request.body()
        
        logger.info(f"🎯 요청 본문: {body}")
        logger.info(f"🎯 요청 헤더: {headers}")
        
        if "content-length" in headers:
            del headers["content-length"]
        
        if service == "auth":
            target_url = f"{AUTH_SERVICE_URL}/{path}"
            logger.info(f"🎯 Auth Service로 전달: {target_url}")
            logger.info(f"🎯 전송할 데이터: {body}")
            logger.info(f"🎯 전송할 헤더: {headers}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    target_url, 
                    content=body,
                    headers=headers, 
                    timeout=30.0
                )
                
                logger.info(f"✅ Auth Service 응답: {response.status_code}")
                logger.info(f"✅ Auth Service 응답 헤더: {dict(response.headers)}")
                
                try:
                    response_content = response.json()
                    logger.info(f"✅ Auth Service 응답 내용: {response_content}")
                except:
                    response_content = response.text
                    logger.info(f"✅ Auth Service 응답 내용 (텍스트): {response_content}")
                
                return JSONResponse(
                    content=response_content,
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

@app.put("/api/v1/{service}/{path:path}")
async def proxy_put(service: str, path: str, request: Request):
    logger.info(f"🎯 PUT 프록시 호출: service={service}, path={path}")
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

@app.delete("/api/v1/{service}/{path:path}")
async def proxy_delete(service: str, path: str, request: Request):
    logger.info(f"🎯 DELETE 프록시 호출: service={service}, path={path}")
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

@app.patch("/api/v1/{service}/{path:path}")
async def proxy_patch(service: str, path: str, request: Request):
    logger.info(f"🎯 PATCH 프록시 호출: service={service}, path={path}")
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

# 404 에러 핸들러 추가
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"🚨 404 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 요청 헤더: {dict(request.headers)}")
    
    # 경로 파싱
    path_parts = request.url.path.split('/')
    logger.error(f"🎯 경로 파싱: {path_parts}")
    
    if len(path_parts) >= 5:
        logger.error(f"🎯 추출된 service: {path_parts[3]}")
        logger.error(f"🎯 추출된 path: {path_parts[4:]}")

    return JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )

# 405 에러 핸들러 추가
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error(f"🚨 405 Method Not Allowed 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 요청 헤더: {dict(request.headers)}")
    
    # 경로 파싱
    path_parts = request.url.path.split('/')
    logger.error(f"🎯 경로 파싱: {path_parts}")
    
    if len(path_parts) >= 5:
        logger.error(f"🎯 추출된 service: {path_parts[3]}")
        logger.error(f"🎯 추출된 path: {path_parts[4:]}")

    return JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 