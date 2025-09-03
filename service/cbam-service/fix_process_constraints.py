#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process 테이블 제약조건 수정 스크립트
(process_name, install_id)에 대한 UNIQUE 제약조건 추가
"""

import asyncio
import asyncpg

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def fix_process_constraints():
    """Process 테이블 제약조건 수정"""
    print("🔧 Process 테이블 제약조건 수정 시작...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 데이터베이스 연결 성공!")
        
        # 1. (process_name, install_id)에 대한 UNIQUE 제약조건 추가
        print("\n1️⃣ (process_name, install_id) UNIQUE 제약조건 추가...")
        try:
            await conn.execute("""
                ALTER TABLE process ADD CONSTRAINT uk_process_name_install 
                UNIQUE (process_name, install_id)
            """)
            print("   ✅ (process_name, install_id) UNIQUE 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e) or "duplicate key" in str(e):
                print("   ℹ️ (process_name, install_id) UNIQUE 제약조건이 이미 존재합니다")
            else:
                print(f"   ❌ UNIQUE 제약조건 추가 실패: {e}")
        
        # 2. 제약조건 확인
        print("\n2️⃣ 제약조건 확인...")
        constraints = await conn.fetch("""
            SELECT constraint_name, constraint_type, table_name
            FROM information_schema.table_constraints 
            WHERE table_name = 'process' AND constraint_type = 'UNIQUE'
            ORDER BY constraint_name
        """)
        
        print("   📋 Process 테이블 UNIQUE 제약조건:")
        for constraint in constraints:
            print(f"     - {constraint['constraint_name']}: {constraint['constraint_type']}")
        
        await conn.close()
        print("\n✅ Process 테이블 제약조건 수정 완료!")
        return True
        
    except Exception as e:
        print(f"❌ Process 테이블 제약조건 수정 실패: {e}")
        return False

async def test_process_creation():
    """공정 생성 테스트"""
    print("\n🧪 공정 생성 테스트 시작...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 1. 사업장1 (포항1)에 공정1 생성
        print("   1️⃣ 사업장1 (포항1)에 공정1 생성...")
        process1_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정1', 14, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        print(f"      ✅ 공정1 생성 성공 (ID: {process1_id})")
        
        # 2. 사업장2 (테스트사업장2)에 공정2 생성
        print("   2️⃣ 사업장2 (테스트사업장2)에 공정2 생성...")
        process2_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정2', 15, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        print(f"      ✅ 공정2 생성 성공 (ID: {process2_id})")
        
        # 3. 사업장2 (테스트사업장2)에 공정3 생성
        print("   3️⃣ 사업장2 (테스트사업장2)에 공정3 생성...")
        process3_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정3', 15, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        print(f"      ✅ 공정3 생성 성공 (ID: {process3_id})")
        
        # 4. 생성된 공정 목록 확인
        print("   4️⃣ 생성된 공정 목록 확인...")
        processes = await conn.fetch("""
            SELECT p.id, p.process_name, p.install_id, i.install_name
            FROM process p
            JOIN install i ON p.install_id = i.id
            WHERE p.process_name LIKE '테스트공정%'
            ORDER BY p.install_id, p.process_name
        """)
        
        print("      📊 테스트 공정 목록:")
        for process in processes:
            print(f"        - ID {process['id']}: {process['process_name']} (사업장: {process['install_name']})")
        
        await conn.close()
        print("   ✅ 공정 생성 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"   ❌ 공정 생성 테스트 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🚀 Process 테이블 제약조건 수정 및 테스트 시작")
    print("=" * 80)
    
    # 1. 제약조건 수정
    constraints_ok = await fix_process_constraints()
    
    if constraints_ok:
        # 2. 공정 생성 테스트
        await test_process_creation()
    
    print("\n" + "=" * 80)
    print("🏁 제약조건 수정 및 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
