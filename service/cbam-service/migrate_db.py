#!/usr/bin/env python3
# ============================================================================
# 🗄️ 데이터베이스 마이그레이션 스크립트
# ============================================================================

"""
PostgreSQL collation 문제 해결 및 데이터베이스 초기화 스크립트

Railway PostgreSQL의 collation 버전 불일치 문제를 해결하고
필요한 테이블들을 생성합니다.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """데이터베이스 URL 가져오기"""
    # Railway 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    return database_url

def clean_database_url(url: str) -> str:
    """데이터베이스 URL 정리"""
    import re
    
    # Railway PostgreSQL에서 발생할 수 있는 잘못된 파라미터들 제거
    invalid_params = [
        'db_type', 'db_type=postgresql', 'db_type=postgres',
        'db_type=mysql', 'db_type=sqlite'
    ]
    
    for param in invalid_params:
        if param in url:
            url = url.replace(param, '')
            logger.warning(f"잘못된 데이터베이스 파라미터 제거: {param}")
    
    # 연속된 & 제거
    url = re.sub(r'&&+', '&', url)
    url = re.sub(r'&+$', '', url)
    
    if '?' in url and url.split('?')[1].startswith('&'):
        url = url.replace('?&', '?')
    
    return url

def create_database_engine(database_url: str):
    """데이터베이스 엔진 생성"""
    try:
        clean_url = clean_database_url(database_url)
        
        # Railway PostgreSQL 최적화 설정
        engine_params = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 5,
            'max_overflow': 10,
            'echo': False,
            'connect_args': {
                'connect_timeout': 30,
                'application_name': 'cbam-migration',
                'options': '-c timezone=utc -c client_encoding=utf8'
            }
        }
        
        # SSL 모드 설정
        if 'postgresql' in clean_url.lower():
            if '?' in clean_url:
                clean_url += "&sslmode=require"
            else:
                clean_url += "?sslmode=require"
        
        logger.info(f"데이터베이스 연결 시도: {clean_url.split('@')[1] if '@' in clean_url else clean_url}")
        
        engine = create_engine(clean_url, **engine_params)
        
        # 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 성공")
        
        return engine
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 엔진 생성 실패: {str(e)}")
        sys.exit(1)

def fix_collation_issues(engine):
    """PostgreSQL collation 문제 해결"""
    try:
        with engine.connect() as conn:
            logger.info("🔧 PostgreSQL collation 문제 해결 중...")
            
            # 데이터베이스 버전 확인
            result = conn.execute(text("SELECT current_setting('server_version_num')"))
            version = result.scalar()
            logger.info(f"PostgreSQL 버전: {version}")
            
            # collation 설정
            conn.execute(text("SET client_encoding = 'UTF8'"))
            conn.execute(text("SET timezone = 'UTC'"))
            
            # collation 버전 불일치 해결 시도
            try:
                # 데이터베이스 collation 버전 새로고침
                conn.execute(text("ALTER DATABASE railway REFRESH COLLATION VERSION"))
                logger.info("✅ Collation 버전 새로고침 완료")
            except Exception as e:
                logger.warning(f"Collation 버전 새로고침 실패 (무시 가능): {str(e)}")
            
            # collation 버전 확인
            try:
                result = conn.execute(text("""
                    SELECT collname, collversion 
                    FROM pg_collation 
                    WHERE collname = 'default'
                """))
                collation_info = result.fetchone()
                if collation_info:
                    logger.info(f"현재 collation: {collation_info[0]}, 버전: {collation_info[1]}")
            except Exception as e:
                logger.warning(f"Collation 정보 조회 실패: {str(e)}")
            
            logger.info("✅ Collation 설정 완료")
            
    except Exception as e:
        logger.error(f"❌ Collation 문제 해결 실패: {str(e)}")
        # 치명적 오류가 아니므로 계속 진행

def create_tables(engine):
    """필요한 테이블들을 생성합니다"""
    try:
        with engine.connect() as conn:
            logger.info("🗄️ 데이터베이스 테이블 생성 중...")
            
            # 제품 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS product (
                    product_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    cn_code VARCHAR(50),
                    period_start DATE,
                    period_end DATE,
                    production_qty DECIMAL(10,2) DEFAULT 0,
                    sales_qty DECIMAL(10,2) DEFAULT 0,
                    export_qty DECIMAL(10,2) DEFAULT 0,
                    inventory_qty DECIMAL(10,2) DEFAULT 0,
                    defect_rate DECIMAL(5,4) DEFAULT 0,
                    node_id VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ product 테이블 생성 완료")
            
            # 인덱스 생성
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_product_name ON product(name)"))
            logger.info("✅ 인덱스 생성 완료")
            
            conn.commit()
            logger.info("✅ 모든 테이블 생성 완료")
            
    except Exception as e:
        logger.error(f"❌ 테이블 생성 실패: {str(e)}")
        raise

def insert_sample_data(engine):
    """샘플 데이터를 삽입합니다"""
    try:
        with engine.connect() as conn:
            logger.info("📊 샘플 데이터 삽입 중...")
            
            # 제품 샘플 데이터 확인 및 삽입
            result = conn.execute(text("SELECT COUNT(*) FROM product"))
            if result.scalar() == 0:
                conn.execute(text("""
                    INSERT INTO product (name, cn_code, period_start, period_end, production_qty, sales_qty, export_qty, inventory_qty, defect_rate) VALUES
                    ('철강 제품 A', '7208', '2024-01-01', '2024-12-31', 1000.0, 800.0, 200.0, 100.0, 0.05),
                    ('철강 제품 B', '7210', '2024-01-01', '2024-12-31', 500.0, 400.0, 100.0, 50.0, 0.03)
                """))
                logger.info("✅ 제품 샘플 데이터 삽입 완료")
            else:
                logger.info("ℹ️ 제품 데이터가 이미 존재합니다")
            
            conn.commit()
            
    except Exception as e:
        logger.error(f"❌ 샘플 데이터 삽입 실패: {str(e)}")
        raise

def main():
    """메인 마이그레이션 함수"""
    logger.info("🚀 CBAM 데이터베이스 마이그레이션 시작")
    
    try:
        # 환경변수 로드
        if not os.getenv("RAILWAY_ENVIRONMENT"):
            load_dotenv()
        
        # 데이터베이스 URL 가져오기
        database_url = get_database_url()
        
        # 데이터베이스 엔진 생성
        engine = create_database_engine(database_url)
        
        # Collation 문제 해결
        fix_collation_issues(engine)
        
        # 테이블 생성
        create_tables(engine)
        
        # 샘플 데이터 삽입
        insert_sample_data(engine)
        
        logger.info("🎉 데이터베이스 마이그레이션 완료!")
        
    except Exception as e:
        logger.error(f"❌ 마이그레이션 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
