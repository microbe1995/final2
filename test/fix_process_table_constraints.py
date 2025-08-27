#!/usr/bin/env python3
"""
process 테이블의 start_period, end_period 컬럼을 NULL 허용으로 변경하는 스크립트
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# DB 연결 정보
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway")

def fix_process_table_constraints():
    """process 테이블의 제약조건 수정"""
    print("🔧 process 테이블 제약조건 수정 시작...")
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    try:
        with conn.cursor() as cursor:
            # 현재 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'process' 
                AND column_name IN ('start_period', 'end_period')
                ORDER BY column_name
            """)
            
            columns = cursor.fetchall()
            print("📋 현재 컬럼 상태:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({col[2]})")
            
            # start_period 컬럼을 NULL 허용으로 변경
            print("\n🔧 start_period 컬럼을 NULL 허용으로 변경...")
            cursor.execute("""
                ALTER TABLE process 
                ALTER COLUMN start_period DROP NOT NULL
            """)
            print("✅ start_period NOT NULL 제약조건 제거 완료")
            
            # end_period 컬럼을 NULL 허용으로 변경
            print("🔧 end_period 컬럼을 NULL 허용으로 변경...")
            cursor.execute("""
                ALTER TABLE process 
                ALTER COLUMN end_period DROP NOT NULL
            """)
            print("✅ end_period NOT NULL 제약조건 제거 완료")
            
            # 변경 후 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, is_nullable, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'process' 
                AND column_name IN ('start_period', 'end_period')
                ORDER BY column_name
            """)
            
            columns_after = cursor.fetchall()
            print("\n📋 변경 후 컬럼 상태:")
            for col in columns_after:
                print(f"  - {col[0]}: {col[1]} ({col[2]})")
            
            print("\n🎉 process 테이블 제약조건 수정 완료!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    fix_process_table_constraints()
