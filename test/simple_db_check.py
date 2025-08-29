import psycopg2

DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

try:
    print("🔍 DB 연결 테스트 중...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # 테이블 목록 확인
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"✅ DB 연결 성공! 발견된 테이블: {len(tables)}개")
    
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ DB 연결 실패: {e}")
