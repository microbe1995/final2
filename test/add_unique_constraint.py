#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB의 install 테이블에 install_name UNIQUE 제약조건 추가
"""

import asyncio
import asyncpg

async def add_unique_constraint():
    """install_name UNIQUE 제약조건 추가"""
    
    # Railway DB 주소
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        print("✅ Railway DB 연결 성공")
        
        # install_name UNIQUE 제약조건 추가
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
        
        # 제약조건 확인
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
                AND tc.constraint_type = 'UNIQUE'
            ORDER BY tc.constraint_name
        """)
        
        print("\n🔒 UNIQUE 제약조건:")
        print("-" * 80)
        if constraints:
            for constraint in constraints:
                print(f"  - {constraint['constraint_name']}: {constraint['constraint_type']} on {constraint['column_name']}")
        else:
            print("  - UNIQUE 제약조건 없음")
        
        await conn.close()
        print("\n✅ 제약조건 추가 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(add_unique_constraint())
