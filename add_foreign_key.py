import psycopg2

# Railway DB 연결
conn = psycopg2.connect(
    "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
)
cur = conn.cursor()

# product 테이블의 install_id에 외래키 제약조건 추가
cur.execute("""
ALTER TABLE product 
ADD CONSTRAINT fk_product_install 
FOREIGN KEY (install_id) REFERENCES install(id);
""")

conn.commit()
cur.close()
conn.close()

print("외래키 제약조건 추가 완료 ✅")
print("product.install_id -> install.id 외래키 관계가 설정되었습니다.")
