"""
데이터베이스 연결 설정 관리
환경변수 우선순위 및 기본값 설정
"""
import os
from typing import Optional

class DatabaseConfig:
    """데이터베이스 연결 설정 관리 클래스"""
    
    @staticmethod
    def get_database_url() -> Optional[str]:
        """
        데이터베이스 URL 반환 (우선순위 순서)
        
        우선순위:
        1. DATABASE_URL (직접 설정)
        2. DATABASE_INTERNAL_URL (Railway 내부 네트워크)
        3. DATABASE_PUBLIC_URL (Railway 퍼블릭 네트워크)
        4. 로컬 개발용 설정
        """
        # 1순위: 직접 설정된 DATABASE_URL
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        
        # 2순위: Railway 내부 네트워크 (권장)
        if os.getenv("DATABASE_INTERNAL_URL"):
            return os.getenv("DATABASE_INTERNAL_URL")
        
        # 3순위: Railway 퍼블릭 네트워크
        if os.getenv("DATABASE_PUBLIC_URL"):
            return os.getenv("DATABASE_PUBLIC_URL")
        
        # 4순위: 로컬 개발용 설정
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "cbam_db")
        db_user = os.getenv("DB_USER", "cbam_user")
        db_password = os.getenv("DB_PASSWORD", "cbam_password")
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @staticmethod
    def is_railway_environment() -> bool:
        """Railway 환경인지 확인"""
        return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"))
    
    @staticmethod
    def is_internal_network() -> bool:
        """내부 네트워크 사용 여부 확인"""
        db_url = DatabaseConfig.get_database_url()
        if not db_url:
            return False
        
        # Railway 내부 도메인 확인
        return "railway.internal" in db_url or "postgres.railway.internal" in db_url
