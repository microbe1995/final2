#!/usr/bin/env python3
"""
productionroute 테이블 삭제 스크립트
"""

import psycopg2
import os

def drop_table():
    """productionroute 테이블 삭제"""
    
    # Railway PostgreSQL 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ 데이터베이스 연결 성공")
        
        # productionroute 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS productionroute;")
        print("✅ productionroute 테이블 삭제 완료")
        
        # 삭제 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'productionroute'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("✅ productionroute 테이블 삭제 확인 완료")
        else:
            print("❌ productionroute 테이블 삭제 실패")
        
        cursor.close()
        conn.close()
        print("✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 productionroute 테이블 삭제 시작...")
    drop_table()
    print("🏁 작업 완료")
