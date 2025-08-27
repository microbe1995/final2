import psycopg2

# Railway DB 연결
conn = psycopg2.connect(
    "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
)
cur = conn.cursor()

# product 테이블 생성 (외래키 제약조건 제거)
cur.execute("""
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    install_id INT NOT NULL,
    product_name TEXT NOT NULL,
    product_category TEXT NOT NULL CHECK (product_category IN ('단순제품', '복합제품')),
    prostart_period DATE NOT NULL,
    proend_period DATE NOT NULL,
    product_cncode TEXT,
    goods_name TEXT,
    aggrgoods_name TEXT,
    product_amount FLOAT NOT NULL,
    product_sell FLOAT,
    product_eusell FLOAT
);
""")

conn.commit()
cur.close()
conn.close()

print("product 테이블 생성 완료 ✅")
print("참고: install_id 외래키 제약조건은 install 테이블 생성 후 추가할 수 있습니다.")
