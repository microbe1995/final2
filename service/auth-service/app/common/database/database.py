"""
데이터베이스 연결 설정
PostgreSQL 연결 및 세션 관리

주요 기능:
- PostgreSQL 연결 설정 (동기/비동기)
- 세션 관리 및 풀링
- 테이블 자동 생성
- Railway 환경 자동 감지
- 내부/퍼블릭 네트워크 우선순위 관리
"""

# ============================================================================
# 📦 필요한 모듈 import
# ============================================================================

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.domain.user.user_entity import Base
from app.common.config import DatabaseConfig

# ============================================================================
# 🔧 로거 설정
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ 데이터베이스 연결 관리 클래스
# ============================================================================

class Database:
    """
    데이터베이스 연결 관리 클래스
    
    주요 기능:
    - PostgreSQL 연결 설정 (동기/비동기)
    - 세션 팩토리 생성
    - 테이블 자동 생성
    - Railway 환경 자동 감지
    """
    
    def __init__(self):
        """데이터베이스 초기화"""
        # 환경변수 우선순위에 따른 데이터베이스 URL 설정
        self.database_url = DatabaseConfig.get_database_url()
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        
        if not self.database_url:
            logger.warning("⚠️ 데이터베이스 URL이 설정되지 않았습니다. 메모리 저장소를 사용합니다.")
            return
        
        # Railway 환경 및 네트워크 타입 로깅
        if DatabaseConfig.is_railway_environment():
            network_type = "내부" if DatabaseConfig.is_internal_network() else "퍼블릭"
            logger.info(f"🔧 Railway 환경 감지 - {network_type} 네트워크 사용")
            
        self._setup_database()
    
    def _setup_database(self):
        """
        데이터베이스 연결 설정
        
        주요 설정:
        - 동기 엔진: 테이블 생성 및 관리용
        - 비동기 엔진: 실제 애플리케이션 사용용
        - 세션 팩토리: 동기/비동기 세션 생성
        """
        try:
            # Railway PostgreSQL URL을 asyncpg 형식으로 변환
            if self.database_url.startswith("postgresql://"):
                async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            else:
                async_url = self.database_url
            
            # 동기 엔진 (테이블 생성용)
            self.engine = create_engine(
                self.database_url,
                poolclass=NullPool,  # Railway에서 권장
                echo=False
            )
            
            # 비동기 엔진 (실제 사용)
            self.async_engine = create_async_engine(
                async_url,
                poolclass=NullPool,  # Railway에서 권장
                echo=False
            )
            
            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.async_engine
            )
            
            logger.info("✅ 데이터베이스 연결 설정 완료")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 설정 실패: {str(e)}")
            self.database_url = None
    
    def create_tables(self):
        """테이블 생성 (기존 테이블이 있으면 스키마 확인, 없으면 생성)"""
        if not self.engine:
            logger.warning("⚠️ 데이터베이스 연결이 설정되지 않았습니다.")
            return False
            
        try:
            with self.engine.connect() as conn:
                # 트랜잭션 시작
                trans = conn.begin()
                try:
                    # 1. 기존 테이블이 있는지 확인
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'users'
                        );
                    """))
                    table_exists = result.scalar()
                    
                    if table_exists:
                        logger.info("✅ 기존 users 테이블 발견 - 스키마 확인 중")
                        
                        # 2. 기존 테이블의 컬럼 구조 확인
                        columns_result = conn.execute(text("""
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_schema = 'public' 
                            AND table_name = 'users'
                            ORDER BY ordinal_position;
                        """))
                        existing_columns = {row[0]: row[1] for row in columns_result.fetchall()}
                        
                        logger.info(f"📋 기존 컬럼: {list(existing_columns.keys())}")
                        
                        # 3. 필요한 컬럼이 모두 있는지 확인
                        required_columns = {
                            'id': 'character varying',
                            'email': 'character varying', 
                            'full_name': 'character varying',
                            'password_hash': 'character varying',
                            'is_active': 'boolean',
                            'created_at': 'timestamp without time zone',
                            'updated_at': 'timestamp without time zone',
                            'last_login': 'timestamp without time zone'
                        }
                        
                        missing_columns = []
                        for col, expected_type in required_columns.items():
                            if col not in existing_columns:
                                missing_columns.append(col)
                        
                        if missing_columns:
                            logger.warning(f"⚠️ 누락된 컬럼 발견: {missing_columns}")
                            logger.info("🔨 누락된 컬럼 추가 중...")
                            
                            # 누락된 컬럼 추가
                            for col in missing_columns:
                                if col == 'id':
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR PRIMARY KEY"))
                                elif col == 'email':
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR UNIQUE NOT NULL"))
                                elif col == 'full_name':
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR NOT NULL"))
                                elif col == 'password_hash':
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} VARCHAR NOT NULL"))
                                elif col == 'is_active':
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} BOOLEAN DEFAULT TRUE"))
                                elif col in ['created_at', 'updated_at', 'last_login']:
                                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} TIMESTAMP"))
                            
                            logger.info("✅ 누락된 컬럼 추가 완료")
                        else:
                            logger.info("✅ 모든 필요한 컬럼이 존재합니다")
                        
                        # 4. 인덱스 확인 및 생성
                        try:
                            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"))
                            logger.info("✅ 이메일 인덱스 확인/생성 완료")
                        except Exception as e:
                            logger.warning(f"⚠️ 인덱스 생성 실패: {str(e)}")
                        
                    else:
                        # 5. 테이블이 없으면 새로 생성
                        logger.info("🔨 users 테이블이 없음 - 새로 생성 시작")
                        Base.metadata.create_all(bind=self.engine)
                        logger.info("✅ 새로운 users 테이블 생성 완료")
                    
                    # 트랜잭션 커밋
                    trans.commit()
                    return True
                    
                except Exception as e:
                    # 트랜잭션 롤백
                    trans.rollback()
                    logger.error(f"❌ 테이블 생성/업데이트 실패: {str(e)}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            return False
    
    def get_session(self):
        """동기 세션 반환"""
        if not self.SessionLocal:
            return None
        return self.SessionLocal()
    
    async def get_async_session(self) -> AsyncSession:
        """비동기 세션 반환"""
        if not self.AsyncSessionLocal:
            return None
        return self.AsyncSessionLocal()
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
        if self.async_engine:
            self.async_engine.dispose()
        logger.info("🔌 데이터베이스 연결 종료")

# 전역 데이터베이스 인스턴스
database = Database()
