#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor

def check_expanded_db_structure():
    """확장된 DB 구조 확인"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔍 확장된 DB 구조 확인 중...")
        
        # 1. 새로 생성된 테이블들 확인
        new_tables = ['emission_factors', 'emission_attribution', 'product_emissions']
        
        for table_name in new_tables:
            print(f"\n📋 {table_name} 테이블 구조:")
            print("-" * 50)
            
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            if columns:
                print(f"{'컬럼명':<25} {'데이터타입':<20} {'NULL허용':<10} {'기본값'}")
                print("-" * 70)
                for col in columns:
                    default = col[3] if col[3] else 'NULL'
                    print(f"{col[0]:<25} {col[1]:<20} {col[2]:<10} {default}")
            else:
                print(f"❌ {table_name} 테이블이 존재하지 않습니다.")
        
        # 2. 확장된 process_input 테이블 확인
        print(f"\n📋 확장된 process_input 테이블 구조:")
        print("-" * 50)
        
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process_input'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        if columns:
            print(f"{'컬럼명':<25} {'데이터타입':<20} {'NULL허용':<10} {'기본값'}")
            print("-" * 70)
            for col in columns:
                default = col[3] if col[3] else 'NULL'
                print(f"{col[0]:<25} {col[1]:<20} {col[2]:<10} {default}")
        
        # 3. 배출계수 데이터 확인
        print(f"\n📊 배출계수 데이터 확인:")
        print("-" * 50)
        
        cur.execute("""
            SELECT factor_type, material_name, emission_factor, unit, source
            FROM emission_factors
            ORDER BY factor_type, material_name;
        """)
        
        factors = cur.fetchall()
        if factors:
            print(f"{'타입':<12} {'물질명':<15} {'배출계수':<10} {'단위':<15} {'출처'}")
            print("-" * 70)
            for factor in factors:
                print(f"{factor[0]:<12} {factor[1]:<15} {factor[2]:<10} {factor[3]:<15} {factor[4]}")
        else:
            print("❌ 배출계수 데이터가 없습니다.")
        
        # 4. 전체 테이블 관계 확인
        print(f"\n🔗 전체 테이블 관계:")
        print("-" * 50)
        
        tables = [
            'install',
            'product', 
            'process',
            'process_input',
            'edge',
            'emission_factors',
            'emission_attribution',
            'product_emissions'
        ]
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"✅ {table}: {count}개 레코드")
        
        print(f"\n🎉 DB 스키마 확장 완료!")
        print("📋 다음 단계:")
        print("1. Backend 엔티티 업데이트")
        print("2. API 엔드포인트 확장")
        print("3. 배출량 계산 로직 구현")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_expanded_db_structure()
