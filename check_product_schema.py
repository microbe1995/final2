#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
제품 테이블 스키마 확인 스크립트
"""

import asyncio
import asyncpg
import os

async def check_product_schema():
    """제품 테이블 스키마를 확인합니다."""
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        
        # 제품 테이블 스키마 확인
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'product' 
            ORDER BY ordinal_position
        """)
        
        print("📋 Product 테이블 스키마:")
        print("=" * 50)
        for row in result:
            print(f"  {row['column_name']}: {row['data_type']} (NULL: {row['is_nullable']}, Default: {row['column_default']})")
        
        # 제품 테이블 데이터 샘플 확인
        sample_data = await conn.fetch("SELECT * FROM product LIMIT 3")
        if sample_data:
            print(f"\n📊 Product 테이블 데이터 샘플 (최대 3개):")
            print("=" * 50)
            for i, row in enumerate(sample_data, 1):
                print(f"  제품 {i}: {dict(row)}")
        else:
            print("\n⚠️ Product 테이블에 데이터가 없습니다.")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 스키마 확인 실패: {e}")

if __name__ == "__main__":
    asyncio.run(check_product_schema())
