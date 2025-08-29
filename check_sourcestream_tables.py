import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_sourcestream_tables():
    print("🔍 sourcestream 테이블들 확인 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    tables = ['process_chain', 'process_chain_link', 'cumulative_emission', 'source_stream']
    
    for table_name in tables:
        print(f"\n📋 {table_name} 테이블 구조:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # 데이터 확인
        print(f"\n📊 {table_name} 데이터:")
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            data = cursor.fetchall()
            if data:
                for row in data:
                    print(f"  - {row}")
            else:
                print(f"  - 데이터 없음")
        except Exception as e:
            print(f"  - 데이터 조회 오류: {e}")

    cursor.close()
    conn.close()
    print("\n✅ sourcestream 테이블 확인 완료!")

if __name__ == "__main__":
    check_sourcestream_tables()
