# ============================================================================
# ⚙️ Database Configuration - 데이터베이스 설정
# ============================================================================

"""
데이터베이스 연결 설정을 관리하는 모듈

환경 변수를 통해 데이터베이스 연결 정보를 설정하고 관리합니다.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from loguru import logger

class DatabaseConfig(BaseSettings):
    """데이터베이스 설정 클래스"""
    
    # PostgreSQL 연결 설정
    host: str = Field(default="localhost", env="DB_HOST", description="데이터베이스 호스트")
    port: int = Field(default=5432, env="DB_PORT", description="데이터베이스 포트")
    database: str = Field(default="cal_boundary_db", env="DB_NAME", description="데이터베이스 이름")
    username: str = Field(default="postgres", env="DB_USER", description="데이터베이스 사용자명")
    password: str = Field(default="", env="DB_PASSWORD", description="데이터베이스 비밀번호")
    
    # 연결 풀 설정
    min_connections: int = Field(default=1, env="DB_MIN_CONNECTIONS", description="최소 연결 수")
    max_connections: int = Field(default=10, env="DB_MAX_CONNECTIONS", description="최대 연결 수")
    
    # SSL 설정
    ssl_mode: str = Field(default="prefer", env="DB_SSL_MODE", description="SSL 모드")
    
    # 타임아웃 설정
    connect_timeout: int = Field(default=10, env="DB_CONNECT_TIMEOUT", description="연결 타임아웃 (초)")
    command_timeout: int = Field(default=30, env="DB_COMMAND_TIMEOUT", description="명령 타임아웃 (초)")
    
    # 로깅 설정
    echo: bool = Field(default=False, env="DB_ECHO", description="SQL 쿼리 로깅 여부")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def connection_string(self) -> str:
        """PostgreSQL 연결 문자열을 반환합니다"""
        # 기본 연결 문자열
        conn_str = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        # SSL 설정 추가
        if self.ssl_mode != "disable":
            conn_str += f"?sslmode={self.ssl_mode}"
        
        return conn_str
    
    @property
    def async_connection_string(self) -> str:
        """비동기 PostgreSQL 연결 문자열을 반환합니다"""
        # 기본 연결 문자열 (asyncpg용)
        conn_str = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        # SSL 설정 추가
        if self.ssl_mode != "disable":
            conn_str += f"?sslmode={self.ssl_mode}"
        
        return conn_str
    
    def validate_config(self) -> bool:
        """설정 유효성을 검증합니다"""
        try:
            # 필수 필드 검증
            if not all([self.host, self.database, self.username]):
                logger.error("❌ 필수 데이터베이스 설정이 누락되었습니다")
                return False
            
            # 포트 범위 검증
            if not (1 <= self.port <= 65535):
                logger.error(f"❌ 잘못된 포트 번호: {self.port}")
                return False
            
            # 연결 풀 설정 검증
            if self.min_connections > self.max_connections:
                logger.error("❌ 최소 연결 수가 최대 연결 수보다 큽니다")
                return False
            
            # 타임아웃 설정 검증
            if self.connect_timeout <= 0 or self.command_timeout <= 0:
                logger.error("❌ 타임아웃 값은 0보다 커야 합니다")
                return False
            
            logger.info("✅ 데이터베이스 설정 검증 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 설정 검증 실패: {str(e)}")
            return False
    
    def get_connection_params(self) -> dict:
        """연결 매개변수를 딕셔너리로 반환합니다"""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,
            "min_size": self.min_connections,
            "max_size": self.max_connections,
            "ssl": self.ssl_mode != "disable",
            "command_timeout": self.command_timeout,
            "server_settings": {
                "application_name": "cal_boundary_service"
            }
        }
    
    def __str__(self) -> str:
        """설정 정보를 문자열로 반환합니다"""
        return f"DatabaseConfig(host={self.host}, port={self.port}, database={self.database}, user={self.username})"

# 전역 설정 인스턴스
db_config = DatabaseConfig()

# 설정 검증
if not db_config.validate_config():
    logger.warning("⚠️ 데이터베이스 설정에 문제가 있습니다. 기본값을 사용합니다.")
