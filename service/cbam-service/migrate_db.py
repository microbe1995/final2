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
            
            # 연료 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS fuels (
                    id SERIAL PRIMARY KEY,
                    fuel_name VARCHAR(255) NOT NULL,
                    fuel_eng VARCHAR(255),
                    fuel_emfactor DECIMAL(10,2),
                    net_calory DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ fuels 테이블 생성 완료")
            
            # 원료 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS materials (
                    id SERIAL PRIMARY KEY,
                    item_name VARCHAR(255) NOT NULL,
                    item_eng VARCHAR(255),
                    carbon_factor DECIMAL(10,2),
                    em_factor DECIMAL(10,2),
                    cn_code VARCHAR(50),
                    cn_code1 VARCHAR(50),
                    cn_code2 VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("✅ materials 테이블 생성 완료")
            
            # 전구물질 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS precursors (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    calculation_type VARCHAR(50) NOT NULL,
                    fuel_id INTEGER,
                    material_id INTEGER,
                    quantity DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fuel_id) REFERENCES fuels(id) ON DELETE SET NULL,
                    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET NULL
                )
            """))
            logger.info("✅ precursors 테이블 생성 완료")
            
            # 계산 결과 테이블 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS calculation_results (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    calculation_type VARCHAR(50) NOT NULL,
                    fuel_id INTEGER,
                    material_id INTEGER,
                    quantity DECIMAL(10,2) NOT NULL,
                    result_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fuel_id) REFERENCES fuels(id) ON DELETE SET NULL,
                    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET NULL
                )
            """))
            logger.info("✅ calculation_results 테이블 생성 완료")
            
            # 인덱스 생성
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fuels_name ON fuels(fuel_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_materials_name ON materials(item_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_precursors_user ON precursors(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_calculation_results_user ON calculation_results(user_id)"))
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
            
            # 연료 샘플 데이터 확인 및 삽입
            result = conn.execute(text("SELECT COUNT(*) FROM fuels"))
            if result.scalar() == 0:
                conn.execute(text("""
                    INSERT INTO fuels (fuel_name, fuel_eng, fuel_emfactor, net_calory) VALUES
                    ('천연가스', 'Natural Gas', 56.1, 48.0),
                    ('석탄', 'Coal', 94.6, 25.8),
                    ('중유', 'Heavy Oil', 77.4, 40.4),
                    ('경유', 'Diesel', 74.1, 42.7),
                    ('휘발유', 'Gasoline', 69.3, 44.3)
                """))
                logger.info("✅ 연료 샘플 데이터 삽입 완료")
            else:
                logger.info("ℹ️ 연료 데이터가 이미 존재합니다")
            
            # 원료 샘플 데이터 확인 및 삽입
            result = conn.execute(text("SELECT COUNT(*) FROM materials"))
            if result.scalar() == 0:
                conn.execute(text("""
                    INSERT INTO materials (item_name, item_eng, carbon_factor, em_factor, cn_code, cn_code1, cn_code2) VALUES
                    ('철광석', 'Iron Ore', 0.5, 0.024, '2601', '260111', '26011100'),
                    ('석회석', 'Limestone', 12.0, 0.034, '2521', '252100', '25210000'),
                    ('코크스', 'Coke', 85.0, 2.8, '2704', '270400', '27040000'),
                    ('철스크랩', 'Iron Scrap', 0.1, 0.005, '7204', '720400', '72040000')
                """))
                logger.info("✅ 원료 샘플 데이터 삽입 완료")
            else:
                logger.info("ℹ️ 원료 데이터가 이미 존재합니다")
            
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
