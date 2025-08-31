#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB의 install 테이블 구조 확인 스크립트
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check_install_table_structure():
    """install 테이블 구조 확인"""
    
    # 환경변수 로드
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        print("✅ 데이터베이스 연결 성공")
        
        # 1. install 테이블 존재 여부 확인
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'install'
            );
        """)
        
        if not table_exists:
            print("❌ install 테이블이 존재하지 않습니다.")
            return
        
        print("✅ install 테이블 존재")
        
        # 2. install 테이블 컬럼 구조 확인
        columns = await conn.fetch("""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'install'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 install 테이블 컬럼 구조:")
        print("-" * 80)
        for col in columns:
            print(f"  {col['ordinal_position']:2d}. {col['column_name']:<20} {col['data_type']:<20} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL':<10} {col['column_default'] or ''}")
        
        # 3. 외래키 제약조건 확인
        fk_constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'install'
        """)
        
        if fk_constraints:
            print("\n🔗 install 테이블 외래키 제약조건:")
            print("-" * 80)
            for fk in fk_constraints:
                print(f"  - {fk['constraint_name']}: {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        else:
            print("\n⚠️ install 테이블에 외래키 제약조건이 없습니다.")
        
        # 4. 실제 데이터 확인
        data_count = await conn.fetchval("SELECT COUNT(*) FROM install")
        print(f"\n📊 install 테이블 데이터 개수: {data_count}개")
        
        if data_count > 0:
            sample_data = await conn.fetch("""
                SELECT id, install_name, reporting_year, created_at, updated_at
                FROM install
                ORDER BY id
                LIMIT 3
            """)
            
            print("\n📋 샘플 데이터:")
            print("-" * 80)
            for row in sample_data:
                print(f"  ID: {row['id']}, 이름: {row['install_name']}, 년도: {row['reporting_year']}, 생성: {row['created_at']}")
        
        # 5. product 테이블과의 관계 확인
        product_install_id_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'product' AND column_name = 'install_id'
            );
        """)
        
        if product_install_id_exists:
            print("\n✅ product.install_id 컬럼 존재")
            
            # product 테이블에서 install을 참조하는 데이터 확인
            product_count = await conn.fetchval("""
                SELECT COUNT(*) FROM product WHERE install_id IS NOT NULL
            """)
            print(f"  - install_id가 설정된 제품: {product_count}개")
        else:
            print("\n❌ product.install_id 컬럼이 존재하지 않습니다.")
        
        await conn.close()
        print("\n✅ 테이블 구조 확인 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_install_table_structure())
