#!/usr/bin/env python3
"""
Railway DB 연결 상태와 테이블 존재 여부를 확인하는 스크립트
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime

async def check_railway_db():
    """Railway DB 연결 상태와 테이블을 확인합니다."""
    
    # DATABASE_URL 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        print("🔗 Railway DB 연결 중...")
        print(f"📍 연결 주소: {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        conn = await asyncpg.connect(database_url)
        print("✅ DB 연결 성공")
        
        # 1. 현재 데이터베이스 정보 확인
        print("\n📋 데이터베이스 정보 확인...")
        db_info = await conn.fetchrow("SELECT current_database(), current_user, version()")
        print(f"  - 현재 DB: {db_info[0]}")
        print(f"  - 현재 사용자: {db_info[1]}")
        print(f"  - PostgreSQL 버전: {db_info[2]}")
        
        # 2. 테이블 목록 확인
        print("\n📋 테이블 목록 확인...")
        tables_query = """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        
        tables = await conn.fetch(tables_query)
        print(f"총 {len(tables)}개의 테이블이 있습니다:")
        for table in tables:
            print(f"  - {table['table_name']} ({table['table_type']})")
        
        # 3. process_chain_link 테이블 상세 확인
        print("\n🔍 process_chain_link 테이블 상세 확인...")
        if any(table['table_name'] == 'process_chain_link' for table in tables):
            print("✅ process_chain_link 테이블이 존재합니다.")
            
            # 테이블 구조 확인
            columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process_chain_link' 
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(columns_query)
            print("테이블 구조:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # 데이터 개수 확인
            count_query = "SELECT COUNT(*) FROM process_chain_link;"
            count = await conn.fetchrow(count_query)
            print(f"데이터 개수: {count[0]}개")
            
        else:
            print("❌ process_chain_link 테이블이 존재하지 않습니다.")
        
        # 4. edge 테이블 상세 확인
        print("\n🔍 edge 테이블 상세 확인...")
        if any(table['table_name'] == 'edge' for table in tables):
            print("✅ edge 테이블이 존재합니다.")
            
            # 테이블 구조 확인
            columns_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'edge' 
            ORDER BY ordinal_position;
            """
            
            columns = await conn.fetch(columns_query)
            print("테이블 구조:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # 데이터 개수 확인
            count_query = "SELECT COUNT(*) FROM edge;"
            count = await conn.fetchrow(count_query)
            print(f"데이터 개수: {count[0]}개")
            
        else:
            print("❌ edge 테이블이 존재하지 않습니다.")
        
        # 5. 결과 저장
        check_result = {
            "check_date": datetime.now().isoformat(),
            "database_url": database_url.split('@')[1] if '@' in database_url else database_url,
            "connection_status": "success",
            "database_info": {
                "current_database": db_info[0],
                "current_user": db_info[1],
                "postgresql_version": db_info[2]
            },
            "tables": [{"name": table['table_name'], "type": table['table_type']} for table in tables],
            "process_chain_link_exists": any(table['table_name'] == 'process_chain_link' for table in tables),
            "edge_exists": any(table['table_name'] == 'edge' for table in tables)
        }
        
        with open("railway_db_connection_check.json", "w", encoding="utf-8") as f:
            json.dump(check_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 결과가 railway_db_connection_check.json에 저장되었습니다.")
        print("🎯 Railway DB 연결 및 테이블 확인 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
        # 오류 결과 저장
        error_result = {
            "check_date": datetime.now().isoformat(),
            "database_url": database_url,
            "connection_status": "error",
            "error_message": str(e)
        }
        
        with open("railway_db_connection_error.json", "w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2, ensure_ascii=False)
        
    finally:
        if 'conn' in locals():
            await conn.close()
            print("🔌 DB 연결 종료")

if __name__ == "__main__":
    print("🚀 Railway DB 연결 및 테이블 확인 시작")
    print("=" * 60)
    
    asyncio.run(check_railway_db())
