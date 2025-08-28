import psycopg2
from psycopg2 import sql

# Railway PostgreSQL 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def create_matdir_table():
    conn = None
    cursor = None
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # matdir 테이블 생성
        create_table_query = """
        CREATE TABLE IF NOT EXISTS matdir (
            id SERIAL PRIMARY KEY,
            process_id INTEGER NOT NULL,
            mat_name VARCHAR(255) NOT NULL,           -- 투입된 원료명
            mat_factor DECIMAL(10,6) NOT NULL,        -- 배출계수
            mat_amount DECIMAL(15,6) NOT NULL,        -- 투입된 원료량
            oxyfactor DECIMAL(5,4) DEFAULT 1.0000,    -- 산화계수 (기본값 1)
            matdir_em DECIMAL(15,6) DEFAULT 0,        -- 원료직접배출량 (계산 결과)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        
        print("✅ matdir 테이블이 성공적으로 생성되었습니다!")
        
        # 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'matdir' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 matdir 테이블 구조:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (NULL: {col[2]}, DEFAULT: {col[3]})")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_matdir_table()
