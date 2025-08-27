import psycopg2

# Railway DB 연결
conn = psycopg2.connect(
    "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
)
cur = conn.cursor()

# 삭제할 테이블들만 삭제
cur.execute("""
SET session_replication_role = replica;

DROP TABLE IF EXISTS calculation_results CASCADE;
DROP TABLE IF EXISTS precursors CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS fuels CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS boundary CASCADE;
DROP TABLE IF EXISTS node CASCADE;
DROP TABLE IF EXISTS edge CASCADE;
DROP TABLE IF EXISTS operation CASCADE;
DROP TABLE IF EXISTS production_emission CASCADE;
DROP TABLE IF EXISTS product CASCADE;

SET session_replication_role = DEFAULT;
""")

conn.commit()
cur.close()
conn.close()

print("삭제 완료 ✅")
