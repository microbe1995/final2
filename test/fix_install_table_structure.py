#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB의 install 테이블 구조 수정 스크립트
- company_name, country 컬럼 제거
"""

import asyncio
import asyncpg

async def fix_install_table_structure():
    """install 테이블 구조 수정"""
    
    # Railway DB 주소
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
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
        
        # 2. 불필요한 컬럼들 제거
        columns_to_remove = ['company_name', 'country']
        
        for col_name in columns_to_remove:
            try:
                # 컬럼이 존재하는지 확인
                col_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'install' 
                        AND column_name = $1
                    );
                """, col_name)
                
                if col_exists:
                    print(f"\n🗑️ {col_name} 컬럼 제거 중...")
                    await conn.execute(f"ALTER TABLE install DROP COLUMN {col_name}")
                    print(f"✅ {col_name} 컬럼 제거 완료")
                else:
                    print(f"ℹ️ {col_name} 컬럼은 이미 존재하지 않습니다.")
                    
            except Exception as e:
                print(f"❌ {col_name} 컬럼 제거 실패: {str(e)}")
        
        # 3. 수정된 테이블 구조 확인
        updated_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'install'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 수정된 install 테이블 컬럼 구조:")
        print("-" * 80)
        for col in updated_columns:
            print(f"  - {col['column_name']:<20} {col['data_type']:<20} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL':<10}")
        
        # 4. 테이블 재생성 (필요시)
        print("\n🔄 테이블 구조를 코드와 일치시키기 위해 재생성...")
        
        # 기존 테이블 삭제
        await conn.execute("DROP TABLE IF EXISTS install CASCADE")
        print("✅ 기존 install 테이블 삭제 완료")
        
        # 새로운 테이블 생성 (코드와 일치)
        await conn.execute("""
            CREATE TABLE install (
                id SERIAL PRIMARY KEY,
                install_name TEXT NOT NULL,
                reporting_year INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM NOW()),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✅ 새로운 install 테이블 생성 완료")
        
        # 5. 최종 테이블 구조 확인
        final_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'install'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 최종 install 테이블 컬럼 구조:")
        print("-" * 80)
        for col in final_columns:
            print(f"  - {col['column_name']:<20} {col['data_type']:<20} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL':<10}")
        
        await conn.close()
        print("\n✅ install 테이블 구조 수정 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fix_install_table_structure())
