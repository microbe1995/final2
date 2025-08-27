#!/usr/bin/env python3
"""
install 테이블 상태 확인 스크립트
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

# 환경변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    exit(1)

def check_install_table():
    """install 테이블 상태 확인"""
    
    print("🔍 install 테이블 상태 확인 중...")
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # 1. 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'install' 
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\n📋 install 테이블 구조:")
            print("=" * 80)
            for col in columns:
                print(f"{col[0]:<20} {col[1]:<15} {col[2]:<10} {col[3] or 'NULL'}")
            print("=" * 80)
            
            # 2. 현재 데이터 확인
            cursor.execute("""
                SELECT id, name, reporting_year 
                FROM install 
                ORDER BY id
            """)
            
            installs = cursor.fetchall()
            print(f"\n📊 현재 install 테이블 데이터 ({len(installs)}개):")
            print("=" * 80)
            if installs:
                for install in installs:
                    print(f"ID: {install[0]:<5} | 이름: {install[1]:<20} | 보고년도: {install[2]}년")
            else:
                print("❌ 데이터가 없습니다.")
            print("=" * 80)
            
            # 3. reporting_year 컬럼 상세 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'install' AND column_name = 'reporting_year'
            """)
            
            reporting_year_col = cursor.fetchone()
            if reporting_year_col:
                print(f"\n✅ reporting_year 컬럼 확인:")
                print(f"   - 컬럼명: {reporting_year_col[0]}")
                print(f"   - 데이터타입: {reporting_year_col[1]}")
                print(f"   - NULL 허용: {reporting_year_col[2]}")
                print(f"   - 기본값: {reporting_year_col[3]}")
            else:
                print("\n❌ reporting_year 컬럼이 존재하지 않습니다!")
            
            # 4. 테이블 제약조건 확인
            cursor.execute("""
                SELECT constraint_name, constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = 'install'
            """)
            
            constraints = cursor.fetchall()
            print(f"\n🔒 테이블 제약조건:")
            for constraint in constraints:
                print(f"   - {constraint[0]}: {constraint[1]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 install 테이블 상태 확인 시작")
    print(f"📅 현재 시간: {datetime.now()}")
    print("-" * 50)
    
    check_install_table()
    
    print("\n✅ 확인 완료!")
