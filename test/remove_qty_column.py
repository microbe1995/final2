#!/usr/bin/env python3
"""
Railway DB의 edge 테이블에서 qty 컬럼을 삭제하는 마이그레이션 스크립트
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def remove_qty_column():
    """edge 테이블에서 qty 컬럼을 삭제합니다."""
    
    # DATABASE_URL 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        print("🔗 Railway DB 연결 중...")
        conn = await asyncpg.connect(database_url)
        print("✅ DB 연결 성공")
        
        # 1. 현재 edge 테이블 구조 확인
        print("\n📋 현재 edge 테이블 구조 확인...")
        check_sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'edge' 
        ORDER BY ordinal_position;
        """
        
        result = await conn.fetch(check_sql)
        print("현재 edge 테이블 컬럼:")
        for row in result:
            print(f"  - {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        # 2. qty 컬럼 존재 여부 확인
        qty_exists = any(row['column_name'] == 'qty' for row in result)
        if not qty_exists:
            print("\nℹ️ qty 컬럼이 이미 존재하지 않습니다.")
            return
        
        # 3. qty 컬럼 삭제
        print("\n🗑️ qty 컬럼 삭제 중...")
        drop_sql = "ALTER TABLE edge DROP COLUMN IF EXISTS qty;"
        
        await conn.execute(drop_sql)
        print("✅ qty 컬럼 삭제 완료")
        
        # 4. 삭제 후 테이블 구조 재확인
        print("\n📋 삭제 후 edge 테이블 구조 확인...")
        result = await conn.fetch(check_sql)
        print("삭제 후 edge 테이블 컬럼:")
        for row in result:
            print(f"  - {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
        
        # 5. 결과 저장
        migration_result = {
            "migration_date": datetime.now().isoformat(),
            "operation": "remove_qty_column",
            "table": "edge",
            "column_removed": "qty",
            "status": "success",
            "message": "qty 컬럼이 성공적으로 삭제되었습니다."
        }
        
        with open("qty_column_removal_result.json", "w", encoding="utf-8") as f:
            json.dump(migration_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 결과가 qty_column_removal_result.json에 저장되었습니다.")
        print("🎯 qty 컬럼 삭제 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        # 오류 결과 저장
        error_result = {
            "migration_date": datetime.now().isoformat(),
            "operation": "remove_qty_column",
            "table": "edge",
            "status": "error",
            "error_message": str(e)
        }
        
        with open("qty_column_removal_error.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
        
    finally:
        if 'conn' in locals():
            await conn.close()
            print("🔌 DB 연결 종료")

if __name__ == "__main__":
    print("🚀 edge 테이블 qty 컬럼 삭제 마이그레이션 시작")
    print("=" * 60)
    
    asyncio.run(remove_qty_column())
