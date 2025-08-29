#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
source_stream 테이블 제거 스크립트
Railway DB에서 불필요한 source_stream 테이블을 제거합니다.
"""

import psycopg2
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway DB 연결 정보
DB_CONFIG = {
    "host": "shortline.proxy.rlwy.net",
    "port": 46071,
    "database": "railway",
    "user": "postgres",
    "password": "eQGfytQNhXYAZxsJYlFhYagpJAgstrni"
}

def connect_to_db():
    """Railway DB에 연결"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Railway DB 연결 성공")
        return connection
    except Exception as e:
        logger.error(f"❌ Railway DB 연결 실패: {e}")
        return None

def check_table_exists(connection, table_name: str) -> bool:
    """테이블 존재 여부 확인"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            if exists:
                logger.info(f"📋 테이블 '{table_name}' 존재함")
            else:
                logger.info(f"❌ 테이블 '{table_name}' 존재하지 않음")
            
            return exists
    except Exception as e:
        logger.error(f"❌ 테이블 존재 여부 확인 실패: {e}")
        return False

def get_table_info(connection, table_name: str):
    """테이블 정보 조회"""
    try:
        with connection.cursor() as cursor:
            # 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            logger.info(f"📊 테이블 '{table_name}' 구조:")
            for col in columns:
                logger.info(f"   - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # 데이터 개수 확인
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            logger.info(f"📈 테이블 '{table_name}' 데이터 개수: {count}")
            
            return columns, count
    except Exception as e:
        logger.error(f"❌ 테이블 정보 조회 실패: {e}")
        return [], 0

def remove_source_stream_table(connection):
    """source_stream 테이블 제거"""
    try:
        table_name = "source_stream"
        
        # 1. 테이블 존재 여부 확인
        if not check_table_exists(connection, table_name):
            logger.info("✅ source_stream 테이블이 이미 존재하지 않음")
            return True
        
        # 2. 테이블 정보 조회
        columns, count = get_table_info(connection, table_name)
        
        # 3. 데이터가 있는 경우 경고
        if count > 0:
            logger.warning(f"⚠️ source_stream 테이블에 {count}개의 데이터가 있습니다!")
            logger.warning("⚠️ 데이터 손실을 방지하려면 백업을 먼저 수행하세요!")
            
            # 사용자 확인 (실제 운영에서는 주석 처리)
            # confirm = input("정말로 테이블을 제거하시겠습니까? (yes/no): ")
            # if confirm.lower() != 'yes':
            #     logger.info("❌ 사용자가 테이블 제거를 취소함")
            #     return False
        
        # 4. 테이블 제거
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            connection.commit()
            logger.info(f"✅ 테이블 '{table_name}' 제거 완료")
        
        # 5. 제거 확인
        if not check_table_exists(connection, table_name):
            logger.info("✅ source_stream 테이블 제거 확인 완료")
            return True
        else:
            logger.error("❌ source_stream 테이블 제거 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ source_stream 테이블 제거 실패: {e}")
        return False

def cleanup_related_objects(connection):
    """관련 객체들 정리"""
    try:
        with connection.cursor() as cursor:
            # 관련 시퀀스 확인
            cursor.execute("""
                SELECT sequence_name
                FROM information_schema.sequences
                WHERE sequence_name LIKE '%source_stream%';
            """)
            
            sequences = cursor.fetchall()
            if sequences:
                logger.info(f"🔍 관련 시퀀스 발견: {len(sequences)}개")
                for seq in sequences:
                    logger.info(f"   - {seq[0]}")
            
            # 관련 제약조건 확인
            cursor.execute("""
                SELECT constraint_name, table_name, constraint_type
                FROM information_schema.table_constraints
                WHERE table_name LIKE '%source_stream%';
            """)
            
            constraints = cursor.fetchall()
            if constraints:
                logger.info(f"🔍 관련 제약조건 발견: {len(constraints)}개")
                for const in constraints:
                    logger.info(f"   - {const[0]} ({const[1]}.{const[2]})")
            
            # 관련 인덱스 확인
            cursor.execute("""
                SELECT indexname, tablename
                FROM pg_indexes
                WHERE tablename LIKE '%source_stream%';
            """)
            
            indexes = cursor.fetchall()
            if indexes:
                logger.info(f"🔍 관련 인덱스 발견: {len(indexes)}개")
                for idx in indexes:
                    logger.info(f"   - {idx[0]} ({idx[1]})")
                    
    except Exception as e:
        logger.error(f"❌ 관련 객체 정리 중 오류: {e}")

def main():
    """메인 함수"""
    logger.info("🚀 source_stream 테이블 제거 시작")
    logger.info("="*80)
    
    # 1. DB 연결
    connection = connect_to_db()
    if not connection:
        logger.error("❌ DB 연결 실패로 인해 스크립트 종료")
        return
    
    try:
        # 2. source_stream 테이블 제거
        success = remove_source_stream_table(connection)
        
        if success:
            # 3. 관련 객체들 정리
            cleanup_related_objects(connection)
            
            logger.info("="*80)
            logger.info("✅ source_stream 테이블 제거 완료!")
            logger.info("✅ 이제 Edge 기반의 단순한 공정 연결 관리만 사용됩니다")
            logger.info("="*80)
        else:
            logger.error("❌ source_stream 테이블 제거 실패")
            
    except Exception as e:
        logger.error(f"❌ 스크립트 실행 중 오류: {e}")
        
    finally:
        # 4. DB 연결 종료
        if connection:
            connection.close()
            logger.info("🔌 DB 연결 종료")

if __name__ == "__main__":
    main()
