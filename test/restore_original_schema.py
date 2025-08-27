#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from psycopg2.extras import RealDictCursor

def restore_original_schema():
    """스키마를 원래 컬럼명으로 되돌리기"""
    
    # Railway DB 연결
    conn = psycopg2.connect(
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    )
    cur = conn.cursor()
    
    try:
        print("🔧 스키마를 원래대로 복원 중...")
        
        # 1. install 테이블: install_name -> name
        print("📋 install 테이블 복원: install_name -> name")
        try:
            cur.execute("ALTER TABLE install RENAME COLUMN install_name TO name;")
            print("✅ install.install_name -> name 복원 완료")
        except Exception as e:
            print(f"⚠️ install 테이블 복원 실패: {e}")
        
        # 2. product 테이블: production_amount -> product_amount
        print("📋 product 테이블 복원: production_amount -> product_amount")
        try:
            cur.execute("ALTER TABLE product RENAME COLUMN production_amount TO product_amount;")
            print("✅ product.production_amount -> product_amount 복원 완료")
        except Exception as e:
            print(f"⚠️ product 테이블 복원 실패: {e}")
        
        # 3. product 테이블: sales_amount -> product_sell
        print("📋 product 테이블 복원: sales_amount -> product_sell")
        try:
            cur.execute("ALTER TABLE product RENAME COLUMN sales_amount TO product_sell;")
            print("✅ product.sales_amount -> product_sell 복원 완료")
        except Exception as e:
            print(f"⚠️ product 테이블 복원 실패: {e}")
        
        # 4. product 테이블: eu_sales_amount -> product_eusell
        print("📋 product 테이블 복원: eu_sales_amount -> product_eusell")
        try:
            cur.execute("ALTER TABLE product RENAME COLUMN eu_sales_amount TO product_eusell;")
            print("✅ product.eu_sales_amount -> product_eusell 복원 완료")
        except Exception as e:
            print(f"⚠️ product 테이블 복원 실패: {e}")
        
        # 5. process_input 테이블: material_name -> input_name
        print("📋 process_input 테이블 복원: material_name -> input_name")
        try:
            cur.execute("ALTER TABLE process_input RENAME COLUMN material_name TO input_name;")
            print("✅ process_input.material_name -> input_name 복원 완료")
        except Exception as e:
            print(f"⚠️ process_input 테이블 복원 실패: {e}")
        
        # 6. process_input 테이블: material_type -> input_type
        print("📋 process_input 테이블 복원: material_type -> input_type")
        try:
            cur.execute("ALTER TABLE process_input RENAME COLUMN material_type TO input_type;")
            print("✅ process_input.material_type -> input_type 복원 완료")
        except Exception as e:
            print(f"⚠️ process_input 테이블 복원 실패: {e}")
        
        # 7. process_input 테이블: material_amount -> amount
        print("📋 process_input 테이블 복원: material_amount -> amount")
        try:
            cur.execute("ALTER TABLE process_input RENAME COLUMN material_amount TO amount;")
            print("✅ process_input.material_amount -> amount 복원 완료")
        except Exception as e:
            print(f"⚠️ process_input 테이블 복원 실패: {e}")
        
        # 8. process_input 테이블: direct_emission -> direm_emission
        print("📋 process_input 테이블 복원: direct_emission -> direm_emission")
        try:
            cur.execute("ALTER TABLE process_input RENAME COLUMN direct_emission TO direm_emission;")
            print("✅ process_input.direct_emission -> direm_emission 복원 완료")
        except Exception as e:
            print(f"⚠️ process_input 테이블 복원 실패: {e}")
        
        # 9. process_input 테이블: indirect_emission -> indirem_emission
        print("📋 process_input 테이블 복원: indirect_emission -> indirem_emission")
        try:
            cur.execute("ALTER TABLE process_input RENAME COLUMN indirect_emission TO indirem_emission;")
            print("✅ process_input.indirect_emission -> indirem_emission 복원 완료")
        except Exception as e:
            print(f"⚠️ process_input 테이블 복원 실패: {e}")
        
        conn.commit()
        print("✅ 스키마 원래대로 복원 완료!")
        
        # 복원된 스키마 확인
        print("\n📋 복원된 스키마 구조:")
        print("=" * 60)
        
        tables_to_check = ['install', 'product', 'process', 'process_input']
        
        for table_name in tables_to_check:
            print(f"\n📋 {table_name} 테이블:")
            print("-" * 40)
            
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            if columns:
                print(f"{'컬럼명':<25} {'데이터타입':<20} {'NULL허용'}")
                print("-" * 50)
                for col in columns:
                    print(f"{col[0]:<25} {col[1]:<20} {col[2]}")
            else:
                print(f"❌ {table_name} 테이블이 존재하지 않습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    restore_original_schema()
