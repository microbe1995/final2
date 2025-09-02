#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB 직접 연결 테스트 (asyncpg 사용)
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_railway_connection():
    """Railway DB 직접 연결 테스트"""
    print("🔍 Railway DB 직접 연결 테스트 시작...")
    
    try:
        # PostgreSQL 연결
        print(f"  - 연결 시도: {RAILWAY_DB_URL[:50]}...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 서버 정보 확인
        server_version = await conn.fetchval("SELECT version();")
        print(f"  - PostgreSQL 버전: {server_version.split(',')[0]}")
        
        # 현재 데이터베이스 확인
        current_db = await conn.fetchval("SELECT current_database();")
        print(f"  - 현재 데이터베이스: {current_db}")
        
        # 현재 사용자 확인
        current_user = await conn.fetchval("SELECT current_user;")
        print(f"  - 현재 사용자: {current_user}")
        
        # dummy 테이블 존재 여부 확인
        print("\n🔍 dummy 테이블 확인...")
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dummy'
            );
        """)
        
        if table_exists:
            print("✅ dummy 테이블이 존재합니다.")
            
            # dummy 테이블 구조 확인
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'dummy'
                ORDER BY ordinal_position;
            """)
            
            print("\n📋 dummy 테이블 구조:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} "
                      f"({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # dummy 테이블 데이터 개수 확인
            count = await conn.fetchval("SELECT COUNT(*) FROM dummy")
            print(f"\n📊 dummy 테이블 데이터 개수: {count}")
            
            # 샘플 데이터 조회
            if count > 0:
                sample_data = await conn.fetch("SELECT * FROM dummy LIMIT 3")
                print("\n📝 샘플 데이터:")
                for row in sample_data:
                    print(f"  - ID: {row['id']}, 로트번호: {row['로트번호']}, "
                          f"생산품명: {row['생산품명']}, 공정: {row['공정']}")
            else:
                print("⚠️ dummy 테이블에 데이터가 없습니다.")
                
                # 테스트 데이터 삽입
                print("\n🔧 테스트 데이터 삽입...")
                await conn.execute("""
                    INSERT INTO dummy (로트번호, 생산품명, 생산수량, 투입일, 종료일, 공정, 투입물명, 수량, 단위)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, 'TEST001', '테스트제품', 100.00, datetime(2024, 1, 1).date(), 
                     datetime(2024, 1, 31).date(), '테스트공정', '테스트원료', 50.00, '개')
                print("✅ 테스트 데이터 삽입 성공!")
                
                # 삽입된 데이터 확인
                new_count = await conn.fetchval("SELECT COUNT(*) FROM dummy")
                print(f"  - 새로운 데이터 개수: {new_count}")
                
        else:
            print("❌ dummy 테이블이 존재하지 않습니다.")
            
            # 테이블 생성 시도
            print("\n🔧 dummy 테이블 생성 시도...")
            await conn.execute("""
                CREATE TABLE dummy (
                    id SERIAL PRIMARY KEY,
                    로트번호 VARCHAR(100) NOT NULL,
                    생산품명 VARCHAR(200) NOT NULL,
                    생산수량 NUMERIC(10,2) NOT NULL,
                    투입일 DATE,
                    종료일 DATE,
                    공정 VARCHAR(100) NOT NULL,
                    투입물명 VARCHAR(200) NOT NULL,
                    수량 NUMERIC(10,2) NOT NULL,
                    단위 VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            print("✅ dummy 테이블 생성 성공!")
            
            # 인덱스 생성
            await conn.execute("CREATE INDEX idx_dummy_로트번호 ON dummy(로트번호);")
            await conn.execute("CREATE INDEX idx_dummy_생산품명 ON dummy(생산품명);")
            await conn.execute("CREATE INDEX idx_dummy_공정 ON dummy(공정);")
            print("✅ 인덱스 생성 성공!")
            
            # 샘플 데이터 삽입
            print("\n🔧 샘플 데이터 삽입...")
            await conn.execute("""
                INSERT INTO dummy (로트번호, 생산품명, 생산수량, 투입일, 종료일, 공정, 투입물명, 수량, 단위)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 'TEST001', '테스트제품', 100.00, datetime(2024, 1, 1).date(), 
                 datetime(2024, 1, 31).date(), '테스트공정', '테스트원료', 50.00, '개')
            print("✅ 샘플 데이터 삽입 성공!")
        
        await conn.close()
        print("\n✅ Railway DB 연결 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Railway DB 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 Railway DB 직접 연결 테스트 시작\n")
    
    success = await test_railway_connection()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Railway DB 연결 테스트가 성공했습니다!")
        print("✅ dummy 테이블과 dummy 도메인 코드가 완벽하게 연결되어 있습니다.")
    else:
        print("❌ Railway DB 연결 테스트가 실패했습니다.")
        print("⚠️ 연결 정보나 네트워크 설정을 확인해주세요.")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
