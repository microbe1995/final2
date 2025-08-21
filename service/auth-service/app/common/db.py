from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.common.settings import settings
from app.common.logger import auth_logger
import re

def clean_database_url(url: str) -> str:
    """데이터베이스 URL에서 잘못된 파라미터 제거"""
    # Railway PostgreSQL에서 발생할 수 있는 잘못된 파라미터들
    invalid_params = [
        'db_type', 'db_type=postgresql', 'db_type=postgres',
        'db_type=mysql', 'db_type=sqlite'
    ]
    
    # URL에서 잘못된 파라미터 제거
    for param in invalid_params:
        if param in url:
            url = url.replace(param, '')
            auth_logger.warning(f"잘못된 데이터베이스 파라미터 제거: {param}")
    
    # 연속된 & 제거
    url = re.sub(r'&&+', '&', url)
    url = re.sub(r'&+$', '', url)
    
    # URL 시작이 ?로 시작하면 &로 변경
    if '?' in url and url.split('?')[1].startswith('&'):
        url = url.replace('?&', '?')
    
    return url

def create_database_engine():
    """데이터베이스 엔진 생성 (Railway PostgreSQL 최적화)"""
    try:
        # DATABASE_URL 정리
        clean_url = clean_database_url(settings.DATABASE_URL)
        
        # Railway PostgreSQL 최적화 설정
        engine_params = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20,
            'echo': settings.DB_ECHO,
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'greensteel-auth-service'
            }
        }
        
        # SSL 모드 설정
        if settings.DATABASE_SSL_MODE:
            if 'postgresql' in clean_url.lower():
                # PostgreSQL SSL 설정
                if '?' in clean_url:
                    clean_url += f"&sslmode={settings.DATABASE_SSL_MODE}"
                else:
                    clean_url += f"?sslmode={settings.DATABASE_SSL_MODE}"
        
        auth_logger.info(f"데이터베이스 연결 시도: {clean_url.split('@')[1] if '@' in clean_url else clean_url}")
        
        engine = create_engine(clean_url, **engine_params)
        
        # 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            auth_logger.info("데이터베이스 연결 성공")
        
        return engine
        
    except Exception as e:
        auth_logger.error(f"데이터베이스 엔진 생성 실패: {str(e)}")
        raise

# 데이터베이스 엔진 생성
try:
    engine = create_database_engine()
except Exception as e:
    auth_logger.error(f"데이터베이스 초기화 실패: {str(e)}")
    # 폴백: SQLite 사용
    engine = create_engine(
        "sqlite:///./auth_fallback.db",
        pool_pre_ping=True,
        echo=settings.DB_ECHO
    )
    auth_logger.warning("SQLite 폴백 데이터베이스 사용")

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 클래스
Base = declarative_base()

def get_db() -> Session:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """데이터베이스 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        auth_logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        auth_logger.error(f"테이블 생성 실패: {str(e)}")
        raise

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            auth_logger.info(f"데이터베이스 연결 테스트 성공: {version}")
            return True
    except Exception as e:
        auth_logger.error(f"데이터베이스 연결 테스트 실패: {str(e)}")
        return False
