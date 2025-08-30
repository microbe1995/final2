import os
import pandas as pd
import psycopg2
from decimal import Decimal

def load_material_master_to_railway():
    """Material Master CSV 데이터를 Railway DB에 로드"""
    
    # Railway DB 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    print("🚀 Material Master 데이터 로드 시작...")
    
    try:
        # 1. CSV 파일 경로
        csv_file_path = "C:/Users/bitcamp/Desktop/CBAM/LCA_final-main-new/masterdb/material_master.csv"
        
        # 2. CSV 파일 존재 확인
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return
        
        # 3. CSV 파일 읽기
        print(f"\n📊 CSV 파일 읽기")
        df = pd.read_csv(csv_file_path)
        print(f"   파일 경로: {csv_file_path}")
        print(f"   총 행 수: {len(df)}개")
        print(f"   컬럼: {list(df.columns)}")
        
        # 4. 데이터베이스 연결
        print(f"\n🔗 Railway DB 연결")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 5. material_master 테이블 생성
        print(f"\n📋 material_master 테이블 생성")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS material_master (
            id SERIAL PRIMARY KEY,
            mat_name VARCHAR(255) NOT NULL,
            mat_engname VARCHAR(255) NOT NULL,
            carbon_content NUMERIC(10, 6),
            mat_factor NUMERIC(10, 6) NOT NULL
        );
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ material_master 테이블 생성 완료")
        
        # 6. 기존 데이터 삭제
        print(f"\n🗑️ 기존 데이터 삭제")
        cursor.execute("DELETE FROM material_master")
        conn.commit()
        print("✅ 기존 material_master 데이터 삭제 완료")
        
        # 7. 새 데이터 삽입
        print(f"\n📥 데이터 삽입")
        success_count = 0
        
        for index, row in df.iterrows():
            try:
                # carbon_content가 '-'인 경우 NULL로 처리
                carbon_content = None if row['carbon_content'] == '-' else Decimal(str(row['carbon_content']))
                mat_factor = Decimal(str(row['mat_factor']))
                
                insert_sql = """
                INSERT INTO material_master (mat_name, mat_engname, carbon_content, mat_factor)
                VALUES (%s, %s, %s, %s)
                """
                
                cursor.execute(insert_sql, (
                    row['mat_name'],
                    row['mat_engname'],
                    carbon_content,
                    mat_factor
                ))
                
                success_count += 1
                print(f"   ✅ {row['mat_name']} - 배출계수: {mat_factor}")
                
            except Exception as e:
                print(f"   ❌ 행 {index + 1} 처리 실패: {e}")
                continue
        
        conn.commit()
        print(f"\n✅ 데이터 삽입 완료: {success_count}/{len(df)}개 성공")
        
        # 8. 로드된 데이터 확인
        print(f"\n📋 로드된 데이터 확인")
        cursor.execute("SELECT COUNT(*) FROM material_master")
        total_count = cursor.fetchone()[0]
        print(f"   총 원료 수: {total_count}개")
        
        cursor.execute("""
            SELECT mat_name, mat_engname, carbon_content, mat_factor 
            FROM material_master 
            ORDER BY mat_name
        """)
        
        results = cursor.fetchall()
        print(f"\n   📋 로드된 원료 목록:")
        for i, row in enumerate(results[:10], 1):  # 처음 10개만 표시
            mat_name, mat_engname, carbon_content, mat_factor = row
            carbon_info = f" (탄소함량: {carbon_content})" if carbon_content else ""
            print(f"   {i:2d}. {mat_name} ({mat_engname}) - 배출계수: {mat_factor}{carbon_info}")
        
        if len(results) > 10:
            print(f"   ... 외 {len(results) - 10}개")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Material Master 데이터 로드 완료!")
        print(f"   총 {total_count}개의 원료 배출계수가 Railway DB에 저장되었습니다.")
        
    except Exception as e:
        print(f"❌ Material Master 데이터 로드 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_material_master_to_railway()
