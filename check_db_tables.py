import psycopg2

# DB 연결
conn = psycopg2.connect('postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway')
cur = conn.cursor()

# 테이블 목록 조회
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
tables = cur.fetchall()

print('현재 DB 테이블 목록:')
for table in tables:
    print(f'- {table[0]}')

# process 테이블 구조 확인
print('\n=== process 테이블 구조 ===')
try:
    cur.execute("SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name = 'process' ORDER BY ordinal_position;")
    columns = cur.fetchall()
    for col in columns:
        print(f'- {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})')
except Exception as e:
    print(f'process 테이블 조회 실패: {e}')

# process 테이블 제약 조건 확인
print('\n=== process 테이블 제약 조건 ===')
try:
    cur.execute("""
        SELECT conname, contype, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'process'::regclass;
    """)
    constraints = cur.fetchall()
    for constraint in constraints:
        print(f'- {constraint[0]}: {constraint[1]} - {constraint[2]}')
except Exception as e:
    print(f'제약 조건 조회 실패: {e}')

conn.close()
