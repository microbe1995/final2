import psycopg2
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_matdir_table():
    """matdir 테이블 존재 여부 확인"""
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # matdir 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'matdir'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ matdir 테이블이 존재합니다.")
            
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
            
            # 기존 데이터 확인
            cursor.execute("SELECT COUNT(*) FROM matdir;")
            count = cursor.fetchone()[0]
            print(f"\n📊 현재 데이터 개수: {count}개")
            
            if count > 0:
                cursor.execute("SELECT * FROM matdir LIMIT 3;")
                rows = cursor.fetchall()
                print("\n📄 샘플 데이터:")
                for row in rows:
                    print(f"  - {row}")
                    
        else:
            print("❌ matdir 테이블이 존재하지 않습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_matdir_table()
