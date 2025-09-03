#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL 데이터베이스 구조 확인 스크립트
크로스 사업장 공정 연결을 위한 테이블 구조 검증
"""

import asyncio
import asyncpg
import os
from datetime import datetime

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def check_database_structure():
    """데이터베이스 구조 확인"""
    print("🔍 Railway PostgreSQL 데이터베이스 구조 확인 시작...")
    print(f"📡 연결 URL: {DATABASE_URL.split('@')[1]}")  # 비밀번호 제외하고 표시
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ 데이터베이스 연결 성공!")
        
        # 1. 테이블 목록 확인
        print("\n📋 테이블 목록:")
        tables = await conn.fetch("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        for table in tables:
            print(f"   - {table['table_name']} ({table['table_type']})")
        
        # 2. install 테이블 구조 확인
        print("\n🏭 Install 테이블 구조:")
        try:
            install_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'install' 
                ORDER BY ordinal_position
            """)
            
            for col in install_columns:
                print(f"   - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']}, 기본값: {col['column_default']})")
                
            # install 데이터 확인
            install_count = await conn.fetchval("SELECT COUNT(*) FROM install")
            print(f"   📊 총 {install_count}개 사업장")
            
            if install_count > 0:
                installs = await conn.fetch("SELECT id, install_name FROM install LIMIT 5")
                for install in installs:
                    print(f"     - ID {install['id']}: {install['install_name']}")
                    
        except Exception as e:
            print(f"   ❌ Install 테이블 확인 실패: {e}")
        
        # 3. product 테이블 구조 확인
        print("\n📦 Product 테이블 구조:")
        try:
            product_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'product' 
                ORDER BY ordinal_position
            """)
            
            for col in product_columns:
                print(f"   - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']}, 기본값: {col['column_default']})")
                
            # product 데이터 확인
            product_count = await conn.fetchval("SELECT COUNT(*) FROM product")
            print(f"   📊 총 {product_count}개 제품")
            
            if product_count > 0:
                products = await conn.fetch("""
                    SELECT p.id, p.product_name, p.install_id, i.install_name 
                    FROM product p 
                    LEFT JOIN install i ON p.install_id = i.id 
                    LIMIT 5
                """)
                for product in products:
                    print(f"     - ID {product['id']}: {product['product_name']} (사업장: {product['install_name'] or 'Unknown'})")
                    
        except Exception as e:
            print(f"   ❌ Product 테이블 확인 실패: {e}")
        
        # 4. process 테이블 구조 확인
        print("\n⚙️ Process 테이블 구조:")
        try:
            process_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'process' 
                ORDER BY ordinal_position
            """)
            
            for col in process_columns:
                print(f"   - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']}, 기본값: {col['column_default']})")
                
            # process 데이터 확인
            process_count = await conn.fetchval("SELECT COUNT(*) FROM process")
            print(f"   📊 총 {process_count}개 공정")
            
            if process_count > 0:
                processes = await conn.fetch("""
                    SELECT p.id, p.process_name, p.install_id, i.install_name 
                    FROM process p 
                    LEFT JOIN install i ON p.install_id = i.id 
                    LIMIT 5
                """)
                for process in processes:
                    print(f"     - ID {process['id']}: {process['process_name']} (사업장: {process['install_name'] or 'Unknown'})")
                    
        except Exception as e:
            print(f"   ❌ Process 테이블 확인 실패: {e}")
        
        # 5. product_process 테이블 구조 확인
        print("\n🔗 Product-Process 관계 테이블 구조:")
        try:
            pp_columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'product_process' 
                ORDER BY ordinal_position
            """)
            
            for col in pp_columns:
                print(f"   - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']}, 기본값: {col['column_default']})")
                
            # product_process 데이터 확인
            pp_count = await conn.fetchval("SELECT COUNT(*) FROM product_process")
            print(f"   📊 총 {pp_count}개 제품-공정 연결")
            
            if pp_count > 0:
                pp_relations = await conn.fetch("""
                    SELECT pp.product_id, p.product_name, pp.process_id, pr.process_name,
                           pi.install_name as product_install, pri.install_name as process_install
                    FROM product_process pp
                    JOIN product p ON pp.product_id = p.id
                    JOIN process pr ON pp.process_id = pr.id
                    LEFT JOIN install pi ON p.install_id = pi.id
                    LEFT JOIN install pri ON pr.install_id = pri.id
                    LIMIT 5
                """)
                for relation in pp_relations:
                    print(f"     - 제품 '{relation['product_name']}' ({relation['product_install']}) ↔ 공정 '{relation['process_name']}' ({relation['process_install']})")
                    
        except Exception as e:
            print(f"   ❌ Product-Process 테이블 확인 실패: {e}")
        
        # 6. 외래키 제약조건 확인
        print("\n🔒 외래키 제약조건:")
        try:
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
            
            for fk in foreign_keys:
                print(f"   - {fk['table_name']}.{fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']}")
                
        except Exception as e:
            print(f"   ❌ 외래키 제약조건 확인 실패: {e}")
        
        # 7. 크로스 사업장 공정 연결 테스트 데이터 생성
        print("\n🧪 크로스 사업장 공정 연결 테스트:")
        
        # 사업장이 2개 이상 있는지 확인
        install_count = await conn.fetchval("SELECT COUNT(*) FROM install")
        if install_count >= 2:
            print("   ✅ 사업장이 2개 이상 있어서 크로스 사업장 테스트 가능")
            
            # 사업장별 공정 분포 확인
            install_processes = await conn.fetch("""
                SELECT i.install_name, COUNT(p.id) as process_count
                FROM install i
                LEFT JOIN process p ON i.id = p.install_id
                GROUP BY i.id, i.install_name
                ORDER BY i.id
            """)
            
            print("   📊 사업장별 공정 분포:")
            for ip in install_processes:
                print(f"     - {ip['install_name']}: {ip['process_count']}개 공정")
                
        else:
            print("   ⚠️ 사업장이 1개만 있어서 크로스 사업장 테스트 불가")
        
        await conn.close()
        print("\n✅ 데이터베이스 구조 확인 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 또는 확인 실패: {e}")
        return False
    
    return True

async def test_cross_install_process_connection():
    """크로스 사업장 공정 연결 기능 테스트"""
    print("\n🧪 크로스 사업장 공정 연결 기능 테스트 시작...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 1. 테스트용 사업장 생성 (이미 있다면 건너뛰기)
        print("   1️⃣ 테스트용 사업장 생성/확인...")
        
        # 사업장1: 제품1 생산, 공정1만 존재
        install1_id = await conn.fetchval("""
            INSERT INTO install (install_name, created_at, updated_at) 
            VALUES ('테스트사업장1', NOW(), NOW()) 
            ON CONFLICT (install_name) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        # 사업장2: 공정2, 공정3 존재
        install2_id = await conn.fetchval("""
            INSERT INTO install (install_name, created_at, updated_at) 
            VALUES ('테스트사업장2', NOW(), NOW()) 
            ON CONFLICT (install_name) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """)
        
        print(f"      ✅ 사업장1 ID: {install1_id}, 사업장2 ID: {install2_id}")
        
        # 2. 테스트용 제품 생성
        print("   2️⃣ 테스트용 제품 생성...")
        product1_id = await conn.fetchval("""
            INSERT INTO product (install_id, product_name, product_category, prostart_period, proend_period, product_amount, product_sell, product_eusell, created_at, updated_at)
            VALUES ($1, '테스트제품1', '복합제품', '2025-01-01', '2025-12-31', 100, 1000, 800, NOW(), NOW())
            ON CONFLICT (product_name) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """, install1_id)
        
        print(f"      ✅ 제품1 ID: {product1_id}")
        
        # 3. 테스트용 공정 생성
        print("   3️⃣ 테스트용 공정 생성...")
        
        # 사업장1: 공정1
        process1_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정1', $1, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """, install1_id)
        
        # 사업장2: 공정2
        process2_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정2', $1, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """, install2_id)
        
        # 사업장2: 공정3
        process3_id = await conn.fetchval("""
            INSERT INTO process (process_name, install_id, created_at, updated_at)
            VALUES ('테스트공정3', $1, NOW(), NOW())
            ON CONFLICT (process_name, install_id) DO UPDATE SET updated_at = NOW()
            RETURNING id
        """, install2_id)
        
        print(f"      ✅ 공정1 ID: {process1_id} (사업장1), 공정2 ID: {process2_id} (사업장2), 공정3 ID: {process3_id} (사업장2)")
        
        # 4. 크로스 사업장 공정 연결 테스트
        print("   4️⃣ 크로스 사업장 공정 연결 테스트...")
        
        # 제품1을 사업장1의 공정1 + 사업장2의 공정2,3으로 연결
        await conn.execute("""
            INSERT INTO product_process (product_id, process_id, created_at, updated_at)
            VALUES ($1, $2, NOW(), NOW()), ($1, $3, NOW(), NOW()), ($1, $4, NOW(), NOW())
            ON CONFLICT (product_id, process_id) DO NOTHING
        """, product1_id, process1_id, process2_id, process3_id)
        
        print("      ✅ 크로스 사업장 공정 연결 성공!")
        
        # 5. 연결 결과 확인
        print("   5️⃣ 연결 결과 확인...")
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
            WHERE p.id = $1
            ORDER BY pr.install_id, pr.process_name
        """, product1_id)
        
        print("      📊 제품1의 크로스 사업장 공정 연결:")
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
    print("🚀 Railway PostgreSQL 데이터베이스 구조 및 기능 검증 시작")
    print("=" * 80)
    
    # 1. 데이터베이스 구조 확인
    structure_ok = await check_database_structure()
    
    if structure_ok:
        # 2. 크로스 사업장 공정 연결 기능 테스트
        await test_cross_install_process_connection()
    
    print("\n" + "=" * 80)
    print("🏁 검증 완료!")

if __name__ == "__main__":
    asyncio.run(main())
