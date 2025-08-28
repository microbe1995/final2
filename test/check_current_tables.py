import psycopg2
import os

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_current_tables():
    conn = None
    cursor = None
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 모든 테이블 조회
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print("📋 현재 데이터베이스의 모든 테이블:")
        print("=" * 50)
        for table in tables:
            print(f"• {table[0]}")
        
        print(f"\n총 {len(tables)}개의 테이블이 있습니다.")
        
        # 유지할 테이블 목록
        keep_tables = ['edge', 'companies', 'countries', 'install', 'process', 'hs_cn_mapping', 'product', 'users', 'product_process']
        
        print(f"\n🔒 유지할 테이블 ({len(keep_tables)}개):")
        for table in keep_tables:
            print(f"• {table}")
        
        # 삭제할 테이블 목록
        delete_tables = [table[0] for table in tables if table[0] not in keep_tables]
        
        print(f"\n🗑️ 삭제할 테이블 ({len(delete_tables)}개):")
        for table in delete_tables:
            print(f"• {table}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_current_tables()
