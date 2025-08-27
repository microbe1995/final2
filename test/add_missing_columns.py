#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
누락된 컬럼 추가 스크립트
스키마와 일치하도록 누락된 컬럼들을 추가합니다.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# 환경변수에서 DB URL 가져오기
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def check_column_exists(conn, table_name, column_name):
    """컬럼 존재 여부 확인"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s 
                AND column_name = %s
            );
        """, (table_name, column_name))
        return cursor.fetchone()[0]

def add_missing_columns(conn):
    """누락된 컬럼들 추가"""
    print("🔄 누락된 컬럼들 추가 중...")
    
    # Install 테이블에 created_at, updated_at 추가
    if not check_column_exists(conn, 'install', 'created_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE install ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ install.created_at 컬럼 추가 완료")
    
    if not check_column_exists(conn, 'install', 'updated_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE install ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ install.updated_at 컬럼 추가 완료")
    
    # Product 테이블에 created_at, updated_at 추가
    if not check_column_exists(conn, 'product', 'created_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE product ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ product.created_at 컬럼 추가 완료")
    
    if not check_column_exists(conn, 'product', 'updated_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE product ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ product.updated_at 컬럼 추가 완료")
    
    # Process 테이블에 created_at, updated_at 추가
    if not check_column_exists(conn, 'process', 'created_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ process.created_at 컬럼 추가 완료")
    
    if not check_column_exists(conn, 'process', 'updated_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ process.updated_at 컬럼 추가 완료")
    
    # ProcessInput 테이블에 created_at, updated_at 추가
    if not check_column_exists(conn, 'process_input', 'created_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process_input ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ process_input.created_at 컬럼 추가 완료")
    
    if not check_column_exists(conn, 'process_input', 'updated_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE process_input ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ process_input.updated_at 컬럼 추가 완료")

def fix_edge_table(conn):
    """Edge 테이블 컬럼명 수정"""
    print("\n🔄 Edge 테이블 컬럼명 수정 중...")
    
    # source_node_id를 source_id로 변경
    if check_column_exists(conn, 'edge', 'source_node_id') and not check_column_exists(conn, 'edge', 'source_id'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE edge RENAME COLUMN source_node_id TO source_id;")
            print("✅ edge.source_node_id → edge.source_id 변경 완료")
    
    # target_node_id를 target_id로 변경
    if check_column_exists(conn, 'edge', 'target_node_id') and not check_column_exists(conn, 'edge', 'target_id'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE edge RENAME COLUMN target_node_id TO target_id;")
            print("✅ edge.target_node_id → edge.target_id 변경 완료")
    
    # kind를 edge_kind로 변경
    if check_column_exists(conn, 'edge', 'kind') and not check_column_exists(conn, 'edge', 'edge_kind'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE edge RENAME COLUMN kind TO edge_kind;")
            print("✅ edge.kind → edge.edge_kind 변경 완료")
    
    # created_at, updated_at 추가
    if not check_column_exists(conn, 'edge', 'created_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE edge ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ edge.created_at 컬럼 추가 완료")
    
    if not check_column_exists(conn, 'edge', 'updated_at'):
        with conn.cursor() as cursor:
            cursor.execute("ALTER TABLE edge ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
            print("✅ edge.updated_at 컬럼 추가 완료")

def verify_changes(conn):
    """변경사항 검증"""
    print("\n🔍 변경사항 검증 중...")
    
    tables = ['install', 'product', 'process', 'process_input', 'edge']
    
    for table in tables:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;", (table,))
            columns = [row['column_name'] for row in cursor.fetchall()]
            print(f"📋 {table} 테이블 컬럼: {columns}")

def main():
    """메인 함수"""
    print("🚀 누락된 컬럼 추가 시작")
    print("=" * 50)
    
    conn = connect_db()
    
    try:
        # 누락된 컬럼들 추가
        add_missing_columns(conn)
        
        # Edge 테이블 수정
        fix_edge_table(conn)
        
        # 변경사항 커밋
        conn.commit()
        print("\n✅ 모든 변경사항이 성공적으로 커밋되었습니다.")
        
        # 변경사항 검증
        verify_changes(conn)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    finally:
        conn.close()
    
    print("\n🎉 누락된 컬럼 추가 완료!")

if __name__ == "__main__":
    main()
