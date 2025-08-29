import psycopg2

# DB 연결
conn = psycopg2.connect('postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway')
cur = conn.cursor()

print('=== product_process 테이블 구조 ===')
try:
    cur.execute("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'product_process' ORDER BY ordinal_position;")
    columns = cur.fetchall()
    for col in columns:
        print(f'- {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})')
except Exception as e:
    print(f'product_process 테이블 조회 실패: {e}')

print('\n=== product_process 테이블 제약 조건 ===')
try:
    cur.execute("""
        SELECT conname, contype, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'product_process'::regclass;
    """)
    constraints = cur.fetchall()
    for constraint in constraints:
        print(f'- {constraint[0]}: {constraint[1]} - {constraint[2]}')
except Exception as e:
    print(f'제약 조건 조회 실패: {e}')

conn.close()
