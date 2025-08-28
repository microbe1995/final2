#!/usr/bin/env python3
"""
HS-CN 매핑 테이블 생성 스크립트
Railway PostgreSQL 데이터베이스에 hs_cn_mapping 테이블을 생성합니다.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def get_database_url():
    """데이터베이스 URL 가져오기"""
    # Railway 환경변수 확인
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # 로컬 환경변수 확인
        database_url = os.getenv("RAILWAY_DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL 환경변수를 찾을 수 없습니다.")
        print("다음 중 하나를 설정해주세요:")
        print("1. DATABASE_URL")
        print("2. RAILWAY_DATABASE_URL")
        return None
    
    return database_url

def create_hs_cn_mapping_table():
    """HS-CN 매핑 테이블 생성"""
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        # 데이터베이스 연결
        print("🔗 데이터베이스에 연결 중...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'hs_cn_mapping'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("⚠️  hs_cn_mapping 테이블이 이미 존재합니다.")
            response = input("테이블을 삭제하고 다시 생성하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                print("❌ 테이블 생성이 취소되었습니다.")
                return False
            
            cursor.execute("DROP TABLE hs_cn_mapping;")
            print("🗑️  기존 테이블을 삭제했습니다.")
        
        # 테이블 생성
        print("📋 hs_cn_mapping 테이블을 생성 중...")
        cursor.execute("""
            CREATE TABLE hs_cn_mapping (
                id SERIAL PRIMARY KEY,
                hscode CHAR(6) NOT NULL,            -- HS 코드 (앞 6자리)
                aggregoods_name TEXT,               -- 품목군명
                aggregoods_engname TEXT,            -- 품목군영문명
                cncode_total CHAR(8) NOT NULL,      -- CN 코드 (8자리)
                goods_name TEXT,                    -- 품목명
                goods_engname TEXT                  -- 품목영문명
            );
        """)
        
        # 인덱스 생성 (성능 최적화)
        print("🔍 인덱스를 생성 중...")
        cursor.execute("""
            CREATE INDEX idx_hs_cn_mapping_hscode ON hs_cn_mapping(hscode);
        """)
        
        cursor.execute("""
            CREATE INDEX idx_hs_cn_mapping_cncode ON hs_cn_mapping(cncode_total);
        """)
        
        # 변경사항 커밋
        conn.commit()
        print("✅ hs_cn_mapping 테이블이 성공적으로 생성되었습니다!")
        
        # 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'hs_cn_mapping'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📊 테이블 구조:")
        print("-" * 80)
        print(f"{'컬럼명':<20} {'데이터타입':<15} {'NULL허용':<10} {'기본값'}")
        print("-" * 80)
        for col in columns:
            print(f"{col[0]:<20} {col[1]:<15} {col[2]:<10} {col[3] or 'None'}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ 데이터베이스 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 HS-CN 매핑 테이블 생성 스크립트")
    print("=" * 50)
    
    success = create_hs_cn_mapping_table()
    
    if success:
        print("\n🎉 테이블 생성이 완료되었습니다!")
        print("\n📝 다음 단계:")
        print("1. HS-CN 매핑 데이터를 테이블에 삽입")
        print("2. product 테이블의 product_cncode 필드와 연결")
        print("3. CBAM 계산 로직에서 CN 코드 기반 분류 활용")
    else:
        print("\n❌ 테이블 생성에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
