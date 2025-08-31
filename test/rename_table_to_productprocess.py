#!/usr/bin/env python3
"""
productionroute 테이블을 productprocess로 이름 변경 스크립트
"""

import psycopg2
import os

def rename_table():
    """productionroute 테이블을 productprocess로 이름 변경"""
    
    # Railway PostgreSQL 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ 데이터베이스 연결 성공")
        
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'productionroute'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("📋 productionroute 테이블 발견")
            
            # 테이블 이름 변경
            cursor.execute('ALTER TABLE productionroute RENAME TO product_process;')
            print("✅ 테이블 이름 변경 완료: productionroute → product_process")
            
            # 변경 확인
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'product_process'
                );
            """)
            
            new_table_exists = cursor.fetchone()[0]
            
            if new_table_exists:
                print("✅ product_process 테이블 확인 완료")
            else:
                print("❌ 테이블 이름 변경 실패")
                
        else:
            print("⚠️ productionroute 테이블이 존재하지 않습니다")
            
            # product_process 테이블이 이미 존재하는지 확인
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'product_process'
                );
            """)
            
            new_table_exists = cursor.fetchone()[0]
            
            if new_table_exists:
                print("✅ product_process 테이블이 이미 존재합니다")
            else:
                print("❌ productionroute 테이블도 없고 product_process 테이블도 없습니다")
        
        cursor.close()
        conn.close()
        print("✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 productionroute 테이블 이름 변경 시작...")
    rename_table()
    print("🏁 작업 완료")
