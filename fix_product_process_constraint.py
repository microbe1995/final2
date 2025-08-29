import psycopg2

# DB 연결
conn = psycopg2.connect('postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway')
cur = conn.cursor()

try:
    print("🔧 product_process 테이블에 고유 제약 조건 추가 중...")
    
    # (product_id, process_id) 조합에 대한 고유 제약 조건 추가
    cur.execute("""
        ALTER TABLE product_process 
        ADD CONSTRAINT product_process_product_id_process_id_unique 
        UNIQUE (product_id, process_id);
    """)
    
    conn.commit()
    print("✅ 고유 제약 조건 추가 완료!")
    
    # 제약 조건 확인
    print("\n=== 추가된 제약 조건 확인 ===")
    cur.execute("""
        SELECT conname, contype, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'product_process'::regclass;
    """)
    constraints = cur.fetchall()
    for constraint in constraints:
        print(f'- {constraint[0]}: {constraint[1]} - {constraint[2]}')
        
except Exception as e:
    conn.rollback()
    print(f"❌ 오류 발생: {e}")
    
finally:
    conn.close()
