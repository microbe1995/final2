import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_edge_structure():
    print("🔍 edge 테이블 구조 확인 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. edge 테이블 컬럼 구조 확인
    print("\n📋 edge 테이블 컬럼 구조:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'edge'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")

    # 2. edge 테이블 데이터 샘플 확인
    print("\n📊 edge 테이블 데이터 샘플:")
    cursor.execute("""
        SELECT * FROM edge LIMIT 5
    """)
    edges = cursor.fetchall()
    for edge in edges:
        print(f"  - {edge}")

    # 3. process 테이블 데이터 확인
    print("\n📊 process 테이블 데이터:")
    cursor.execute("""
        SELECT id, name, install_id FROM process ORDER BY id LIMIT 10
    """)
    processes = cursor.fetchall()
    for process in processes:
        print(f"  - ID: {process['id']}, 이름: {process['name']}, 사업장: {process['install_id']}")

    # 4. process_attrdir_emission 데이터 확인
    print("\n📊 process_attrdir_emission 데이터:")
    cursor.execute("""
        SELECT process_id, attrdir_em FROM process_attrdir_emission ORDER BY process_id LIMIT 10
    """)
    emissions = cursor.fetchall()
    for emission in emissions:
        print(f"  - 공정 {emission['process_id']}: {emission['attrdir_em']}")

    cursor.close()
    conn.close()
    print("\n✅ edge 테이블 구조 확인 완료!")

if __name__ == "__main__":
    check_edge_structure()
