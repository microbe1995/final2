import psycopg2
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_matdir_table_creation():
    """matdir 테이블 생성 상태 확인"""
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ 데이터베이스 연결 성공")
        
        # 1. matdir 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'matdir'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"📋 matdir 테이블 존재: {table_exists}")
        
        if table_exists:
            # 2. 테이블 구조 확인
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
            
            # 3. 데이터 개수 확인
            cursor.execute("SELECT COUNT(*) FROM matdir;")
            count = cursor.fetchone()[0]
            print(f"\n📊 현재 데이터 개수: {count}개")
            
            # 4. 외래키 제약조건 확인
            cursor.execute("""
                SELECT 
                    tc.constraint_name, 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name='matdir';
            """)
            
            foreign_keys = cursor.fetchall()
            print(f"\n🔗 외래키 제약조건:")
            for fk in foreign_keys:
                print(f"  - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
            
            # 5. process 테이블 존재 확인 (외래키 참조)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'process'
                );
            """)
            
            process_exists = cursor.fetchone()[0]
            print(f"\n🏭 process 테이블 존재: {process_exists}")
            
            if process_exists:
                cursor.execute("SELECT COUNT(*) FROM process;")
                process_count = cursor.fetchone()[0]
                print(f"📊 process 테이블 데이터 개수: {process_count}개")
                
                if process_count > 0:
                    cursor.execute("SELECT id, process_name FROM process LIMIT 3;")
                    processes = cursor.fetchall()
                    print(f"📋 process 테이블 샘플:")
                    for proc in processes:
                        print(f"  - ID: {proc[0]}, Name: {proc[1]}")
            
            # 6. 테스트 데이터 삽입 시도
            print(f"\n🧪 테스트 데이터 삽입 시도...")
            try:
                cursor.execute("""
                    INSERT INTO matdir (process_id, mat_name, mat_factor, mat_amount, oxyfactor, matdir_em)
                    VALUES (1, '테스트 원료', 1.0, 1.0, 1.0, 1.0)
                    RETURNING id;
                """)
                
                test_id = cursor.fetchone()[0]
                print(f"✅ 테스트 데이터 삽입 성공: ID {test_id}")
                
                # 테스트 데이터 삭제
                cursor.execute("DELETE FROM matdir WHERE id = %s;", (test_id,))
                print(f"🧹 테스트 데이터 삭제 완료")
                
            except Exception as e:
                print(f"❌ 테스트 데이터 삽입 실패: {str(e)}")
                
        else:
            print("❌ matdir 테이블이 존재하지 않습니다!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_matdir_table_creation()
