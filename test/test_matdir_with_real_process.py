import psycopg2
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def test_matdir_with_real_process():
    """실제 process_id로 matdir 데이터 삽입 테스트"""
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ 데이터베이스 연결 성공")
        
        # 1. 실제 process 데이터 확인
        cursor.execute("SELECT id, process_name FROM process ORDER BY id;")
        processes = cursor.fetchall()
        
        print(f"\n📋 실제 process 데이터:")
        for proc in processes:
            print(f"  - ID: {proc[0]}, Name: {proc[1]}")
        
        if not processes:
            print("❌ process 데이터가 없습니다!")
            return
        
        # 2. 실제 process_id로 matdir 데이터 삽입
        real_process_id = processes[0][0]  # 첫 번째 process의 ID 사용
        print(f"\n🧪 process_id {real_process_id}로 matdir 데이터 삽입 시도...")
        
        try:
            cursor.execute("""
                INSERT INTO matdir (process_id, mat_name, mat_factor, mat_amount, oxyfactor, matdir_em)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, process_id, mat_name, matdir_em;
            """, (real_process_id, '철광석', 1.5, 100.0, 1.0, 150.0))
            
            result = cursor.fetchone()
            print(f"✅ matdir 데이터 삽입 성공!")
            print(f"  - ID: {result[0]}")
            print(f"  - Process ID: {result[1]}")
            print(f"  - Material: {result[2]}")
            print(f"  - Emission: {result[3]}")
            
            # 3. 삽입된 데이터 확인
            cursor.execute("SELECT COUNT(*) FROM matdir;")
            count = cursor.fetchone()[0]
            print(f"\n📊 matdir 테이블 현재 데이터 개수: {count}개")
            
            cursor.execute("""
                SELECT m.id, m.process_id, p.process_name, m.mat_name, m.matdir_em
                FROM matdir m
                JOIN process p ON m.process_id = p.id
                ORDER BY m.id DESC
                LIMIT 5;
            """)
            
            matdir_data = cursor.fetchall()
            print(f"\n📋 matdir 테이블 최신 데이터:")
            for data in matdir_data:
                print(f"  - ID: {data[0]}, Process: {data[2]} (ID: {data[1]}), Material: {data[3]}, Emission: {data[4]}")
            
            # 4. 테스트 데이터 삭제 (선택사항)
            print(f"\n🧹 테스트 데이터 삭제...")
            cursor.execute("DELETE FROM matdir WHERE id = %s;", (result[0],))
            print(f"✅ 테스트 데이터 삭제 완료")
            
        except Exception as e:
            print(f"❌ matdir 데이터 삽입 실패: {str(e)}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_matdir_with_real_process()
