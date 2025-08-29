import os
import psycopg2
from psycopg2.extras import RealDictCursor

# DB 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_db_status():
    """DB 상태 확인"""
    try:
        print("🔍 DB 상태 확인 중...")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. 테이블 존재 여부 확인
        print("\n📋 테이블 존재 여부:")
        tables_to_check = ['install', 'product', 'process', 'product_process', 'matdir', 'fueldir', 'process_attrdir_emission']
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()[0]
            status = "✅ 존재" if exists else "❌ 없음"
            print(f"  {table}: {status}")
        
        # 2. install 테이블 데이터 확인
        print("\n🏭 install 테이블 데이터:")
        cursor.execute("SELECT id, install_name, reporting_year FROM install ORDER BY id")
        installs = cursor.fetchall()
        
        if installs:
            print(f"  총 {len(installs)}개 사업장:")
            for install in installs:
                print(f"    - ID: {install['id']}, 이름: {install['install_name']}, 보고기간: {install['reporting_year']}")
        else:
            print("  ⚠️ 사업장 데이터가 없습니다.")
        
        cursor.close()
        conn.close()
        
        print("\n✅ DB 상태 확인 완료!")
        
    except Exception as e:
        print(f"❌ DB 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    check_db_status()
