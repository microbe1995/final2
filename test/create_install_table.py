import psycopg2

# Railway DB 연결
conn = psycopg2.connect(
    "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
)
cur = conn.cursor()

# install 테이블 생성
cur.execute("""
CREATE TABLE install (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
""")

conn.commit()
cur.close()
conn.close()

print("install 테이블 생성 완료 ✅")
