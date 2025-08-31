#!/usr/bin/env python3
"""
product_process와 productionroute 테이블 상태 확인 스크립트
"""

import psycopg2
import os

def check_tables():
    """테이블 상태 확인"""
    
    # Railway PostgreSQL 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ 데이터베이스 연결 성공")
        
        # productionroute 테이블 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'productionroute'
            );
        """)
        
        productionroute_exists = cursor.fetchone()[0]
        
        # product_process 테이블 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'product_process'
            );
        """)
        
        product_process_exists = cursor.fetchone()[0]
        
        print(f"📋 productionroute 테이블 존재: {productionroute_exists}")
        print(f"📋 product_process 테이블 존재: {product_process_exists}")
        
        if productionroute_exists and product_process_exists:
            print("⚠️ 두 테이블이 모두 존재합니다. productionroute를 삭제해야 합니다.")
        elif productionroute_exists:
            print("✅ productionroute 테이블만 존재합니다.")
        elif product_process_exists:
            print("✅ product_process 테이블만 존재합니다.")
        else:
            print("❌ 두 테이블 모두 존재하지 않습니다.")
        
        cursor.close()
        conn.close()
        print("✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 테이블 상태 확인 시작...")
    check_tables()
    print("🏁 작업 완료")
