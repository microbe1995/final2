#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB의 install 테이블에 데이터 무결성 제약조건 추가
- install_name UNIQUE 제약조건
- 데이터 검증을 위한 CHECK 제약조건
"""

import asyncio
import asyncpg

async def add_install_constraints():
    """install 테이블에 데이터 무결성 제약조건 추가"""
    
    # Railway DB 주소
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        print("✅ Railway DB 연결 성공")
        
        # 1. 현재 테이블 구조 확인
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'install'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 현재 install 테이블 컬럼 구조:")
        print("-" * 80)
        for col in columns:
            print(f"  - {col['column_name']:<20} {col['data_type']:<20} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL':<10}")
        
        # 2. 현재 제약조건 확인
        constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public' 
                AND tc.table_name = 'install'
            ORDER BY tc.constraint_type, kcu.column_name
        """)
        
        print("\n🔒 현재 제약조건:")
        print("-" * 80)
        if constraints:
            for constraint in constraints:
                print(f"  - {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")
        else:
            print("  - 제약조건 없음")
        
        # 3. install_name UNIQUE 제약조건 추가
        print("\n🔒 install_name UNIQUE 제약조건 추가 중...")
        try:
            await conn.execute("""
                ALTER TABLE install 
                ADD CONSTRAINT install_name_unique UNIQUE (install_name)
            """)
            print("✅ install_name UNIQUE 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️ install_name UNIQUE 제약조건이 이미 존재합니다.")
            else:
                print(f"❌ install_name UNIQUE 제약조건 추가 실패: {str(e)}")
        
        # 4. 데이터 검증을 위한 CHECK 제약조건 추가
        print("\n🔒 데이터 검증 제약조건 추가 중...")
        
        # install_name이 빈 문자열이 아니고 공백만으로 구성되지 않도록
        try:
            await conn.execute("""
                ALTER TABLE install 
                ADD CONSTRAINT install_name_not_empty 
                CHECK (install_name IS NOT NULL AND LENGTH(TRIM(install_name)) > 0)
            """)
            print("✅ install_name_not_empty CHECK 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️ install_name_not_empty CHECK 제약조건이 이미 존재합니다.")
            else:
                print(f"❌ install_name_not_empty CHECK 제약조건 추가 실패: {str(e)}")
        
        # reporting_year가 유효한 범위인지 확인
        try:
            await conn.execute("""
                ALTER TABLE install 
                ADD CONSTRAINT reporting_year_valid 
                CHECK (reporting_year >= 1900 AND reporting_year <= 2100)
            """)
            print("✅ reporting_year_valid CHECK 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e):
                print("ℹ️ reporting_year_valid CHECK 제약조건이 이미 존재합니다.")
            else:
                print(f"❌ reporting_year_valid CHECK 제약조건 추가 실패: {str(e)}")
        
        # 5. 인덱스 추가 (성능 향상)
        print("\n📊 성능 향상을 위한 인덱스 추가 중...")
        
        # install_name에 대한 인덱스 (UNIQUE 제약조건으로 인해 자동 생성됨)
        print("✅ install_name 인덱스 (UNIQUE 제약조건으로 자동 생성됨)")
        
        # reporting_year에 대한 인덱스
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_install_reporting_year 
                ON install (reporting_year)
            """)
            print("✅ reporting_year 인덱스 추가 완료")
        except Exception as e:
            print(f"ℹ️ reporting_year 인덱스: {str(e)}")
        
        # created_at에 대한 인덱스
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_install_created_at 
                ON install (created_at)
            """)
            print("✅ created_at 인덱스 추가 완료")
        except Exception as e:
            print(f"ℹ️ created_at 인덱스: {str(e)}")
        
        # 6. 최종 제약조건 확인
        final_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public' 
                AND tc.table_name = 'install'
            ORDER BY tc.constraint_type, kcu.column_name
        """)
        
        print("\n🔒 최종 제약조건:")
        print("-" * 80)
        for constraint in final_constraints:
            print(f"  - {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")
        
        # 7. 인덱스 확인
        indexes = await conn.fetch("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = 'install'
            ORDER BY indexname
        """)
        
        print("\n📊 인덱스:")
        print("-" * 80)
        for index in indexes:
            print(f"  - {index['indexname']}")
        
        await conn.close()
        print("\n✅ install 테이블 제약조건 및 인덱스 추가 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_install_constraints())
