# ============================================================================
# ⚙️ 설정 관리 모듈
# ============================================================================

import os
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드 (존재하는 경우)
load_dotenv()

class Settings:
    """애플리케이션 설정 클래스"""
    
    # ============================================================================
    # 🗄️ 데이터베이스 설정
    # ============================================================================
    
    @property
    def database_url(self) -> str:
        """데이터베이스 연결 URL"""
        # 환경변수에서 가져오거나 기본값 사용
        return os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'
        )
    
    # ============================================================================
    # 🔧 서비스 설정
    # ============================================================================
    
    @property
    def port(self) -> int:
        """서비스 포트"""
        return int(os.getenv('PORT', '8001'))
    
    @property
    def log_level(self) -> str:
        """로그 레벨"""
        return os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def environment(self) -> str:
        """환경 (development, production, test)"""
        return os.getenv('ENVIRONMENT', 'development')
    
    # ============================================================================
    # 🔒 보안 설정
    # ============================================================================
    
    @property
    def secret_key(self) -> str:
        """시크릿 키"""
        return os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    @property
    def debug(self) -> bool:
        """디버그 모드"""
        return self.environment == 'development'

# 전역 설정 인스턴스
settings = Settings()

# ============================================================================
# 📋 사용 예시
# ============================================================================

# from app.config import settings
# database_url = settings.database_url
# port = settings.port
