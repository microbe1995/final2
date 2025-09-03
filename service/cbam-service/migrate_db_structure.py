#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL 데이터베이스 마이그레이션 스크립트
크로스 사업장 공정 연결을 위한 테이블 구조 업데이트
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def migrate_database_structure():
    """데이터베이스 구조 마이그레이션"""
    print("🔧 Railway PostgreSQL 데이터베이스 마이그레이션 시작...")
    print(f"📡 연결 URL: {DATABASE_URL.split('@')[1]}")  # 비밀번호 제외하고 표시
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 데이터베이스 연결 성공!")
        
        # 1. Install 테이블에 UNIQUE 제약조건 추가
        print("\n1️⃣ Install 테이블 UNIQUE 제약조건 추가...")
        try:
            await conn.execute("""
                ALTER TABLE install ADD CONSTRAINT uk_install_name UNIQUE (install_name)
            """)
            print("   ✅ install_name에 UNIQUE 제약조건 추가 완료")
        except Exception as e:
            if "already exists" in str(e) or "duplicate key" in str(e):
                print("   ℹ️ install_name UNIQUE 제약조건이 이미 존재합니다")
            else:
                print(f"   ❌ install_name UNIQUE 제약조건 추가 실패: {e}")
        
        # 2. Process 테이블에 install_id 컬럼 추가
        print("\n2️⃣ Process 테이블에 install_id 컬럼 추가...")
        try:
            # install_id 컬럼이 존재하는지 확인
            columns = await conn.fetch("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'process' AND column_name = 'install_id'
            """)
            
            if not columns:
                # install_id 컬럼 추가
                await conn.execute("""
                    ALTER TABLE process ADD COLUMN install_id INTEGER NOT NULL DEFAULT 1
                """)
                print("   ✅ install_id 컬럼 추가 완료 (기본값: 1)")
                
                # 외래키 제약조건 추가
                await conn.execute("""
                    ALTER TABLE process ADD CONSTRAINT fk_process_install 
                    FOREIGN KEY (install_id) REFERENCES install(id) ON DELETE CASCADE
                """)
                print("   ✅ install_id 외래키 제약조건 추가 완료")
            else:
                print("   ℹ️ install_id 컬럼이 이미 존재합니다")
                
        except Exception as e:
            print(f"   ❌ Process 테이블 마이그레이션 실패: {e}")
        
        # 3. 테스트용 사업장 추가
        print("\n3️⃣ 테스트용 사업장 추가...")
        try:
            # 사업장2 생성 (이미 있다면 건너뛰기)
            install2_id = await conn.fetchval("""
                INSERT INTO install (install_name, reporting_year, created_at, updated_at)
                VALUES ('테스트사업장2', EXTRACT(year FROM now()), NOW(), NOW())
                ON CONFLICT (install_name) DO UPDATE SET updated_at = NOW()
                RETURNING id
            """)
            print(f"   ✅ 테스트사업장2 생성 완료 (ID: {install2_id})")
            
        except Exception as e:
            print(f"   ❌ 테스트용 사업장 추가 실패: {e}")
        
        # 4. 마이그레이션 결과 확인
        print("\n4️⃣ 마이그레이션 결과 확인...")
        
        # Process 테이블 구조 재확인
        process_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process' 
            ORDER BY ordinal_position
        """)
        
        print("   📋 Process 테이블 최종 구조:")
        for col in process_columns:
            print(f"     - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']}, 기본값: {col['column_default']})")
        
        # 외래키 제약조건 확인
        foreign_keys = await conn.fetch("""
            SELECT 
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            ORDER BY tc.table_name, kcu.column_name
        """)
        
        print("   🔒 외래키 제약조건:")
        for fk in foreign_keys:
            print(f"     - {fk['table_name']}.{fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        # 사업장 목록 확인
        installs = await conn.fetch("SELECT id, install_name FROM install ORDER BY id")
        print("   🏭 사업장 목록:")
        for install in installs:
            print(f"     - ID {install['id']}: {install['install_name']}")
        
        await conn.close()
        print("\n✅ 데이터베이스 마이그레이션 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 마이그레이션 실패: {e}")
        return False

async def test_cross_install_process_connection():
    """크로스 사업장 공정 연결 기능 테스트"""
    print("\n🧪 크로스 사업장 공정 연결 기능 테스트 시작...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 1. 테스트용 공정 생성
        print("   1️⃣ 테스트용 공정 생성...")
        
        # 사업장1 (포항1)에 공정1 생성
        process1_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정1', 14, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        # 사업장2 (테스트사업장2)에 공정2, 공정3 생성
        process2_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정2', (SELECT id FROM install WHERE install_name = '테스트사업장2'), NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        process3_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정3', (SELECT id FROM install WHERE install_name = '테스트사업장2'), NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        print(f"      ✅ 공정1 ID: {process1_id} (사업장1: 포항1)")
        print(f"      ✅ 공정2 ID: {process2_id} (사업장2: 테스트사업장2)")
        print(f"      ✅ 공정3 ID: {process3_id} (사업장2: 테스트사업장2)")
        
        # 2. 크로스 사업장 공정 연결 테스트
        print("   2️⃣ 크로스 사업장 공정 연결 테스트...")
        
        # 제품1 (블룸)을 사업장1의 공정1 + 사업장2의 공정2,3으로 연결
        await conn.execute("""
            INSERT INTO product_process (product_id, process_id, created_at, updated_at)
            VALUES (14, $1, NOW(), NOW()), (14, $2, NOW(), NOW()), (14, $3, NOW(), NOW())
            ON CONFLICT (product_id, process_id) DO NOTHING
        """, process1_id, process2_id, process3_id)
        
        print("      ✅ 크로스 사업장 공정 연결 성공!")
        
        # 3. 연결 결과 확인
        print("   3️⃣ 연결 결과 확인...")
        connections = await conn.fetch("""
            SELECT 
                p.product_name,
                pr.process_name,
                i.install_name,
                pp.created_at
            FROM product_process pp
            JOIN product p ON pp.product_id = p.id
            JOIN process pr ON pp.process_id = pr.id
            JOIN install i ON pr.install_id = i.id
            WHERE p.id = 14
            ORDER BY pr.install_id, pr.process_name
        """)
        
        print("      📊 제품 '블룸'의 크로스 사업장 공정 연결:")
        for conn_info in connections:
            print(f"        - {conn_info['product_name']} ↔ {conn_info['process_name']} ({conn_info['install_name']})")
        
        await conn.close()
        print("   ✅ 크로스 사업장 공정 연결 기능 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"   ❌ 크로스 사업장 공정 연결 기능 테스트 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🚀 Railway PostgreSQL 데이터베이스 마이그레이션 및 테스트 시작")
    print("=" * 80)
    
    # 1. 데이터베이스 구조 마이그레이션
    migration_ok = await migrate_database_structure()
    
    if migration_ok:
        # 2. 크로스 사업장 공정 연결 기능 테스트
        await test_cross_install_process_connection()
    
    print("\n" + "=" * 80)
    print("🏁 마이그레이션 및 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
