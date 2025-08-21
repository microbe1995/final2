import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    """Auth 서비스 설정 - DDD Architecture"""
    
    # 서비스 기본 정보
    SERVICE_NAME: str = "greensteel-auth-service"
    SERVICE_VERSION: str = "3.0.0"
    LOG_LEVEL: str = "INFO"
    
    # 서비스 포트 설정
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # 데이터베이스 설정
    DATABASE_URL: str = ""
    DATABASE_SSL_MODE: str = "require"
    DB_ECHO: bool = False
    
    # JWT 설정
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: str = "24h"
    JWT_REFRESH_EXPIRES_IN: str = "7d"
    
    # CORS 설정 (Railway 배포용)
    ALLOWED_ORIGINS: str = "https://lca-final.vercel.app,https://gateway-production-22ef.up.railway.app"
    ALLOWED_ORIGIN_REGEX: str = "^https://.*\\.vercel\\.app$|^https://.*\\.up\\.railway\\.app$"
    
    # 보안 설정
    SECRET_KEY: str = ""
    PASSWORD_SALT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 300  # 5분
    
    
    # 로깅 설정
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "auth_service.log"
    
    # 모니터링 설정
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9091
    HEALTH_CHECK_INTERVAL: int = 30
    
    # 개발 환경 설정
    DEBUG: bool = False
    RELOAD: bool = False
    ENVIRONMENT: str = "production"
    
    # 외부 서비스 연동 (Railway 배포용)
    GATEWAY_URL: str = "https://gateway-production-22ef.up.railway.app"
    REDIS_URL: Optional[str] = None
    
    # 이메일 설정 (선택사항)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    ENABLE_EMAIL_VERIFICATION: bool = False
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: str = "image/jpeg,image/png,application/pdf,text/csv"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW_MS: int = 900000  # 15분
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # DDD 도메인 설정
    DOMAIN_EVENTS_ENABLED: bool = True
    AGGREGATE_SNAPSHOT_INTERVAL: int = 50
    EVENT_STORE_TYPE: str = "postgresql"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # JWT_SECRET이 없으면 임시 랜덤 생성
        if not self.JWT_SECRET:
            self.JWT_SECRET = secrets.token_urlsafe(32)
        
        # SECRET_KEY가 없으면 임시 랜덤 생성
        if not self.SECRET_KEY:
            self.SECRET_KEY = secrets.token_urlsafe(32)
        
        # DATABASE_URL이 비어있으면 SQLite 폴백
        if not self.DATABASE_URL:
            self.DATABASE_URL = "sqlite:///./auth.db"
        
        # Railway 환경에서 동적 설정 적용
        self._apply_environment_settings()
    
    @property
    def origins_list(self) -> List[str]:
        """ALLOWED_ORIGINS를 콤마로 분리하여 리스트 반환"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    @property
    def database_url(self) -> str:
        """데이터베이스 URL 반환 (PostgreSQL 우선, SQLite 폴백)"""
        return self.DATABASE_URL
    
    @property
    def jwt_secret(self) -> str:
        """JWT 시크릿 키 반환"""
        return self.JWT_SECRET
    
    @property
    def jwt_algorithm(self) -> str:
        """JWT 알고리즘 반환"""
        return self.JWT_ALGORITHM
    
    @property
    def access_expires_minutes(self) -> int:
        """액세스 토큰 만료 시간(분) 반환 - JWT_EXPIRES_IN에서 파싱"""
        try:
            # "24h" -> 1440분, "30m" -> 30분 등 파싱
            time_str = self.JWT_EXPIRES_IN.lower()
            if 'h' in time_str:
                hours = int(time_str.replace('h', ''))
                return hours * 60
            elif 'm' in time_str:
                return int(time_str.replace('m', ''))
            elif 'd' in time_str:
                days = int(time_str.replace('d', ''))
                return days * 24 * 60
            else:
                return 30  # 기본값
        except:
            return 30
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """허용된 파일 타입을 리스트로 반환"""
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",") if ft.strip()]
    
    @property
    def is_development(self) -> bool:
        """개발 환경 여부 확인"""
        return self.ENVIRONMENT.lower() in ['development', 'dev', 'local']
    
    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부 확인"""
        return self.ENVIRONMENT.lower() in ['production', 'prod']
    
    def _apply_environment_settings(self):
        """환경별 동적 설정 적용"""
        # Railway 환경 감지
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            # Railway 운영 환경 설정
            self.ENVIRONMENT = "production"
            
            # Railway 환경변수 기반 CORS 설정 (환경변수가 있으면 덮어쓰기)
            cors_url = os.getenv("CORS_URL")
            if cors_url:
                self.ALLOWED_ORIGINS = cors_url
                
            # Railway 환경변수 기반 Gateway URL
            gateway_url = os.getenv("GATEWAY_URL")
            if gateway_url:
                self.GATEWAY_URL = gateway_url
        else:
            # 로컬 개발 환경 설정
            self.ENVIRONMENT = "development"
            self.ALLOWED_ORIGINS = "http://localhost:3000"
            self.GATEWAY_URL = "http://localhost:8080"
    
    @property
    def service_info(self) -> dict:
        """서비스 정보 반환"""
        return {
            "name": self.SERVICE_NAME,
            "version": self.SERVICE_VERSION,
            "environment": self.ENVIRONMENT,
            "port": self.PORT,
            "architecture": "DDD (Domain-Driven Design)",
            "features": {
                "domain_events": self.DOMAIN_EVENTS_ENABLED,
                "metrics": self.ENABLE_METRICS,
                "email_verification": self.ENABLE_EMAIL_VERIFICATION
            }
        }

# 전역 설정 인스턴스
settings = Settings()
