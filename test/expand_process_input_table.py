#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor

def expand_process_input_table():
    """기존 process_input 테이블을 CBAM 규정에 맞게 확장"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔧 process_input 테이블 확장 중...")
        
        # 1. 기존 테이블 구조 확인
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'process_input'
            ORDER BY ordinal_position;
        """)
        
        existing_columns = [row[0] for row in cur.fetchall()]
        print(f"📋 기존 컬럼: {existing_columns}")
        
        # 2. 새로운 컬럼들 추가
        new_columns = [
            ("emission_factor_id", "INTEGER REFERENCES emission_factors(id)"),
            ("allocation_method", "allocation_method_enum DEFAULT 'direct'"),
            ("allocation_ratio", "DECIMAL(5,4) DEFAULT 1.0"),
            ("measurement_uncertainty", "DECIMAL(5,4)"),
            ("data_quality", "TEXT"),
            ("verification_status", "TEXT DEFAULT 'pending'"),
            ("notes", "TEXT")
        ]
        
        for column_name, column_definition in new_columns:
            if column_name not in existing_columns:
                try:
                    cur.execute(f"ALTER TABLE process_input ADD COLUMN {column_name} {column_definition};")
                    print(f"✅ 컬럼 추가: {column_name}")
                except Exception as e:
                    print(f"⚠️ 컬럼 {column_name} 추가 실패 (이미 존재할 수 있음): {e}")
        
        # 3. 기존 컬럼들의 제약조건 개선
        print("🔧 기존 컬럼 제약조건 개선 중...")
        
        # factor, oxy_factor에 기본값 설정
        try:
            cur.execute("ALTER TABLE process_input ALTER COLUMN factor SET DEFAULT 1.0;")
            cur.execute("ALTER TABLE process_input ALTER COLUMN oxy_factor SET DEFAULT 1.0;")
            print("✅ 기본값 설정 완료")
        except Exception as e:
            print(f"⚠️ 기본값 설정 실패: {e}")
        
        # 4. 인덱스 추가
        print("🔧 인덱스 추가 중...")
        
        new_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_process_input_factor_id ON process_input(emission_factor_id);",
            "CREATE INDEX IF NOT EXISTS idx_process_input_allocation ON process_input(allocation_method);",
            "CREATE INDEX IF NOT EXISTS idx_process_input_verification ON process_input(verification_status);"
        ]
        
        for index_sql in new_indexes:
            try:
                cur.execute(index_sql)
                print(f"✅ 인덱스 추가 완료")
            except Exception as e:
                print(f"⚠️ 인덱스 추가 실패: {e}")
        
        # 5. 기존 데이터에 배출계수 연결
        print("🔧 기존 데이터 배출계수 연결 중...")
        
        # 기본 배출계수로 factor 업데이트
        cur.execute("""
            UPDATE process_input 
            SET factor = ef.emission_factor
            FROM emission_factors ef
            WHERE process_input.input_name = ef.material_name
            AND process_input.factor IS NULL;
        """)
        
        updated_count = cur.rowcount
        print(f"✅ {updated_count}개 레코드의 배출계수 업데이트 완료")
        
        conn.commit()
        print("✅ process_input 테이블 확장 완료!")
        print("📋 추가된 컬럼:")
        for column_name, _ in new_columns:
            print(f"  - {column_name}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    expand_process_input_table()
