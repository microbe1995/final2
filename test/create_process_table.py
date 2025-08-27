import psycopg2

def create_process_table():
    """process 테이블 생성"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔧 process 테이블 생성 중...")
        
        # process 테이블 생성
        cur.execute("""
            CREATE TABLE IF NOT EXISTS process (
                id SERIAL PRIMARY KEY,
                product_id INT NOT NULL REFERENCES product(id),
                process_name TEXT NOT NULL,
                start_period DATE NOT NULL,
                end_period DATE NOT NULL
            );
        """)
        
        # 인덱스 생성
        cur.execute("CREATE INDEX IF NOT EXISTS idx_process_product_id ON process(product_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_process_name ON process(process_name);")
        
        conn.commit()
        print("✅ process 테이블 생성 완료!")
        print("📋 테이블 구조:")
        print("  - id: SERIAL PRIMARY KEY")
        print("  - product_id: INT NOT NULL (product.id 참조)")
        print("  - process_name: TEXT NOT NULL")
        print("  - start_period: DATE NOT NULL")
        print("  - end_period: DATE NOT NULL")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_process_table()
