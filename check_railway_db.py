#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL DB 테이블 구조 확인 스크립트
실제 DB에 어떤 테이블들이 존재하는지 파악
"""

import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
import sys

# Railway PostgreSQL 연결 정보
DB_CONFIG = {
    'host': 'shortline.proxy.rlwy.net',
    'port': 46071,
    'database': 'railway',
    'user': 'postgres',
    'password': 'eQGfytQNhXYAZxsJYlFhYagpJAgstrni'
}

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Railway PostgreSQL 연결 성공!")
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return None

def get_all_tables(conn):
    """모든 테이블 목록 조회"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            print("\n📋 Railway DB에 존재하는 모든 테이블:")
            print("=" * 60)
            for table_name, table_type in tables:
                print(f"  {table_name:<30} ({table_type})")
            
            return [table[0] for table in tables if table[1] == 'BASE TABLE']
            
    except Exception as e:
        print(f"❌ 테이블 목록 조회 실패: {e}")
        return []

def get_table_structure(conn, table_name):
    """특정 테이블의 구조 조회"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            print(f"\n🏗️ 테이블 구조: {table_name}")
            print("-" * 60)
            print(f"{'컬럼명':<20} {'데이터타입':<20} {'NULL':<8} {'기본값'}")
            print("-" * 60)
            
            for col_name, data_type, is_nullable, default in columns:
                nullable = "YES" if is_nullable == "YES" else "NO"
                default_val = str(default) if default else ""
                print(f"{col_name:<20} {data_type:<20} {nullable:<8} {default_val}")
            
            return columns
            
    except Exception as e:
        print(f"❌ 테이블 구조 조회 실패: {e}")
        return []

def get_table_data_sample(conn, table_name, limit=5):
    """테이블 데이터 샘플 조회"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            
            if rows:
                print(f"\n📊 테이블 데이터 샘플: {table_name} (최대 {limit}행)")
                print("-" * 60)
                
                # DataFrame으로 변환하여 보기 좋게 출력
                df = pd.DataFrame(rows)
                print(df.to_string(index=False))
            else:
                print(f"\n📊 테이블 {table_name}에 데이터가 없습니다.")
                
    except Exception as e:
        print(f"❌ 테이블 데이터 조회 실패: {e}")

def check_material_fuel_tables(conn):
    """Material/Fuel 관련 테이블 특별 확인"""
    print("\n🔍 Material/Fuel 관련 테이블 상세 분석")
    print("=" * 60)
    
    # Material 관련 테이블들
    material_tables = ['materials', 'material_master', 'matdir']
    fuel_tables = ['fuels', 'fuel_master', 'fueldir']
    
    print("\n📦 Material 관련 테이블:")
    for table in material_tables:
        if table in get_all_tables(conn):
            print(f"  ✅ {table} 테이블 존재")
            get_table_structure(conn, table)
            get_table_data_sample(conn, table, 3)
        else:
            print(f"  ❌ {table} 테이블 없음")
    
    print("\n⛽ Fuel 관련 테이블:")
    for table in fuel_tables:
        if table in get_all_tables(conn):
            print(f"  ✅ {table} 테이블 존재")
            get_table_structure(conn, table)
            get_table_data_sample(conn, table, 3)
        else:
            print(f"  ❌ {table} 테이블 없음")

def main():
    """메인 함수"""
    print("🚀 Railway PostgreSQL DB 테이블 구조 확인 시작")
    print("=" * 60)
    
    # DB 연결
    conn = connect_db()
    if not conn:
        sys.exit(1)
    
    try:
        # 1. 모든 테이블 목록 조회
        tables = get_all_tables(conn)
        
        # 2. Material/Fuel 관련 테이블 상세 분석
        check_material_fuel_tables(conn)
        
        # 3. 사용자 선택으로 특정 테이블 상세 조회
        print("\n🔍 특정 테이블 상세 조회 (종료하려면 'quit' 입력)")
        while True:
            table_name = input("\n테이블명 입력 (또는 'quit'): ").strip()
            if table_name.lower() == 'quit':
                break
            
            if table_name in tables:
                get_table_structure(conn, table_name)
                get_table_data_sample(conn, table_name, 5)
            else:
                print(f"❌ 테이블 '{table_name}'을 찾을 수 없습니다.")
                print(f"사용 가능한 테이블: {', '.join(tables)}")
    
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        if conn:
            conn.close()
            print("\n✅ 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
