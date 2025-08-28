#!/usr/bin/env python3
"""
HS-CN 매핑 테이블 생성 스크립트
CBAM 서비스 내에서 Railway PostgreSQL 데이터베이스에 hs_cn_mapping 테이블을 생성합니다.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

def get_database_url():
    """데이터베이스 URL 가져오기"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL 환경변수를 찾을 수 없습니다.")
        return None
    
    return database_url

def create_hs_cn_mapping_table():
    """HS-CN 매핑 테이블 생성"""
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        # 데이터베이스 연결
        logger.info("🔗 데이터베이스에 연결 중...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'hs_cn_mapping'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            logger.info("⚠️  hs_cn_mapping 테이블이 이미 존재합니다.")
            # 기존 테이블 삭제 (자동으로)
            cursor.execute("DROP TABLE hs_cn_mapping CASCADE;")
            logger.info("🗑️  기존 테이블을 삭제했습니다.")
        
        # 테이블 생성
        logger.info("📋 hs_cn_mapping 테이블을 생성 중...")
        cursor.execute("""
            CREATE TABLE hs_cn_mapping (
                id SERIAL PRIMARY KEY,
                hscode CHAR(6) NOT NULL,            -- HS 코드 (앞 6자리)
                aggregoods_name TEXT,               -- 품목군명
                aggregoods_engname TEXT,            -- 품목군영문명
                cncode_total CHAR(8) NOT NULL,      -- CN 코드 (8자리)
                goods_name TEXT,                    -- 품목명
                goods_engname TEXT                  -- 품목영문명
            );
        """)
        
        # 인덱스 생성 (성능 최적화)
        logger.info("🔍 인덱스를 생성 중...")
        cursor.execute("""
            CREATE INDEX idx_hs_cn_mapping_hscode ON hs_cn_mapping(hscode);
        """)
        
        cursor.execute("""
            CREATE INDEX idx_hs_cn_mapping_cncode ON hs_cn_mapping(cncode_total);
        """)
        
        # 변경사항 커밋
        conn.commit()
        logger.info("✅ hs_cn_mapping 테이블이 성공적으로 생성되었습니다!")
        
        # 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'hs_cn_mapping'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("\n📊 테이블 구조:")
        logger.info("-" * 80)
        logger.info(f"{'컬럼명':<20} {'데이터타입':<15} {'NULL허용':<10} {'기본값'}")
        logger.info("-" * 80)
        for col in columns:
            logger.info(f"{col[0]:<20} {col[1]:<15} {col[2]:<10} {col[3] or 'None'}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ 데이터베이스 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("🚀 HS-CN 매핑 테이블 생성 스크립트")
    logger.info("=" * 50)
    
    success = create_hs_cn_mapping_table()
    
    if success:
        logger.info("\n🎉 테이블 생성이 완료되었습니다!")
        logger.info("\n📝 다음 단계:")
        logger.info("1. HS-CN 매핑 데이터를 테이블에 삽입")
        logger.info("2. product 테이블의 product_cncode 필드와 연결")
        logger.info("3. CBAM 계산 로직에서 CN 코드 기반 분류 활용")
    else:
        logger.error("\n❌ 테이블 생성에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
