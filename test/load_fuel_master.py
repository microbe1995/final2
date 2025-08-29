import pandas as pd
import psycopg2
import os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 데이터베이스 연결 정보
DATABASE_URL = 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway'

def load_fuel_master_data():
    """Fuel Master 데이터를 DB에 로드"""
    
    try:
        # Excel 파일 읽기
        print("📖 Fuel Master Excel 파일 읽기 중...")
        df = pd.read_excel('masterdb/fuel_master.xlsx')
        
        print(f"✅ Excel 파일 읽기 완료: {len(df)}개 행")
        print(f"📋 컬럼: {list(df.columns)}")
        print("\n📊 첫 5행 데이터:")
        print(df.head())
        
        # 데이터베이스 연결
        print("\n🔌 데이터베이스 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # fuel_master 테이블 생성
        print("\n🏗️ fuel_master 테이블 생성 중...")
        create_table_sql = """
        DROP TABLE IF EXISTS fuel_master;
        
        CREATE TABLE fuel_master (
            id SERIAL PRIMARY KEY,
            fuel_name VARCHAR(255) NOT NULL,
            fuel_engname VARCHAR(255) NOT NULL,
            fuel_factor NUMERIC(10, 6) NOT NULL,
            net_calory NUMERIC(10, 6),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_fuel_master_name ON fuel_master(fuel_name);
        CREATE INDEX idx_fuel_master_engname ON fuel_master(fuel_engname);
        """
        
        cursor.execute(create_table_sql)
        print("✅ fuel_master 테이블 생성 완료")
        
        # 데이터 삽입
        print("\n💾 데이터 삽입 중...")
        insert_sql = """
        INSERT INTO fuel_master (fuel_name, fuel_engname, fuel_factor, net_calory)
        VALUES (%s, %s, %s, %s)
        """
        
        inserted_count = 0
        for index, row in df.iterrows():
            try:
                # 데이터 정리
                fuel_name = str(row['fuel_name']).strip()
                fuel_engname = str(row['fuel_engname']).strip()
                fuel_factor = float(row['fuel_factor']) if pd.notna(row['fuel_factor']) else 0.0
                net_calory = float(row['net_calory']) if pd.notna(row['net_calory']) else None
                
                cursor.execute(insert_sql, (fuel_name, fuel_engname, fuel_factor, net_calory))
                inserted_count += 1
                
                if (index + 1) % 10 == 0:
                    print(f"  📝 {index + 1}/{len(df)}개 처리 완료")
                    
            except Exception as e:
                print(f"❌ 행 {index + 1} 삽입 실패: {e}")
                print(f"   데이터: {row.to_dict()}")
        
        print(f"\n✅ 데이터 삽입 완료: {inserted_count}/{len(df)}개")
        
        # 결과 확인
        print("\n🔍 삽입된 데이터 확인...")
        cursor.execute("SELECT COUNT(*) FROM fuel_master")
        total_count = cursor.fetchone()[0]
        print(f"📊 총 {total_count}개 연료 데이터가 저장됨")
        
        cursor.execute("SELECT fuel_name, fuel_engname, fuel_factor, net_calory FROM fuel_master ORDER BY fuel_name LIMIT 5")
        sample_data = cursor.fetchall()
        
        print("\n📋 샘플 데이터:")
        for i, (fuel_name, fuel_engname, fuel_factor, net_calory) in enumerate(sample_data, 1):
            print(f"  {i}. {fuel_name} ({fuel_engname}) - 배출계수: {fuel_factor}, 순발열량: {net_calory}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Fuel Master 데이터 로드 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    load_fuel_master_data()
