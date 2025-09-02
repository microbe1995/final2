#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗑️ dummy_data 테이블 삭제 스크립트
"""

import asyncio
import asyncpg
import os

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def delete_dummy_data_table():
    """dummy_data 테이블 삭제"""
    print("🗑️ dummy_data 테이블 삭제 시작...")
    
    try:
        # PostgreSQL 연결
        print("🔗 Railway DB 연결 중...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # dummy_data 테이블 존재 여부 확인
        print("\n🔍 dummy_data 테이블 확인...")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dummy_data'
            );
        """)
        
        if table_exists:
            print("✅ dummy_data 테이블이 존재합니다.")
            
            # 테이블 구조 확인
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'dummy_data'
                ORDER BY ordinal_position;
            """)
            
            print("\n📋 dummy_data 테이블 구조:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} "
                      f"({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # 데이터 개수 확인
            count = await conn.fetchval("SELECT COUNT(*) FROM dummy_data")
            print(f"\n📊 dummy_data 테이블 데이터 개수: {count}")
            
            # 사용자 확인
            confirm = input(f"\n⚠️ 정말로 dummy_data 테이블을 삭제하시겠습니까? (y/N): ")
            
            if confirm.lower() == 'y':
                print("\n🗑️ dummy_data 테이블 삭제 중...")
                await conn.execute("DROP TABLE dummy_data CASCADE")
                print("✅ dummy_data 테이블 삭제 완료!")
                
                # 삭제 확인
                table_exists_after = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'dummy_data'
                    );
                """)
                
                if not table_exists_after:
                    print("✅ 테이블 삭제 확인 완료!")
                else:
                    print("❌ 테이블 삭제 실패!")
            else:
                print("❌ 테이블 삭제가 취소되었습니다.")
        else:
            print("❌ dummy_data 테이블이 존재하지 않습니다.")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(delete_dummy_data_table())
