import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_current_db_status():
    print("🔍 현재 DB 상태 확인 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. 기존 테이블들 확인
    print("\n📋 기존 테이블들:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('process', 'edge', 'process_attrdir_emission', 'matdir', 'fueldir')
        ORDER BY table_name
    """)
    existing_tables = cursor.fetchall()
    for table in existing_tables:
        print(f"  ✅ {table['table_name']}")

    # 2. sourcestream 관련 테이블들 확인
    print("\n📋 sourcestream 테이블들:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('process_chain', 'process_chain_link', 'cumulative_emission', 'source_stream')
        ORDER BY table_name
    """)
    sourcestream_tables = cursor.fetchall()
    for table in sourcestream_tables:
        print(f"  ✅ {table['table_name']}")

    # 3. edge 테이블의 연결 상태 확인
    print("\n🔗 edge 테이블 연결 상태:")
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM edge 
        GROUP BY type
    """)
    edge_types = cursor.fetchall()
    for edge_type in edge_types:
        print(f"  - {edge_type['type']}: {edge_type['count']}개")

    # 4. process_attrdir_emission 데이터 확인
    print("\n📊 process_attrdir_emission 데이터:")
    cursor.execute("""
        SELECT process_id, attrdir_em, COUNT(*) as count
        FROM process_attrdir_emission 
        GROUP BY process_id, attrdir_em
        ORDER BY process_id
        LIMIT 10
    """)
    emissions = cursor.fetchall()
    for emission in emissions:
        print(f"  - 공정 {emission['process_id']}: {emission['attrdir_em']}")

    # 5. 연결된 공정들 예시 확인
    print("\n🔗 연결된 공정들 예시:")
    cursor.execute("""
        SELECT e.source_id, e.target_id, e.type, 
               p1.name as source_name, p2.name as target_name
        FROM edge e
        JOIN process p1 ON e.source_id = p1.id
        JOIN process p2 ON e.target_id = p2.id
        WHERE e.type = 'continue'
        LIMIT 5
    """)
    connected_processes = cursor.fetchall()
    for conn in connected_processes:
        print(f"  - {conn['source_name']}({conn['source_id']}) → {conn['target_name']}({conn['target_id']})")

    cursor.close()
    conn.close()
    print("\n✅ DB 상태 확인 완료!")

if __name__ == "__main__":
    check_current_db_status()
