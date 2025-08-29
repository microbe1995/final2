import os
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_all_schemas():
    print("🔍 CBAM 서비스 모든 스키마 기준으로 DB 확인 및 수정...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 스키마 기준 테이블 정의
    schema_definitions = {
        'install': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'install_name': 'TEXT NOT NULL',
                'reporting_year': 'INTEGER NOT NULL DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': ['CREATE INDEX idx_install_name ON install(install_name)']
        },
        'product': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'install_id': 'INTEGER NOT NULL REFERENCES install(id)',
                'product_name': 'TEXT NOT NULL',
                'product_category': 'TEXT NOT NULL',
                'prostart_period': 'DATE NOT NULL',
                'proend_period': 'DATE NOT NULL',
                'product_amount': 'NUMERIC(15, 6) NOT NULL DEFAULT 0',
                'cncode_total': 'TEXT',
                'goods_name': 'TEXT',
                'goods_engname': 'TEXT',
                'aggrgoods_name': 'TEXT',
                'aggrgoods_engname': 'TEXT',
                'product_sell': 'NUMERIC(15, 6) DEFAULT 0',
                'product_eusell': 'NUMERIC(15, 6) DEFAULT 0',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': [
                'CREATE INDEX idx_product_install_id ON product(install_id)',
                'CREATE INDEX idx_product_name ON product(product_name)'
            ]
        },
        'process': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'process_name': 'TEXT NOT NULL',
                'start_period': 'DATE NOT NULL',
                'end_period': 'DATE NOT NULL',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': ['CREATE INDEX idx_process_name ON process(process_name)']
        },
        'product_process': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'product_id': 'INTEGER NOT NULL REFERENCES product(id)',
                'process_id': 'INTEGER NOT NULL REFERENCES process(id)',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': [
                'CREATE INDEX idx_product_process_product_id ON product_process(product_id)',
                'CREATE INDEX idx_product_process_process_id ON product_process(process_id)'
            ]
        },
        'edge': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'source_id': 'INTEGER NOT NULL',
                'target_id': 'INTEGER NOT NULL',
                'edge_kind': 'TEXT NOT NULL',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': [
                'CREATE INDEX idx_edge_source_id ON edge(source_id)',
                'CREATE INDEX idx_edge_target_id ON edge(target_id)'
            ]
        },
        'process_attrdir_emission': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'process_id': 'INTEGER NOT NULL REFERENCES process(id) ON DELETE CASCADE',
                'total_matdir_emission': 'NUMERIC(15, 6) NOT NULL DEFAULT 0',
                'total_fueldir_emission': 'NUMERIC(15, 6) NOT NULL DEFAULT 0',
                'attrdir_em': 'NUMERIC(15, 6) NOT NULL DEFAULT 0',
                'calculation_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': ['CREATE INDEX idx_process_attrdir_emission_process_id ON process_attrdir_emission(process_id)']
        },
        'matdir': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'process_id': 'INTEGER NOT NULL REFERENCES process(id) ON DELETE CASCADE',
                'mat_name': 'VARCHAR(255) NOT NULL',
                'mat_factor': 'NUMERIC(10, 6) NOT NULL',
                'mat_amount': 'NUMERIC(15, 6) NOT NULL',
                'oxyfactor': 'NUMERIC(5, 4) DEFAULT 1.0000',
                'matdir_em': 'NUMERIC(15, 6) DEFAULT 0',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': ['CREATE INDEX idx_matdir_process_id ON matdir(process_id)']
        },
        'fueldir': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'process_id': 'INTEGER NOT NULL REFERENCES process(id) ON DELETE CASCADE',
                'fuel_name': 'VARCHAR(255) NOT NULL',
                'fuel_factor': 'NUMERIC(10, 6) NOT NULL',
                'fuel_amount': 'NUMERIC(15, 6) NOT NULL',
                'fuel_oxyfactor': 'NUMERIC(5, 4) DEFAULT 1.0000',
                'fueldir_em': 'NUMERIC(15, 6) DEFAULT 0',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'indexes': ['CREATE INDEX idx_fueldir_process_id ON fueldir(process_id)']
        },
        'material_master': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'mat_name': 'VARCHAR(255) NOT NULL',
                'mat_engname': 'VARCHAR(255) NOT NULL',
                'carbon_content': 'NUMERIC(10, 6)',
                'mat_factor': 'NUMERIC(10, 6) NOT NULL'
            },
            'indexes': [
                'CREATE INDEX idx_material_master_name ON material_master(mat_name)',
                'CREATE INDEX idx_material_master_engname ON material_master(mat_engname)'
            ]
        },
        'fuel_master': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'fuel_name': 'VARCHAR(255) NOT NULL',
                'fuel_engname': 'VARCHAR(255) NOT NULL',
                'fuel_factor': 'NUMERIC(10, 6) NOT NULL',
                'net_calory': 'NUMERIC(10, 6)'
            },
            'indexes': [
                'CREATE INDEX idx_fuel_master_name ON fuel_master(fuel_name)',
                'CREATE INDEX idx_fuel_master_engname ON fuel_master(fuel_engname)'
            ]
        },
        'hs_cn_mapping': {
            'columns': {
                'id': 'SERIAL PRIMARY KEY',
                'hscode': 'VARCHAR(6) NOT NULL',
                'aggregoods_name': 'TEXT',
                'aggregoods_engname': 'TEXT',
                'cncode_total': 'VARCHAR(8) NOT NULL',
                'goods_name': 'TEXT',
                'goods_engname': 'TEXT'
            },
            'indexes': [
                'CREATE INDEX idx_hs_cn_mapping_hscode ON hs_cn_mapping(hscode)',
                'CREATE INDEX idx_hs_cn_mapping_cncode ON hs_cn_mapping(cncode_total)'
            ]
        }
    }

    # 각 테이블 확인 및 수정
    for table_name, schema_def in schema_definitions.items():
        print(f"\n🔍 {table_name} 테이블 확인 중...")
        
        # 1. 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            )
        """, (table_name,))
        table_exists = cursor.fetchone()['exists']
        
        if not table_exists:
            print(f"  ❌ {table_name} 테이블이 존재하지 않습니다. 생성합니다...")
            create_table(cursor, table_name, schema_def)
        else:
            # 2. 컬럼 구조 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            current_columns = cursor.fetchall()
            
            # 컬럼 비교
            current_col_names = [col['column_name'] for col in current_columns]
            missing_columns = []
            
            for expected_col, expected_def in schema_def['columns'].items():
                if expected_col not in current_col_names:
                    missing_columns.append((expected_col, expected_def))
            
            if missing_columns:
                print(f"  ⚠️ {table_name} 테이블에 누락된 컬럼이 있습니다: {len(missing_columns)}개")
                for col_name, col_def in missing_columns:
                    print(f"    - {col_name}: {col_def}")
                    add_column(cursor, table_name, col_name, col_def)
            else:
                print(f"  ✅ {table_name} 테이블 구조가 정상입니다.")

    # 3. 인덱스 확인 및 생성
    print("\n📋 인덱스 확인 및 생성...")
    for table_name, schema_def in schema_definitions.items():
        for index_sql in schema_def.get('indexes', []):
            try:
                cursor.execute(index_sql)
                print(f"  ✅ 인덱스 생성: {index_sql}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"  ℹ️ 인덱스 이미 존재: {index_sql}")
                else:
                    print(f"  ❌ 인덱스 생성 실패: {e}")

    cursor.close()
    conn.close()
    print("\n🎉 모든 스키마 확인 및 수정 완료!")

def create_table(cursor, table_name, schema_def):
    """테이블 생성"""
    columns_sql = []
    for col_name, col_def in schema_def['columns'].items():
        columns_sql.append(f"{col_name} {col_def}")
    
    create_sql = f"""
    CREATE TABLE {table_name} (
        {', '.join(columns_sql)}
    )
    """
    
    try:
        cursor.execute(create_sql)
        print(f"  ✅ {table_name} 테이블 생성 완료")
    except Exception as e:
        print(f"  ❌ {table_name} 테이블 생성 실패: {e}")

def add_column(cursor, table_name, column_name, column_def):
    """컬럼 추가"""
    add_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
    
    try:
        cursor.execute(add_sql)
        print(f"    ✅ {column_name} 컬럼 추가 완료")
    except Exception as e:
        print(f"    ❌ {column_name} 컬럼 추가 실패: {e}")

if __name__ == "__main__":
    check_all_schemas()
