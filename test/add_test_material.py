#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Material Master 테이블에 테스트 데이터 추가
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def add_test_material():
    """테스트용 원료 데이터 추가"""
    
    # Railway DB 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    print("🚀 테스트 원료 데이터 추가 시작...")
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 1. material_master 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'material_master'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ material_master 테이블이 존재하지 않습니다.")
            return
        
        print("✅ material_master 테이블 확인 완료")
        
        # 2. 테스트 데이터 추가
        test_materials = [
            ("직접", "Direct", 0.85, 2.5),  # 직접 - 탄소함량 0.85, 배출계수 2.5
            ("간접", "Indirect", 0.75, 2.0),  # 간접 - 탄소함량 0.75, 배출계수 2.0
            ("원료", "Raw Material", 0.80, 2.2),  # 원료 - 탄소함량 0.80, 배출계수 2.2
        ]
        
        for mat_name, mat_engname, carbon_content, mat_factor in test_materials:
            try:
                # 중복 확인
                cursor.execute("SELECT id FROM material_master WHERE mat_name = %s", (mat_name,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"   ⚠️ {mat_name} 이미 존재함 (ID: {existing[0]})")
                    continue
                
                # 새 데이터 삽입
                insert_sql = """
                INSERT INTO material_master (mat_name, mat_engname, carbon_content, mat_factor)
                VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (mat_name, mat_engname, carbon_content, mat_factor))
                print(f"   ✅ {mat_name} 추가 완료 - 배출계수: {mat_factor}")
                
            except Exception as e:
                print(f"   ❌ {mat_name} 추가 실패: {e}")
                continue
        
        conn.commit()
        print("✅ 테스트 데이터 추가 완료")
        
        # 3. 추가된 데이터 확인
        print(f"\n📋 추가된 데이터 확인")
        cursor.execute("""
            SELECT mat_name, mat_engname, carbon_content, mat_factor 
            FROM material_master 
            WHERE mat_name IN ('직접', '간접', '원료')
            ORDER BY mat_name
        """)
        
        results = cursor.fetchall()
        for row in results:
            print(f"   📝 {row[0]} ({row[1]}) - 탄소함량: {row[2]}, 배출계수: {row[3]}")
        
        # 4. 전체 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM material_master")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 총 원료 수: {total_count}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()
            print("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    add_test_material()
