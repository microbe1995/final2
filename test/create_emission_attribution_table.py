#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor

def create_emission_attribution_table():
    """배출량 귀속 테이블 생성"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔧 배출량 귀속 테이블 생성 중...")
        
        # 1. 배출량 타입 ENUM 생성
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE emission_type_enum AS ENUM ('direct', 'indirect', 'precursor');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # 2. 배분 방법 ENUM 생성
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE allocation_method_enum AS ENUM ('direct', 'proportional', 'time_based', 'mass_based', 'energy_based');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        
        # 3. 배출량 귀속 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS emission_attribution (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
                process_id INTEGER REFERENCES process(id) ON DELETE CASCADE,
                emission_type emission_type_enum NOT NULL,
                emission_amount DECIMAL(15,6) NOT NULL DEFAULT 0,
                attribution_method allocation_method_enum NOT NULL,
                allocation_ratio DECIMAL(5,4) DEFAULT 1.0,
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 4. 제품별 총 배출량 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_emissions (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
                direct_emission DECIMAL(15,6) NOT NULL DEFAULT 0,
                indirect_emission DECIMAL(15,6) NOT NULL DEFAULT 0,
                precursor_emission DECIMAL(15,6) NOT NULL DEFAULT 0,
                total_emission DECIMAL(15,6) NOT NULL DEFAULT 0,
                emission_intensity DECIMAL(15,6), -- tCO2/ton
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 5. 인덱스 생성
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_attribution_product ON emission_attribution(product_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_attribution_process ON emission_attribution(process_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_emission_attribution_type ON emission_attribution(emission_type);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_product_emissions_product ON product_emissions(product_id);")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_product_emissions_unique ON product_emissions(product_id);")
        
        conn.commit()
        print("✅ 배출량 귀속 테이블 생성 완료!")
        print("📋 테이블 구조:")
        print("\n1. emission_attribution 테이블:")
        print("  - id: SERIAL PRIMARY KEY")
        print("  - product_id: INTEGER (product.id 참조)")
        print("  - process_id: INTEGER (process.id 참조)")
        print("  - emission_type: ENUM('direct', 'indirect', 'precursor')")
        print("  - emission_amount: DECIMAL(15,6) NOT NULL")
        print("  - attribution_method: ENUM('direct', 'proportional', 'time_based', 'mass_based', 'energy_based')")
        print("  - allocation_ratio: DECIMAL(5,4) DEFAULT 1.0")
        print("  - calculation_date: TIMESTAMP")
        
        print("\n2. product_emissions 테이블:")
        print("  - id: SERIAL PRIMARY KEY")
        print("  - product_id: INTEGER (product.id 참조, UNIQUE)")
        print("  - direct_emission: DECIMAL(15,6) NOT NULL")
        print("  - indirect_emission: DECIMAL(15,6) NOT NULL")
        print("  - precursor_emission: DECIMAL(15,6) NOT NULL")
        print("  - total_emission: DECIMAL(15,6) NOT NULL")
        print("  - emission_intensity: DECIMAL(15,6) (tCO2/ton)")
        print("  - calculation_date: TIMESTAMP")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_emission_attribution_table()
