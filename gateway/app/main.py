"""
Gateway API 메인 파일 - CORS 문제 해결 버전
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
    description="Gateway API for LCA Final - CORS 문제 해결 버전",
    version="0.2.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 설정 - 환경변수 기반 (더 안전한 방식)
CORS_URL = os.getenv("CORS_URL")
if not CORS_URL:
    CORS_URL = "https://lca-final.vercel.app"
    logger.warning("⚠️ CORS_URL 환경변수가 설정되지 않아 기본값 사용")

FRONT_ORIGIN = CORS_URL.strip()
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers")

# 메서드와 헤더를 리스트로 변환
ALLOWED_METHODS = [m.strip() for m in CORS_ALLOW_METHODS.split(",") if m.strip()]
ALLOWED_HEADERS = [h.strip() for h in CORS_ALLOW_HEADERS.split(",") if h.strip()]

# 허용할 origin들을 리스트로 설정 - CORS 문제 해결을 위해 명시적 설정
ALLOWED_ORIGINS = [
    FRONT_ORIGIN,  # 환경변수에서 가져온 값
    "https://lca-final.vercel.app",  # 기본 Vercel 도메인
    "https://lca-final-9th3dtaxw-microbe95s-projects.vercel.app",  # 실제 Vercel 도메인
    "http://localhost:3000",  # 로컬 개발 환경
    "http://127.0.0.1:3000",  # 로컬 개발 환경
]

logger.info(f"🔧 CORS 설정 정보:")
logger.info(f"🔧 CORS_URL: {CORS_URL}")
logger.info(f"🔧 FRONT_ORIGIN: {FRONT_ORIGIN}")
logger.info(f"🔧 ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
logger.info(f"🔧 ALLOWED_METHODS: {ALLOWED_METHODS}")
logger.info(f"🔧 ALLOWED_HEADERS: {ALLOWED_HEADERS}")
logger.info(f"🔧 CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")

# CORS 미들웨어 추가 (더 명시적 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
    expose_headers=["*"],
    max_age=86400,
)

# CORS 헤더를 응답에 강제로 추가하는 함수
def add_cors_headers(response: Response, request: Request) -> Response:
    """응답에 CORS 헤더를 강제로 추가합니다."""
    origin = request.headers.get("origin")
    
    # origin이 허용된 목록에 있으면 해당 origin 사용, 없으면 기본값 사용
    if origin in ALLOWED_ORIGINS:
        allowed_origin = origin
    else:
        allowed_origin = FRONT_ORIGIN
        logger.warning(f"⚠️ 허용되지 않은 origin: {origin}, 기본값 사용: {allowed_origin}")
    
    # CORS 헤더 강제 삽입 (기존 헤더 덮어쓰기)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    
    # 추가 CORS 헤더 (더 안전한 CORS 설정)
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    logger.info(f"🔧 CORS 헤더 추가: Origin={allowed_origin}, Method={request.method}")
    return response

# CORS OPTIONS 요청 처리 - 모든 경로에 대해
@app.options("/{path:path}")
async def any_options(path: str, request: Request):
    """모든 OPTIONS 요청을 처리합니다 (CORS preflight)."""
    logger.info(f"🔧 OPTIONS 요청 처리: {path}")
    
    origin = request.headers.get("origin")
    if origin in ALLOWED_ORIGINS:
        allowed_origin = origin
    else:
        allowed_origin = FRONT_ORIGIN
    
    # 204 No Content로 응답 (CORS preflight 표준)
    response = Response(status_code=204)
    response.headers["Access-Control-Allow-Origin"] = allowed_origin
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    response.headers["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    
    logger.info(f"🔧 OPTIONS 응답 CORS 헤더: Origin={allowed_origin}")
    return response

# 요청 로깅 미들웨어
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    logger.info(f"🌐 요청: {request.method} {request.url.path}")
    logger.info(f"🌐 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = await call_next(request)
    
    # CORS 헤더 강제 추가
    response = add_cors_headers(response, request)
    
    logger.info(f"🌐 응답: {response.status_code}")
    return response

# 기본 엔드포인트들 (정적 경로를 먼저 등록)
@app.get("/")
async def root():
    return {"message": "Gateway API - CORS 문제 해결 버전", "version": "0.2.0"}

@app.get("/register")
async def register_page():
    """회원가입 페이지로 리다이렉트"""
    return {"message": "회원가입 페이지", "redirect_to": "/api/v1/auth/register"}

@app.get("/login")
async def login_page():
    """로그인 페이지로 리다이렉트"""
    return {"message": "로그인 페이지", "redirect_to": "/api/v1/auth/login"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway", "version": "0.2.0"}

@app.get("/health/db")
async def health_check_db():
    return {
        "status": "healthy",
        "service": "gateway",
        "message": "Database health check delegated to auth-service"
    }

# Auth Service URL
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")

logger.info(f"🔧 Auth Service URL: {AUTH_SERVICE_URL}")

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
                
                # CORS 헤더가 포함된 응답 생성
                json_response = JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                # CORS 헤더 강제 추가
                return add_cors_headers(json_response, request)
        else:
            response = JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            return add_cors_headers(response, request)
            
    except Exception as e:
        logger.error(f"GET 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

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
    logger.info(f"🎯 Origin: {request.headers.get('origin', 'N/A')}")
    
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
                
                # CORS 헤더가 포함된 응답 생성
                json_response = JSONResponse(
                    content=response_content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                # CORS 헤더 강제 추가
                return add_cors_headers(json_response, request)
        else:
            response = JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            return add_cors_headers(response, request)

    except Exception as e:
        logger.error(f"POST 프록시 오류: {e}")
        response = JSONResponse(
            content={"detail": f"Gateway error: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

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
                
                json_response = JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                return add_cors_headers(json_response, request)
        else:
            response = JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            return add_cors_headers(response, request)
            
    except Exception as e:
        logger.error(f"PUT 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

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
                
                json_response = JSONResponse(
                    content=response.json() if response.content else {},
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                return add_cors_headers(json_response, request)
        else:
            response = JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            return add_cors_headers(response, request)
            
    except Exception as e:
        logger.error(f"DELETE 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

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
                
                json_response = JSONResponse(
                    content=response.json(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
                return add_cors_headers(json_response, request)
        else:
            response = JSONResponse(
                content={"detail": f"Service {service} not supported"},
                status_code=400
            )
            return add_cors_headers(response, request)
            
    except Exception as e:
        logger.error(f"PATCH 프록시 오류: {str(e)}")
        response = JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )
        return add_cors_headers(response, request)

# 404 에러 핸들러 추가
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"🚨 404 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = JSONResponse(
        status_code=404,
        content={
            "detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )
    
    # CORS 헤더 강제 추가
    return add_cors_headers(response, request)

# 405 에러 핸들러 추가
@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc):
    logger.error(f"🚨 405 Method Not Allowed 에러 발생!")
    logger.error(f"🚨 요청 URL: {request.url}")
    logger.error(f"🚨 요청 메서드: {request.method}")
    logger.error(f"🚨 요청 경로: {request.url.path}")
    logger.error(f"🚨 Origin: {request.headers.get('origin', 'N/A')}")
    
    response = JSONResponse(
        status_code=405,
        content={
            "detail": f"허용되지 않는 HTTP 메서드입니다. 메서드: {request.method}, URL: {request.url}",
            "method": request.method,
            "path": request.url.path
        }
    )
    
    # CORS 헤더 강제 추가
    return add_cors_headers(response, request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port) 