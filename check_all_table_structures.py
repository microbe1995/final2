import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_all_table_structures():
    print("🔍 모든 테이블 구조 확인 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    tables = ['edge', 'process', 'process_attrdir_emission', 'matdir', 'fueldir']
    
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
        
        # 데이터 샘플 확인
        print(f"\n📊 {table_name} 데이터 샘플:")
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            data = cursor.fetchall()
            for row in data:
                print(f"  - {row}")
        except Exception as e:
            print(f"  - 데이터 조회 오류: {e}")

    cursor.close()
    conn.close()
    print("\n✅ 모든 테이블 구조 확인 완료!")

if __name__ == "__main__":
    check_all_table_structures()
