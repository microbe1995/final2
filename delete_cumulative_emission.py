import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def delete_cumulative_emission():
    print("🗑️ cumulative_emission 테이블 삭제 중...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. 테이블 존재 여부 확인
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'cumulative_emission'
        )
    """)
    table_exists = cursor.fetchone()['exists']
    
    if table_exists:
        print("  ✅ cumulative_emission 테이블이 존재합니다.")
        
        # 2. 테이블 데이터 확인
        cursor.execute("SELECT COUNT(*) as count FROM cumulative_emission")
        data_count = cursor.fetchone()['count']
        print(f"  📊 테이블 내 데이터: {data_count}개 레코드")
        
        # 3. 테이블 삭제
        print("  🗑️ cumulative_emission 테이블 삭제 중...")
        cursor.execute("DROP TABLE IF EXISTS cumulative_emission CASCADE")
        print("  ✅ cumulative_emission 테이블 삭제 완료")
    else:
        print("  ℹ️ cumulative_emission 테이블이 존재하지 않습니다.")

    # 4. 삭제 후 확인
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        AND table_name LIKE '%emission%'
        ORDER BY table_name
    """)
    remaining_emission_tables = cursor.fetchall()
    
    print(f"\n📋 삭제 후 남은 emission 관련 테이블들:")
    for table in remaining_emission_tables:
        print(f"  - {table['table_name']}")

    cursor.close()
    conn.close()
    print("\n🎉 cumulative_emission 테이블 삭제 완료!")

if __name__ == "__main__":
    delete_cumulative_emission()
