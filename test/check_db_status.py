import os
import psycopg2
from psycopg2.extras import RealDictCursor

# DB 연결 정보
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_db_status():
    """DB 상태 확인"""
    try:
        print("🔍 DB 상태 확인 중...")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. 테이블 존재 여부 확인
        print("\n📋 테이블 존재 여부:")
        tables_to_check = ['install', 'product', 'process', 'product_process', 'matdir', 'fueldir', 'process_attrdir_emission']
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()[0]
            status = "✅ 존재" if exists else "❌ 없음"
            print(f"  {table}: {status}")
        
        # 2. install 테이블 데이터 확인
        print("\n🏭 install 테이블 데이터:")
        cursor.execute("SELECT id, install_name, reporting_year FROM install ORDER BY id")
        installs = cursor.fetchall()
        
        if installs:
            print(f"  총 {len(installs)}개 사업장:")
            for install in installs:
                print(f"    - ID: {install['id']}, 이름: {install['install_name']}, 보고기간: {install['reporting_year']}")
        else:
            print("  ⚠️ 사업장 데이터가 없습니다.")
        
        # 3. product 테이블 데이터 확인
        print("\n📦 product 테이블 데이터:")
        cursor.execute("SELECT id, install_id, product_name FROM product ORDER BY id")
        products = cursor.fetchall()
        
        if products:
            print(f"  총 {len(products)}개 제품:")
            for product in products:
                print(f"    - ID: {product['id']}, 사업장ID: {product['install_id']}, 제품명: {product['product_name']}")
        else:
            print("  ⚠️ 제품 데이터가 없습니다.")
        
        # 4. process 테이블 데이터 확인
        print("\n⚙️ process 테이블 데이터:")
        cursor.execute("SELECT id, process_name FROM process ORDER BY id")
        processes = cursor.fetchall()
        
        if processes:
            print(f"  총 {len(processes)}개 공정:")
            for process in processes:
                print(f"    - ID: {process['id']}, 공정명: {process['process_name']}")
        else:
            print("  ⚠️ 공정 데이터가 없습니다.")
        
        # 5. product_process 관계 확인
        print("\n🔗 product_process 관계:")
        cursor.execute("SELECT product_id, process_id FROM product_process ORDER BY product_id, process_id")
        relations = cursor.fetchall()
        
        if relations:
            print(f"  총 {len(relations)}개 관계:")
            for relation in relations:
                print(f"    - 제품ID: {relation['product_id']} ↔ 공정ID: {relation['process_id']}")
        else:
            print("  ⚠️ 제품-공정 관계가 없습니다.")
        
        # 6. matdir 데이터 확인
        print("\n🛢️ matdir 테이블 데이터:")
        cursor.execute("SELECT id, process_id, mat_name, matdir_em FROM matdir ORDER BY process_id")
        matdirs = cursor.fetchall()
        
        if matdirs:
            print(f"  총 {len(matdirs)}개 원료배출량:")
            for matdir in matdirs:
                print(f"    - ID: {matdir['id']}, 공정ID: {matdir['process_id']}, 원료명: {matdir['mat_name']}, 배출량: {matdir['matdir_em']}")
        else:
            print("  ⚠️ 원료배출량 데이터가 없습니다.")
        
        # 7. fueldir 데이터 확인
        print("\n🔥 fueldir 테이블 데이터:")
        cursor.execute("SELECT id, process_id, fuel_name, fueldir_em FROM fueldir ORDER BY process_id")
        fueldirs = cursor.fetchall()
        
        if fueldirs:
            print(f"  총 {len(fueldirs)}개 연료배출량:")
            for fueldir in fueldirs:
                print(f"    - ID: {fueldir['id']}, 공정ID: {fueldir['process_id']}, 연료명: {fueldir['fuel_name']}, 배출량: {fueldir['fueldir_em']}")
        else:
            print("  ⚠️ 연료배출량 데이터가 없습니다.")
        
        # 8. process_attrdir_emission 데이터 확인
        print("\n📊 process_attrdir_emission 테이블 데이터:")
        cursor.execute("SELECT process_id, total_matdir_emission, total_fueldir_emission, attrdir_em FROM process_attrdir_emission ORDER BY process_id")
        emissions = cursor.fetchall()
        
        if emissions:
            print(f"  총 {len(emissions)}개 직접귀속배출량:")
            for emission in emissions:
                print(f"    - 공정ID: {emission['process_id']}, 원료배출량: {emission['total_matdir_emission']}, 연료배출량: {emission['total_fueldir_emission']}, 직접귀속배출량: {emission['attrdir_em']}")
        else:
            print("  ⚠️ 직접귀속배출량 데이터가 없습니다.")
        
        cursor.close()
        conn.close()
        
        print("\n✅ DB 상태 확인 완료!")
        
    except Exception as e:
        print(f"❌ DB 확인 중 오류 발생: {e}")

if __name__ == "__main__":
    check_db_status()
