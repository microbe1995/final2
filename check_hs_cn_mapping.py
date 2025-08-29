import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_hs_cn_mapping():
    print("🔍 hs_cn_mapping 테이블 상태 확인 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. 테이블 구조 확인
    print("\n📋 hs_cn_mapping 테이블 구조:")
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'hs_cn_mapping'
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")

    # 2. 데이터 확인
    print("\n📊 hs_cn_mapping 데이터:")
    cursor.execute("SELECT COUNT(*) as count FROM hs_cn_mapping")
    count = cursor.fetchone()['count']
    print(f"  - 총 레코드 수: {count}개")

    if count > 0:
        cursor.execute("SELECT * FROM hs_cn_mapping LIMIT 5")
        data = cursor.fetchall()
        for row in data:
            print(f"  - {row}")
    else:
        print("  - 데이터가 없습니다.")

    # 3. 기존 HS 코드 데이터가 있는지 확인 (다른 테이블명으로)
    print("\n🔍 다른 HS 코드 관련 테이블 확인:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name LIKE '%hs%' OR table_name LIKE '%cn%' OR table_name LIKE '%mapping%'
        ORDER BY table_name
    """)
    hs_related_tables = cursor.fetchall()
    for table in hs_related_tables:
        print(f"  - {table['table_name']}")

    cursor.close()
    conn.close()
    print("\n✅ hs_cn_mapping 테이블 확인 완료!")

if __name__ == "__main__":
    check_hs_cn_mapping()
