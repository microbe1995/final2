#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
크로스 사업장 공정 연결 완전 테스트 스크립트
"""

import asyncio
import asyncpg

# Railway PostgreSQL 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_cross_install_process_connection():
    """크로스 사업장 공정 연결 완전 테스트"""
    print("🧪 크로스 사업장 공정 연결 완전 테스트 시작...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # 1. 현재 상태 확인
        print("\n1️⃣ 현재 상태 확인...")
        
        # 사업장 목록
        installs = await conn.fetch("SELECT id, install_name FROM install ORDER BY id")
        print("   🏭 사업장 목록:")
        for install in installs:
            print(f"     - ID {install['id']}: {install['install_name']}")
        
        # 공정 목록
        processes = await conn.fetch("""
            SELECT p.id, p.process_name, p.install_id, i.install_name
            FROM process p
            JOIN install i ON p.install_id = i.id
            WHERE p.process_name LIKE '테스트공정%'
            ORDER BY p.install_id, p.process_name
        """)
        print("   ⚙️ 테스트 공정 목록:")
        for process in processes:
            print(f"     - ID {process['id']}: {process['process_name']} (사업장: {process['install_name']})")
        
        # 제품 목록
        products = await conn.fetch("SELECT id, product_name, install_id FROM product ORDER BY id")
        print("   📦 제품 목록:")
        for product in products:
            print(f"     - ID {product['id']}: {product['product_name']} (사업장 ID: {product['install_id']})")
        
        # 2. 크로스 사업장 공정 연결 생성
        print("\n2️⃣ 크로스 사업장 공정 연결 생성...")
        
        # 제품1 (블룸)을 사업장1의 공정1 + 사업장2의 공정2,3으로 연결
        await conn.execute("""
            INSERT INTO product_process (product_id, process_id, created_at, updated_at)
            VALUES (14, 182, NOW(), NOW()), (14, 183, NOW(), NOW()), (14, 184, NOW(), NOW())
            ON CONFLICT (product_id, process_id) DO NOTHING
        """)
        
        print("      ✅ 크로스 사업장 공정 연결 생성 완료!")
        
        # 3. 연결 결과 확인
        print("\n3️⃣ 연결 결과 확인...")
        
        # 제품별 공정 연결 확인
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
        
        # 4. 사업장별 공정 분포 확인
        print("\n4️⃣ 사업장별 공정 분포 확인...")
        
        install_processes = await conn.fetch("""
            SELECT 
                i.install_name,
                COUNT(p.id) as process_count,
                STRING_AGG(p.process_name, ', ' ORDER BY p.process_name) as process_names
            FROM install i
            LEFT JOIN process p ON i.id = p.install_id
            WHERE p.process_name LIKE '테스트공정%'
            GROUP BY i.id, i.install_name
            ORDER BY i.id
        """)
        
        print("      📊 사업장별 공정 분포:")
        for ip in install_processes:
            print(f"        - {ip['install_name']}: {ip['process_count']}개 공정 ({ip['process_names']})")
        
        # 5. 크로스 사업장 연결 요약
        print("\n5️⃣ 크로스 사업장 연결 요약...")
        
        cross_install_summary = await conn.fetch("""
            SELECT 
                p.product_name,
                COUNT(DISTINCT pr.install_id) as install_count,
                STRING_AGG(DISTINCT i.install_name, ' + ' ORDER BY i.install_name) as install_names,
                COUNT(pp.process_id) as process_count
            FROM product_process pp
            JOIN product p ON pp.product_id = p.id
            JOIN process pr ON pp.process_id = pr.id
            JOIN install i ON pr.install_id = i.id
            WHERE p.id = 14
            GROUP BY p.id, p.product_name
        """)
        
        for summary in cross_install_summary:
            print(f"      🎯 {summary['product_name']}: {summary['install_count']}개 사업장 ({summary['install_names']})에서 {summary['process_count']}개 공정 사용")
        
        await conn.close()
        print("\n   ✅ 크로스 사업장 공정 연결 완전 테스트 성공!")
        return True
        
    except Exception as e:
        print(f"   ❌ 크로스 사업장 공정 연결 테스트 실패: {e}")
        return False

async def main():
    """메인 함수"""
    print("🚀 크로스 사업장 공정 연결 완전 테스트 시작")
    print("=" * 80)
    
    await test_cross_install_process_connection()
    
    print("\n" + "=" * 80)
    print("🏁 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main())
