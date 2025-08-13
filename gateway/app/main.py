"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from contextlib import asynccontextmanager

# Gateway API 서비스
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 🚨 강력한 테스트 로그 추가
print("=" * 60)
print("🚀 Gateway API 서비스 시작 - Railway 디버깅 모드")
print("=" * 60)
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"Python 경로: {os.environ.get('PYTHONPATH', '설정되지 않음')}")
print(f"현재 시간: {os.popen('date').read().strip()}")
print("=" * 60)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway_api")

# 🚨 모든 환경변수 출력 (Railway 디버깅용)
print("🔧 모든 환경변수 확인:")
for key, value in os.environ.items():
    if key.startswith(('CORS_', 'RAILWAY_', 'PYTHON')):
        print(f"  - {key}: {value}")
print("=" * 60)

# 환경변수 로드 (Railway 환경이 아닐 때만)
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()
    print("📁 .env 파일에서 환경변수 로드됨")
else:
    print("🚂 Railway 환경에서 실행 중 - .env 파일 로드 안함")
print("=" * 60)

# Railway 환경 감지 및 import 경로 결정
def get_auth_router():
    """Railway 환경에 따라 적절한 import 경로 선택"""
    # Railway 환경 감지 (더 확실한 방법)
    is_railway = (
        os.getenv("RAILWAY_ENVIRONMENT") == "true" or
        os.getenv("RAILWAY_STATIC_URL") is not None or
        os.getenv("PORT") is not None or
        os.getenv("RAILWAY_PROJECT_ID") is not None or
        os.getenv("RAILWAY_SERVICE_ID") is not None
    )
    
    # 디버깅: 환경 변수 출력
    print(f"🔍 환경 변수 확인:")
    print(f"  - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
    print(f"  - RAILWAY_STATIC_URL: {os.getenv('RAILWAY_STATIC_URL')}")
    print(f"  - PORT: {os.getenv('PORT')}")
    print(f"  - RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID')}")
    print(f"  - RAILWAY_SERVICE_ID: {os.getenv('RAILWAY_SERVICE_ID')}")
    print(f"  - /app/main.py 존재: {os.path.exists('/app/main.py')}")
    print(f"  - is_railway: {is_railway}")
    
    # Railway 환경이거나 Docker 컨테이너 내부라면 절대 경로 사용
    if is_railway or os.path.exists("/app/main.py"):
        print(f"🚂 Railway/Docker 환경 감지됨 - 절대 경로 import 사용")
        # Railway/Docker 환경: 절대 경로로 import (app. 접두사 없음)
        try:
            from router.auth_router import auth_router
            print(f"✅ 절대 경로 import 성공: router.auth_router")
            return auth_router
        except ImportError as e:
            print(f"❌ 절대 경로 import 실패: {e}")
            # fallback: 상대 경로 시도
            from .router.auth_router import auth_router
            print(f"✅ 상대 경로 import 성공: .router.auth_router")
            return auth_router
    else:
        print(f"🏠 로컬 개발 환경 감지됨 - 상대 경로 import 사용")
        # 로컬 개발 환경: 상대 경로로 import
        try:
            from .router.auth_router import auth_router
            print(f"✅ 상대 경로 import 성공: .router.auth_router")
            return auth_router
        except ImportError as e:
            print(f"❌ 상대 경로 import 실패: {e}")
            # fallback: 절대 경로 시도 (app. 접두사 없음)
            from router.auth_router import auth_router
            print(f"✅ 절대 경로 import 성공: router.auth_router")
            return auth_router

# auth_router 가져오기
auth_router = get_auth_router()

# Railway 환경이 아닐 때만 .env 파일 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# JSON 형태의 로그 포맷터 클래스
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 추가 필드가 있는 경우 포함
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
            
        return json.dumps(log_entry, ensure_ascii=False)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 루트 로거 설정
root_logger = logging.getLogger()
root_logger.handlers.clear()

# JSON 포맷터 적용
json_formatter = JSONFormatter()
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json_formatter)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS 환경변수 설정
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://lca-final.vercel.app,https://*.vercel.app").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(",")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With,Origin,Access-Control-Request-Method,Access-Control-Request-Headers").split(",")

# CORS 환경변수 디버깅 로그 추가
print(f"🔧 CORS 환경변수 확인:")
print(f"  - CORS_ORIGINS: {CORS_ORIGINS}")
print(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print(f"  - CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
print(f"  - CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
print(f"  - CORS_ORIGINS 원본값: {os.getenv('CORS_ORIGINS')}")
print(f"  - CORS_ALLOW_CREDENTIALS 원본값: {os.getenv('CORS_ALLOW_CREDENTIALS')}")
print(f"  - CORS_ALLOW_METHODS 원본값: {os.getenv('CORS_ALLOW_METHODS')}")
print(f"  - CORS_ALLOW_HEADERS 원본값: {os.getenv('CORS_ALLOW_HEADERS')}")

# CORS 미들웨어 설정 (OPTIONS 핸들러보다 먼저)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel 서브도메인 정규식
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=["*"],  # 모든 응답 헤더 노출
    max_age=86400,  # CORS preflight 캐시 시간 (24시간)
)

# CORS preflight 요청을 위한 OPTIONS 핸들러 추가 (CORS 미들웨어보다 먼저)
@app.options("/api/v1/auth/register")
async def auth_register_options():
    """회원가입 API에 대한 OPTIONS 요청 처리 (CORS preflight)"""
    logger.info(f"🌐 회원가입 OPTIONS 요청 처리")
    
    # 환경변수 기반 CORS 헤더 설정
    from fastapi.responses import Response
    response = Response(content="OK", status_code=200)
    
    # CORS 헤더 설정 전 환경변수 확인
    logger.info(f"🔧 회원가입 OPTIONS CORS 헤더 설정:")
    logger.info(f"  - CORS_ORIGINS: {CORS_ORIGINS}")
    logger.info(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
    logger.info(f"  - CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
    logger.info(f"  - CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
    
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGINS[0] if CORS_ORIGINS else "https://lca-final.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_ALLOW_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    
    # 설정된 헤더 확인
    logger.info(f"🌐 회원가입 OPTIONS 응답 헤더 설정 완료:")
    logger.info(f"  - Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    logger.info(f"  - Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
    logger.info(f"  - Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers')}")
    logger.info(f"  - Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
    
    return response

@app.options("/api/v1/auth/login")
async def auth_login_options():
    """로그인 API에 대한 OPTIONS 요청 처리 (CORS preflight)"""
    logger.info(f"🌐 로그인 OPTIONS 요청 처리")
    
    # 환경변수 기반 CORS 헤더 설정
    from fastapi.responses import Response
    response = Response(content="OK", status_code=200)
    
    # CORS 헤더 설정 전 환경변수 확인
    logger.info(f"🔧 로그인 OPTIONS CORS 헤더 설정:")
    logger.info(f"  - CORS_ORIGINS: {CORS_ORIGINS}")
    logger.info(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
    logger.info(f"  - CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
    logger.info(f"  - CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
    
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGINS[0] if CORS_ORIGINS else "https://lca-final.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_ALLOW_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    
    # 설정된 헤더 확인
    logger.info(f"🌐 로그인 OPTIONS 응답 헤더 설정 완료:")
    logger.info(f"  - Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    logger.info(f"  - Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
    logger.info(f"  - Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers')}")
    logger.info(f"  - Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
    
    return response

# 모든 API 경로에 대한 범용 OPTIONS 핸들러
@app.options("/api/{full_path:path}")
async def api_options(full_path: str):
    """모든 API 경로에 대한 OPTIONS 요청 처리 (CORS preflight)"""
    logger.info(f"🌐 API OPTIONS 요청 처리: /api/{full_path}")
    
    # 환경변수 기반 CORS 헤더 설정
    from fastapi.responses import Response
    response = Response(content="OK", status_code=200)
    
    # CORS 헤더 설정 전 환경변수 확인
    logger.info(f"🔧 API OPTIONS CORS 헤더 설정:")
    logger.info(f"  - CORS_ORIGINS: {CORS_ORIGINS}")
    logger.info(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
    logger.info(f"  - CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
    logger.info(f"  - CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
    
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGINS[0] if CORS_ORIGINS else "https://lca-final.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_ALLOW_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    
    # 설정된 헤더 확인
    logger.info(f"🌐 API OPTIONS 응답 헤더 설정 완료:")
    logger.info(f"  - Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    logger.info(f"  - Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
    logger.info(f"  - Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers')}")
    logger.info(f"  - Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
    
    return response

# 루트 경로에 대한 OPTIONS 핸들러 추가
@app.options("/")
async def root_options():
    """루트 경로에 대한 OPTIONS 요청 처리"""
    logger.info(f"🌐 루트 OPTIONS 요청 처리")
    
    from fastapi.responses import Response
    response = Response(content="OK", status_code=200)
    
    # CORS 헤더 설정 전 환경변수 확인
    logger.info(f"🔧 루트 OPTIONS CORS 헤더 설정:")
    logger.info(f"  - CORS_ORIGINS: {CORS_ORIGINS}")
    logger.info(f"  - CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
    logger.info(f"  - CORS_ALLOW_METHODS: {CORS_ALLOW_METHODS}")
    logger.info(f"  - CORS_ALLOW_HEADERS: {CORS_ALLOW_HEADERS}")
    
    response.headers["Access-Control-Allow-Origin"] = CORS_ORIGINS[0] if CORS_ORIGINS else "https://lca-final.vercel.app"
    response.headers["Access-Control-Origin"] = CORS_ORIGINS[0] if CORS_ORIGINS else "https://lca-final.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = ", ".join(CORS_ALLOW_METHODS)
    response.headers["Access-Control-Allow-Headers"] = ", ".join(CORS_ALLOW_HEADERS)
    response.headers["Access-Control-Max-Age"] = "86400"
    response.headers["Access-Control-Allow-Credentials"] = str(CORS_ALLOW_CREDENTIALS).lower()
    
    # 설정된 헤더 확인
    logger.info(f"🌐 루트 OPTIONS 응답 헤더 설정 완료:")
    logger.info(f"  - Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
    logger.info(f"  - Access-Control-Allow-Methods: {response.headers.get('access-control-allow-methods')}")
    logger.info(f"  - Access-Control-Allow-Headers: {response.headers.get('access-control-allow-headers')}")
    logger.info(f"  - Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials')}")
    
    return response

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])
gateway_router.include_router(auth_router)
app.include_router(gateway_router)

# CORS 디버깅을 위한 미들웨어 추가
@app.middleware("http")
async def cors_debug_middleware(request: Request, call_next):
    """CORS 요청 디버깅을 위한 미들웨어"""
    # 요청 정보 로깅
    logger.info(f"🌐 CORS 요청: {request.method} {request.url}")
    logger.info(f"🌐 Origin: {request.headers.get('origin', 'No Origin')}")
    logger.info(f"🌐 User-Agent: {request.headers.get('user-agent', 'No User-Agent')}")
    
    # 응답 처리
    response = await call_next(request)
    
    # CORS 헤더 확인
    cors_headers = {
        'Access-Control-Allow-Origin': response.headers.get('access-control-allow-origin'),
        'Access-Control-Allow-Methods': response.headers.get('access-control-allow-methods'),
        'Access-Control-Allow-Headers': response.headers.get('access-control-allow-headers'),
    }
    logger.info(f"🌐 CORS 응답 헤더: {cors_headers}")
    
    return response

@app.get("/health", summary="테스트 엔드포인트")
async def health_check():
    return {"status": "healthy!"}

@gateway_router.get("/health", summary="테스트 엔드포인트")
async def gateway_health_check():
    return {"status": "gateway healthy!"}

# 기본 루트 경로햣
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

# Railway 배포를 위한 uvicorn 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 