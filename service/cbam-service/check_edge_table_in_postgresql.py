#!/usr/bin/env python3
"""
PostgreSQL DB에 Edge 테이블이 존재하는지 확인하는 스크립트
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def check_edge_table_in_postgresql():
    """PostgreSQL DB에 Edge 테이블이 존재하는지 확인합니다."""
    
    # DATABASE_URL 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        print("🔗 PostgreSQL DB 연결 중...")
        print(f"📍 연결 주소: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        conn = await asyncpg.connect(database_url)
        print("✅ PostgreSQL DB 연결 성공")
        
        # 1. Edge 테이블 존재 여부 확인
        print("\n🔍 1. Edge 테이블 존재 여부 확인...")
        table_exists_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'edge'
        );
        """
        
        result = await conn.fetchrow(table_exists_query)
        edge_table_exists = result[0]
        
        if edge_table_exists:
            print("✅ Edge 테이블이 PostgreSQL DB에 존재합니다!")
        else:
            print("❌ Edge 테이블이 PostgreSQL DB에 존재하지 않습니다!")
            print("💡 이는 Edge 생성 실패의 원인일 수 있습니다.")
            return
        
        # 2. Edge 테이블 구조 확인
        print("\n🔍 2. Edge 테이블 구조 확인...")
        columns_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'edge' 
        ORDER BY ordinal_position;
        """
        
        columns = await conn.fetch(columns_query)
        print("Edge 테이블 구조:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # 3. Edge 테이블 데이터 개수 확인
        print("\n🔍 3. Edge 테이블 데이터 개수 확인...")
        count_query = "SELECT COUNT(*) FROM edge;"
        count = await conn.fetchrow(count_query)
        print(f"Edge 테이블 데이터 개수: {count[0]}개")
        
        # 4. Edge 테이블 샘플 데이터 확인
        print("\n🔍 4. Edge 테이블 샘플 데이터 확인...")
        if count[0] > 0:
            sample_query = "SELECT * FROM edge LIMIT 3;"
            samples = await conn.fetch(sample_query)
            
            print("샘플 데이터:")
            for i, sample in enumerate(samples, 1):
                print(f"  {i}. {dict(sample)}")
        else:
            print("ℹ️ Edge 테이블에 데이터가 없습니다.")
        
        # 5. Edge 테이블 인덱스 확인
        print("\n🔍 5. Edge 테이블 인덱스 확인...")
        indexes_query = """
        SELECT indexname, indexdef
        FROM pg_indexes 
        WHERE tablename = 'edge';
        """
        
        indexes = await conn.fetch(indexes_query)
        if indexes:
            print("Edge 테이블 인덱스:")
            for idx in indexes:
                print(f"  - {idx['indexname']}: {idx['indexdef']}")
        else:
            print("ℹ️ Edge 테이블에 인덱스가 없습니다.")
        
        # 6. 결과 저장
        check_result = {
            "check_date": datetime.now().isoformat(),
            "database_url": database_url.split('@')[1] if '@' in database_url else database_url,
            "edge_table_exists": edge_table_exists,
            "table_structure": [{"name": col['column_name'], "type": col['data_type'], "nullable": col['is_nullable']} for col in columns],
            "total_records": count[0],
            "sample_data": [dict(sample) for sample in samples] if count[0] > 0 else [],
            "indexes": [{"name": idx['indexname'], "definition": idx['indexdef']} for idx in indexes] if indexes else [],
            "status": "success"
        }
        
        with open("edge_table_check_postgresql.json", "w", encoding="utf-8") as f:
            json.dump(check_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 결과가 edge_table_check_postgresql.json에 저장되었습니다.")
        
        # 7. 문제 해결 방안 제시
        if edge_table_exists:
            print("\n💡 Edge 테이블이 존재하므로 다른 원인을 찾아야 합니다:")
            print("1. Edge 엔티티의 Base 클래스 문제")
            print("2. 데이터베이스 세션 문제")
            print("3. SQLAlchemy 설정 문제")
        else:
            print("\n💡 Edge 테이블이 존재하지 않습니다:")
            print("1. 데이터베이스 마이그레이션 필요")
            print("2. Edge 테이블 생성 스크립트 실행 필요")
        
        print("🎯 PostgreSQL DB Edge 테이블 확인 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        # 오류 결과 저장
        error_result = {
            "check_date": datetime.now().isoformat(),
            "database_url": database_url,
            "status": "error",
            "error_message": str(e)
        }
        
        with open("edge_table_check_postgresql_error.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
        
    finally:
        if 'conn' in locals():
            await conn.close()
            print("🔌 PostgreSQL DB 연결 종료")

if __name__ == "__main__":
    print("🚀 PostgreSQL DB Edge 테이블 확인 시작")
    print("=" * 60)
    
    asyncio.run(check_edge_table_in_postgresql())
