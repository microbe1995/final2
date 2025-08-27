#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor

def create_emission_factors_table():
    """배출계수 테이블 생성"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔧 배출계수 테이블 생성 중...")
        
        # 1. 배출계수 타입 ENUM 생성
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE factor_type_enum AS ENUM ('fuel', 'electricity', 'process', 'precursor');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # 2. 배출계수 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS emission_factors (
                id SERIAL PRIMARY KEY,
                factor_type factor_type_enum NOT NULL,
                material_name TEXT NOT NULL,
                emission_factor DECIMAL(10,6) NOT NULL,
                unit TEXT NOT NULL,
                source TEXT,
                valid_from DATE DEFAULT CURRENT_DATE,
                valid_to DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. 인덱스 생성
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_type ON emission_factors(factor_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_material ON emission_factors(material_name);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_factors_validity ON emission_factors(valid_from, valid_to);")
        
        # 4. 기본 배출계수 데이터 삽입
        print("📊 기본 배출계수 데이터 삽입 중...")
        
        # 연료 배출계수 (기본값)
        fuel_factors = [
            ('fuel', 'LNG', 2.162, 'tCO2/1000m3', '기본값'),
            ('fuel', '경유', 2.639, 'tCO2/kL', '기본값'),
            ('fuel', '중유', 3.169, 'tCO2/kL', '기본값'),
            ('fuel', '석탄', 2.4, 'tCO2/ton', '기본값'),
            ('fuel', '천연가스', 2.162, 'tCO2/1000m3', '기본값'),
        ]
        
        # 전력 배출계수 (한국 전력거래소 기준)
        electricity_factors = [
            ('electricity', '한국전력', 0.415, 'tCO2/MWh', '한국전력거래소'),
        ]
        
        # 공정 배출계수 (기본값)
        process_factors = [
            ('process', '석회석', 0.44, 'tCO2/ton', '기본값'),
            ('process', '시멘트', 0.5, 'tCO2/ton', '기본값'),
        ]
        
        all_factors = fuel_factors + electricity_factors + process_factors
        
        for factor_type, material_name, emission_factor, unit, source in all_factors:
            cur.execute("""
                INSERT INTO emission_factors (factor_type, material_name, emission_factor, unit, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (factor_type, material_name, emission_factor, unit, source))
        
        conn.commit()
        print("✅ 배출계수 테이블 생성 완료!")
        print("📋 테이블 구조:")
        print("  - id: SERIAL PRIMARY KEY")
        print("  - factor_type: ENUM('fuel', 'electricity', 'process', 'precursor')")
        print("  - material_name: TEXT NOT NULL")
        print("  - emission_factor: DECIMAL(10,6) NOT NULL")
        print("  - unit: TEXT NOT NULL")
        print("  - source: TEXT")
        print("  - valid_from/valid_to: DATE")
        print(f"  - 기본 데이터 {len(all_factors)}개 삽입 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_emission_factors_table()
