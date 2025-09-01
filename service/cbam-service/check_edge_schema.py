#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB edge 테이블 스키마 확인 스크립트
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def check_edge_table_schema():
    """Railway DB의 edge 테이블 스키마 확인"""
    try:
        print("🔍 Railway DB edge 테이블 스키마 확인 중...")
        
        # PostgreSQL 연결
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 1. 테이블 존재 여부 확인
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'edge'
            );
        """)
        
        if not table_exists:
            print("❌ edge 테이블이 존재하지 않습니다!")
            return
        
        print("✅ edge 테이블이 존재합니다.")
        
        # 2. 컬럼 정보 조회
        columns = await conn.fetch("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'edge'
            ORDER BY ordinal_position;
        """)
        
        print("\n📋 edge 테이블 컬럼 정보:")
        print("-" * 80)
        
        schema_info = {}
        for col in columns:
            col_info = {
                "name": col['column_name'],
                "type": col['data_type'],
                "nullable": col['is_nullable'] == 'YES',
                "default": col['column_default'],
                "max_length": col['character_maximum_length'],
                "precision": col['numeric_precision'],
                "scale": col['numeric_scale']
            }
            schema_info[col['column_name']] = col_info
            
            print(f"  {col['column_name']:<20} {col['data_type']:<15} {'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL':<10} Default: {col['column_default'] or 'None'}")
        
        # 3. 제약조건 확인
        constraints = await conn.fetch("""
            SELECT 
                tc.constraint_name,
                tc.constraint_type,
                ccu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu 
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_schema = 'public' 
            AND tc.table_name = 'edge'
            ORDER BY tc.constraint_type, tc.constraint_name;
        """)
        
        print("\n🔒 제약조건:")
        print("-" * 80)
        for constraint in constraints:
            print(f"  {constraint['constraint_type']:<15} {constraint['constraint_name']:<30} {constraint['column_name']}")
        
        # 4. 인덱스 확인
        indexes = await conn.fetch("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'edge'
            ORDER BY indexname;
        """)
        
        print("\n📊 인덱스:")
        print("-" * 80)
        for index in indexes:
            print(f"  {index['indexname']:<30} {index['indexdef']}")
        
        # 5. 샘플 데이터 확인
        sample_data = await conn.fetch("""
            SELECT * FROM edge LIMIT 3;
        """)
        
        print(f"\n📄 샘플 데이터 ({len(sample_data)}개):")
        print("-" * 80)
        if sample_data:
            for i, row in enumerate(sample_data, 1):
                print(f"  Row {i}: {dict(row)}")
        else:
            print("  데이터가 없습니다.")
        
        # 6. 테이블 통계
        total_rows = await conn.fetchval("SELECT COUNT(*) FROM edge;")
        print(f"\n📈 테이블 통계:")
        print("-" * 80)
        print(f"  총 레코드 수: {total_rows}")
        
        await conn.close()
        
        # 결과를 JSON 파일로 저장
        result = {
            "table_exists": table_exists,
            "columns": schema_info,
            "constraints": [dict(c) for c in constraints],
            "indexes": [dict(i) for i in indexes],
            "sample_data": [dict(d) for d in sample_data],
            "total_rows": total_rows,
            "checked_at": datetime.now().isoformat()
        }
        
        with open("railway_edge_schema.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 스키마 정보가 railway_edge_schema.json 파일에 저장되었습니다.")
        
        return schema_info
        
    except Exception as e:
        print(f"❌ 스키마 확인 중 오류 발생: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(check_edge_table_schema())
