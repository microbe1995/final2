#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
제품 테이블에 attr_em 컬럼 추가 스크립트
"""

import asyncio
import asyncpg
import os

async def add_product_attr_em_column():
    """제품 테이블에 attr_em 컬럼을 추가합니다."""
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        # attr_em 컬럼이 이미 존재하는지 확인
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'product' AND column_name = 'attr_em'
            );
        """)
        
        if result:
            print("✅ attr_em 컬럼이 이미 존재합니다.")
        else:
            print("⚠️ attr_em 컬럼이 없습니다. 추가합니다...")
            
            # attr_em 컬럼 추가
            await conn.execute("""
                ALTER TABLE product 
                ADD COLUMN attr_em DECIMAL(15,6) DEFAULT 0.0
            """)
            
            print("✅ attr_em 컬럼 추가 완료")
        
        # 업데이트된 스키마 확인
        schema_result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'product' AND column_name = 'attr_em'
        """)
        
        if schema_result:
            row = schema_result[0]
            print(f"📋 attr_em 컬럼 정보:")
            print(f"  컬럼명: {row['column_name']}")
            print(f"  데이터타입: {row['data_type']}")
            print(f"  NULL 허용: {row['is_nullable']}")
            print(f"  기본값: {row['column_default']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 컬럼 추가 실패: {e}")

if __name__ == "__main__":
    asyncio.run(add_product_attr_em_column())
