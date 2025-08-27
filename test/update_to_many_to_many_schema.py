#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다대다 관계로 스키마 변경 스크립트
- product_process 중간 테이블 생성
- 기존 process 테이블의 product_id 제거
- 기존 데이터 마이그레이션
"""

import os
import sys
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 데이터베이스 연결 정보
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway')

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return None

def backup_existing_data(conn):
    """기존 데이터 백업"""
    try:
        cursor = conn.cursor()
        
        # process 테이블 백업
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS process_backup AS 
            SELECT * FROM process
        """)
        
        # product 테이블 백업
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_backup AS 
            SELECT * FROM product
        """)
        
        conn.commit()
        print("✅ 기존 데이터 백업 완료")
        return True
    except Exception as e:
        print(f"❌ 데이터 백업 실패: {e}")
        conn.rollback()
        return False

def create_product_process_table(conn):
    """product_process 중간 테이블 생성"""
    try:
        cursor = conn.cursor()
        
        # product_process 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_process (
                id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                process_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_id, process_id),
                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
                FOREIGN KEY (process_id) REFERENCES process(id) ON DELETE CASCADE
            )
        """)
        
        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_process_product_id 
            ON product_process(product_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_process_process_id 
            ON product_process(process_id)
        """)
        
        conn.commit()
        print("✅ product_process 테이블 생성 완료")
        return True
    except Exception as e:
        print(f"❌ product_process 테이블 생성 실패: {e}")
        conn.rollback()
        return False

def migrate_existing_data(conn):
    """기존 데이터를 다대다 관계로 마이그레이션"""
    try:
        cursor = conn.cursor()
        
        # 기존 process 테이블의 데이터를 product_process로 마이그레이션
        cursor.execute("""
            INSERT INTO product_process (product_id, process_id, created_at, updated_at)
            SELECT product_id, id, created_at, updated_at
            FROM process
            WHERE product_id IS NOT NULL
        """)
        
        # 마이그레이션된 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM product_process")
        count = cursor.fetchone()[0]
        print(f"✅ {count}개의 product-process 관계 마이그레이션 완료")
        
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 데이터 마이그레이션 실패: {e}")
        conn.rollback()
        return False

def update_process_table(conn):
    """process 테이블에서 product_id 컬럼 제거"""
    try:
        cursor = conn.cursor()
        
        # product_id 컬럼 제거
        cursor.execute("""
            ALTER TABLE process DROP COLUMN IF EXISTS product_id
        """)
        
        conn.commit()
        print("✅ process 테이블에서 product_id 컬럼 제거 완료")
        return True
    except Exception as e:
        print(f"❌ process 테이블 업데이트 실패: {e}")
        conn.rollback()
        return False

def verify_migration(conn):
    """마이그레이션 결과 검증"""
    try:
        cursor = conn.cursor()
        
        # product_process 테이블 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM product_process")
        product_process_count = cursor.fetchone()[0]
        
        # process 테이블 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM process")
        process_count = cursor.fetchone()[0]
        
        # product 테이블 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM product")
        product_count = cursor.fetchone()[0]
        
        print(f"📊 마이그레이션 결과:")
        print(f"   - product_process 관계: {product_process_count}개")
        print(f"   - process: {process_count}개")
        print(f"   - product: {product_count}개")
        
        # 샘플 데이터 확인
        cursor.execute("""
            SELECT p.product_name, pr.process_name, pp.created_at
            FROM product_process pp
            JOIN product p ON pp.product_id = p.id
            JOIN process pr ON pp.process_id = pr.id
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        print(f"📋 샘플 관계 데이터:")
        for sample in samples:
            print(f"   - {sample[0]} ←→ {sample[1]} ({sample[2]})")
        
        return True
    except Exception as e:
        print(f"❌ 마이그레이션 검증 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 다대다 관계 스키마 변경 시작")
    print("=" * 50)
    
    # 데이터베이스 연결
    conn = connect_db()
    if not conn:
        return False
    
    try:
        # 1. 기존 데이터 백업
        if not backup_existing_data(conn):
            return False
        
        # 2. product_process 테이블 생성
        if not create_product_process_table(conn):
            return False
        
        # 3. 기존 데이터 마이그레이션
        if not migrate_existing_data(conn):
            return False
        
        # 4. process 테이블 업데이트
        if not update_process_table(conn):
            return False
        
        # 5. 마이그레이션 결과 검증
        if not verify_migration(conn):
            return False
        
        print("=" * 50)
        print("🎉 다대다 관계 스키마 변경 완료!")
        print("📝 다음 단계:")
        print("   1. 백엔드 엔티티 업데이트")
        print("   2. API 엔드포인트 수정")
        print("   3. 프론트엔드 로직 수정")
        
        return True
        
    except Exception as e:
        print(f"❌ 스키마 변경 중 오류 발생: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
