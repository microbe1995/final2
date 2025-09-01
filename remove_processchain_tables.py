#!/usr/bin/env python3
"""
============================================================================
🗑️ ProcessChain 관련 테이블 제거 스크립트
============================================================================
이 스크립트는 ProcessChain 도메인 제거에 따라 관련 테이블들을 삭제합니다.
Edge 기반 배출량 전파로 통일되었으므로 이 테이블들은 더 이상 필요하지 않습니다.

사용법:
python remove_processchain_tables.py
"""

import psycopg2
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_table_exists(conn: psycopg2.extensions.connection, table_name: str) -> bool:
    """테이블이 존재하는지 확인합니다."""
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = %s
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (table_name,))
        result = cursor.fetchone()
        return result[0] if result else False

def get_table_info(conn: psycopg2.extensions.connection, table_name: str) -> Optional[dict]:
    """테이블 정보를 조회합니다."""
    query = """
    SELECT 
        table_name,
        (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = %s) as column_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (table_name, table_name))
        result = cursor.fetchone()
        if result:
            return {
                'table_name': result[0],
                'column_count': result[1]
            }
        return None

def get_table_row_count(conn: psycopg2.extensions.connection, table_name: str) -> int:
    """테이블의 행 수를 조회합니다."""
    try:
        query = f"SELECT COUNT(*) FROM {table_name};"
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.warning(f"테이블 {table_name} 행 수 조회 실패: {e}")
        return 0

def remove_processchain_tables():
    """ProcessChain 관련 테이블들을 안전하게 제거합니다."""
    conn = None
    try:
        # 데이터베이스 연결
        logger.info("🔌 데이터베이스에 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("✅ 데이터베이스 연결 성공")

        # 제거할 테이블 목록
        tables_to_remove = ['process_chain_link', 'process_chain']
        
        for table_name in tables_to_remove:
            logger.info(f"🔍 테이블 '{table_name}' 확인 중...")
            
            # 테이블 존재 여부 확인
            if not check_table_exists(conn, table_name):
                logger.info(f"⚠️ 테이블 '{table_name}'이 존재하지 않습니다. 건너뜁니다.")
                continue
            
            # 테이블 정보 조회
            table_info = get_table_info(conn, table_name)
            if table_info:
                logger.info(f"📋 테이블 '{table_name}' 정보: {table_info['column_count']}개 컬럼")
                
                # 행 수 확인
                row_count = get_table_row_count(conn, table_name)
                logger.info(f"📊 테이블 '{table_name}' 행 수: {row_count}개")
                
                if row_count > 0:
                    logger.warning(f"⚠️ 테이블 '{table_name}'에 {row_count}개의 데이터가 있습니다!")
                    response = input(f"테이블 '{table_name}'을 삭제하시겠습니까? (y/N): ")
                    if response.lower() != 'y':
                        logger.info(f"❌ 테이블 '{table_name}' 삭제가 취소되었습니다.")
                        continue
            
            # 외래키 제약조건 제거 (process_chain_link의 경우)
            if table_name == 'process_chain_link':
                logger.info("🔗 외래키 제약조건 제거 중...")
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            ALTER TABLE process_chain_link 
                            DROP CONSTRAINT IF EXISTS process_chain_link_chain_id_fkey;
                        """)
                        cursor.execute("""
                            ALTER TABLE process_chain_link 
                            DROP CONSTRAINT IF EXISTS process_chain_link_process_id_fkey;
                        """)
                        conn.commit()
                    logger.info("✅ 외래키 제약조건 제거 완료")
                except Exception as e:
                    logger.warning(f"⚠️ 외래키 제약조건 제거 중 오류 (무시됨): {e}")
                    conn.rollback()
            
            # 테이블 삭제
            logger.info(f"🗑️ 테이블 '{table_name}' 삭제 중...")
            with conn.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                conn.commit()
            logger.info(f"✅ 테이블 '{table_name}' 삭제 완료")
        
        # 남은 테이블 확인
        logger.info("📋 남은 테이블 목록 확인 중...")
        remaining_tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        with conn.cursor() as cursor:
            cursor.execute(remaining_tables_query)
            remaining_tables = cursor.fetchall()
        
        logger.info("📊 남은 테이블 목록:")
        for table in remaining_tables:
            logger.info(f"  - {table[0]}")
        
        logger.info("🎉 ProcessChain 관련 테이블 제거 작업이 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("🔌 데이터베이스 연결 종료")

def main():
    """메인 함수"""
    print("=" * 60)
    print("🗑️ ProcessChain 관련 테이블 제거 스크립트")
    print("=" * 60)
    print()
    print("⚠️  주의사항:")
    print("   - 이 스크립트는 process_chain과 process_chain_link 테이블을 완전히 삭제합니다.")
    print("   - 삭제된 데이터는 복구할 수 없습니다.")
    print("   - 테이블에 데이터가 있는 경우 확인 후 삭제합니다.")
    print()
    
    response = input("계속하시겠습니까? (y/N): ")
    if response.lower() != 'y':
        print("❌ 작업이 취소되었습니다.")
        return
    
    try:
        remove_processchain_tables()
        print()
        print("✅ 모든 작업이 성공적으로 완료되었습니다!")
    except Exception as e:
        print(f"❌ 작업 중 오류가 발생했습니다: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code or 0)
