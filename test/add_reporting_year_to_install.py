#!/usr/bin/env python3
"""
install 테이블에 reporting_year 컬럼 추가 스크립트
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

def add_reporting_year_column():
    """install 테이블에 reporting_year 컬럼 추가"""
    
    print("🔧 install 테이블에 reporting_year 컬럼 추가 중...")
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # 1. reporting_year 컬럼이 이미 존재하는지 확인
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'install' AND column_name = 'reporting_year'
            """)
            
            if cursor.fetchone():
                print("⚠️ reporting_year 컬럼이 이미 존재합니다.")
                return
            
            # 2. reporting_year 컬럼 추가
            cursor.execute("""
                ALTER TABLE install 
                ADD COLUMN reporting_year INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            
            print("✅ reporting_year 컬럼이 성공적으로 추가되었습니다.")
            
            # 3. 기존 데이터의 reporting_year를 현재 년도로 업데이트
            current_year = datetime.now().year
            cursor.execute("""
                UPDATE install 
                SET reporting_year = %s 
                WHERE reporting_year IS NULL OR reporting_year = 0
            """, (current_year,))
            
            print(f"✅ 기존 데이터의 reporting_year를 {current_year}년으로 업데이트했습니다.")
            
            # 4. 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'install' 
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\n📋 install 테이블 구조:")
            print("=" * 60)
            for col in columns:
                print(f"{col[0]:<20} {col[1]:<15} {col[2]:<10} {col[3] or 'NULL'}")
            print("=" * 60)
            
            # 5. 샘플 데이터 확인
            cursor.execute("""
                SELECT id, name, reporting_year 
                FROM install 
                LIMIT 5
            """)
            
            samples = cursor.fetchall()
            if samples:
                print("\n📊 샘플 데이터:")
                print("=" * 60)
                for sample in samples:
                    print(f"ID: {sample[0]}, 이름: {sample[1]}, 보고년도: {sample[2]}")
                print("=" * 60)
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 install 테이블 마이그레이션 시작")
    print(f"📅 현재 년도: {datetime.now().year}")
    print("-" * 50)
    
    add_reporting_year_column()
    
    print("\n✅ 마이그레이션 완료!")
