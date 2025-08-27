#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Railway DB 스키마 호환성 검사 스크립트
현재 DB 테이블 구조와 스키마 정의를 비교하여 불일치 부분을 찾습니다.
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

def get_all_tables(conn):
    """모든 테이블 목록 조회"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        return [row[0] for row in cursor.fetchall()]

def get_table_columns(conn, table_name):
    """테이블의 컬럼 정보 조회"""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        return cursor.fetchall()

def get_table_constraints(conn, table_name):
    """테이블의 제약조건 조회"""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT 
                constraint_name,
                constraint_type,
                column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage ccu 
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_schema = 'public' 
            AND tc.table_name = %s
            ORDER BY constraint_type, column_name;
        """, (table_name,))
        return cursor.fetchall()

def check_install_table(conn):
    """Install 테이블 스키마 검사"""
    print("\n🏭 Install 테이블 검사")
    print("-" * 40)
    
    if not get_all_tables(conn):
        print("❌ install 테이블이 존재하지 않습니다.")
        return False
    
    columns = get_table_columns(conn, 'install')
    print("📋 현재 컬럼:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 예상 컬럼
    expected_columns = {
        'id': 'integer',
        'install_name': 'text',  # name → install_name으로 변경됨
        'reporting_year': 'integer',
        'created_at': 'timestamp',
        'updated_at': 'timestamp'
    }
    
    print("\n🔍 스키마 비교:")
    current_cols = {col['column_name']: col['data_type'] for col in columns}
    
    for expected_col, expected_type in expected_columns.items():
        if expected_col in current_cols:
            if current_cols[expected_col] != expected_type:
                print(f"  ⚠️ {expected_col}: 예상 {expected_type}, 실제 {current_cols[expected_col]}")
            else:
                print(f"  ✅ {expected_col}: {expected_type}")
        else:
            print(f"  ❌ {expected_col}: 누락됨")
    
    return True

def check_product_table(conn):
    """Product 테이블 스키마 검사"""
    print("\n📦 Product 테이블 검사")
    print("-" * 40)
    
    if 'product' not in get_all_tables(conn):
        print("❌ product 테이블이 존재하지 않습니다.")
        return False
    
    columns = get_table_columns(conn, 'product')
    print("📋 현재 컬럼:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 예상 컬럼
    expected_columns = {
        'id': 'integer',
        'install_id': 'integer',
        'product_name': 'text',
        'product_category': 'text',
        'prostart_period': 'date',
        'proend_period': 'date',
        'product_amount': 'numeric',
        'product_cncode': 'text',
        'goods_name': 'text',
        'aggrgoods_name': 'text',
        'product_sell': 'numeric',
        'product_eusell': 'numeric',
        'created_at': 'timestamp',
        'updated_at': 'timestamp'
    }
    
    print("\n🔍 스키마 비교:")
    current_cols = {col['column_name']: col['data_type'] for col in columns}
    
    for expected_col, expected_type in expected_columns.items():
        if expected_col in current_cols:
            if current_cols[expected_col] != expected_type:
                print(f"  ⚠️ {expected_col}: 예상 {expected_type}, 실제 {current_cols[expected_col]}")
            else:
                print(f"  ✅ {expected_col}: {expected_type}")
        else:
            print(f"  ❌ {expected_col}: 누락됨")
    
    return True

def check_process_table(conn):
    """Process 테이블 스키마 검사"""
    print("\n🔄 Process 테이블 검사")
    print("-" * 40)
    
    if 'process' not in get_all_tables(conn):
        print("❌ process 테이블이 존재하지 않습니다.")
        return False
    
    columns = get_table_columns(conn, 'process')
    print("📋 현재 컬럼:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 예상 컬럼
    expected_columns = {
        'id': 'integer',
        'product_id': 'integer',
        'process_name': 'text',
        'start_period': 'date',
        'end_period': 'date',
        'created_at': 'timestamp',
        'updated_at': 'timestamp'
    }
    
    print("\n🔍 스키마 비교:")
    current_cols = {col['column_name']: col['data_type'] for col in columns}
    
    for expected_col, expected_type in expected_columns.items():
        if expected_col in current_cols:
            if current_cols[expected_col] != expected_type:
                print(f"  ⚠️ {expected_col}: 예상 {expected_type}, 실제 {current_cols[expected_col]}")
            else:
                print(f"  ✅ {expected_col}: {expected_type}")
        else:
            print(f"  ❌ {expected_col}: 누락됨")
    
    return True

def check_process_input_table(conn):
    """ProcessInput 테이블 스키마 검사"""
    print("\n📥 ProcessInput 테이블 검사")
    print("-" * 40)
    
    if 'process_input' not in get_all_tables(conn):
        print("❌ process_input 테이블이 존재하지 않습니다.")
        return False
    
    columns = get_table_columns(conn, 'process_input')
    print("📋 현재 컬럼:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 예상 컬럼 (업데이트된 스키마)
    expected_columns = {
        'id': 'integer',
        'process_id': 'integer',
        'input_type': 'text',
        'input_name': 'text',
        'input_amount': 'numeric',  # amount → input_amount로 변경됨
        'factor': 'numeric',
        'oxy_factor': 'numeric',
        'direm': 'numeric',  # direm_emission → direm으로 변경됨
        'indirem': 'numeric',  # indirem_emission → indirem으로 변경됨
        'created_at': 'timestamp',
        'updated_at': 'timestamp'
    }
    
    print("\n🔍 스키마 비교:")
    current_cols = {col['column_name']: col['data_type'] for col in columns}
    
    for expected_col, expected_type in expected_columns.items():
        if expected_col in current_cols:
            if current_cols[expected_col] != expected_type:
                print(f"  ⚠️ {expected_col}: 예상 {expected_type}, 실제 {current_cols[expected_col]}")
            else:
                print(f"  ✅ {expected_col}: {expected_type}")
        else:
            print(f"  ❌ {expected_col}: 누락됨")
    
    # 추가 컬럼 확인
    print("\n🔍 추가 컬럼:")
    for col in columns:
        if col['column_name'] not in expected_columns:
            print(f"  ℹ️ {col['column_name']}: {col['data_type']} (스키마에 정의되지 않음)")
    
    return True

def check_edge_table(conn):
    """Edge 테이블 스키마 검사"""
    print("\n🔗 Edge 테이블 검사")
    print("-" * 40)
    
    if 'edge' not in get_all_tables(conn):
        print("❌ edge 테이블이 존재하지 않습니다.")
        return False
    
    columns = get_table_columns(conn, 'edge')
    print("📋 현재 컬럼:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
    
    # 예상 컬럼
    expected_columns = {
        'id': 'integer',
        'source_id': 'integer',
        'target_id': 'integer',
        'edge_kind': 'text',
        'created_at': 'timestamp',
        'updated_at': 'timestamp'
    }
    
    print("\n🔍 스키마 비교:")
    current_cols = {col['column_name']: col['data_type'] for col in columns}
    
    for expected_col, expected_type in expected_columns.items():
        if expected_col in current_cols:
            if current_cols[expected_col] != expected_type:
                print(f"  ⚠️ {expected_col}: 예상 {expected_type}, 실제 {current_cols[expected_col]}")
            else:
                print(f"  ✅ {expected_col}: {expected_type}")
        else:
            print(f"  ❌ {expected_col}: 누락됨")
    
    return True

def check_other_tables(conn):
    """기타 테이블 확인"""
    print("\n🔍 기타 테이블 확인")
    print("-" * 40)
    
    all_tables = get_all_tables(conn)
    expected_tables = ['install', 'product', 'process', 'process_input', 'edge']
    
    other_tables = [table for table in all_tables if table not in expected_tables]
    
    if other_tables:
        print("📋 스키마에 정의되지 않은 테이블들:")
        for table in other_tables:
            print(f"  - {table}")
            columns = get_table_columns(conn, table)
            for col in columns:
                print(f"    └─ {col['column_name']}: {col['data_type']}")
    else:
        print("✅ 스키마에 정의되지 않은 테이블이 없습니다.")

def main():
    """메인 함수"""
    print("🚀 Railway DB 스키마 호환성 검사 시작")
    print("=" * 60)
    
    conn = connect_db()
    
    try:
        # 각 테이블별 검사
        check_install_table(conn)
        check_product_table(conn)
        check_process_table(conn)
        check_process_input_table(conn)
        check_edge_table(conn)
        
        # 기타 테이블 확인
        check_other_tables(conn)
        
        print("\n" + "=" * 60)
        print("🎉 스키마 호환성 검사 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
