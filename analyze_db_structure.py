#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 데이터베이스 구조 분석 스크립트
CBAM 시스템의 테이블 구조와 데이터를 파악하여 배출량 계산 문제를 진단합니다.
"""

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import sys
from typing import Dict, List, Any

# 데이터베이스 연결 정보
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
        print("✅ 데이터베이스 연결 성공")
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def get_all_tables(conn) -> List[str]:
    """모든 테이블 목록 조회"""
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            return tables
    except Exception as e:
        print(f"❌ 테이블 목록 조회 실패: {e}")
        return []

def get_table_structure(conn, table_name: str) -> List[Dict[str, Any]]:
    """테이블 구조 조회"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cursor.fetchall()
            return [dict(col) for col in columns]
    except Exception as e:
        print(f"❌ 테이블 {table_name} 구조 조회 실패: {e}")
        return []

def get_table_data_count(conn, table_name: str) -> int:
    """테이블 데이터 개수 조회"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        print(f"❌ 테이블 {table_name} 데이터 개수 조회 실패: {e}")
        return 0

def get_sample_data(conn, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """테이블 샘플 데이터 조회"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ 테이블 {table_name} 샘플 데이터 조회 실패: {e}")
        return []

def analyze_emission_tables(conn):
    """배출량 관련 테이블 분석"""
    print("\n" + "="*80)
    print("🔥 배출량 관련 테이블 분석")
    print("="*80)
    
    emission_tables = [
        'matdir', 'fueldir', 'process_attrdir_emission',
        'sourcestream', 'process_chain', 'process_chain_link'
    ]
    
    for table_name in emission_tables:
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
                exists = cursor.fetchone()[0]
                
                if exists:
                    count = get_table_data_count(conn, table_name)
                    print(f"\n📊 테이블: {table_name}")
                    print(f"   데이터 개수: {count}")
                    
                    if count > 0:
                        # 테이블 구조 조회
                        columns = get_table_structure(conn, table_name)
                        print(f"   컬럼 구조:")
                        for col in columns:
                            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                            print(f"     - {col['column_name']}: {col['data_type']} {nullable}{default}")
                        
                        # 샘플 데이터 조회
                        if count <= 10:
                            sample_data = get_sample_data(conn, table_name, count)
                            print(f"   전체 데이터:")
                            for i, row in enumerate(sample_data, 1):
                                print(f"     {i}. {row}")
                        else:
                            sample_data = get_sample_data(conn, table_name, 3)
                            print(f"   샘플 데이터 (처음 3개):")
                            for i, row in enumerate(sample_data, 1):
                                print(f"     {i}. {row}")
                else:
                    print(f"\n❌ 테이블 {table_name}이 존재하지 않습니다.")
                    
        except Exception as e:
            print(f"❌ 테이블 {table_name} 분석 중 오류: {e}")

def analyze_process_chain_data(conn):
    """통합 공정 그룹 데이터 분석"""
    print("\n" + "="*80)
    print("🔗 통합 공정 그룹 데이터 분석")
    print("="*80)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # process_chain 테이블 확인
            cursor.execute("""
                SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'process_chain')
            """)
            chain_exists = cursor.fetchone()['exists']
            
            if chain_exists:
                # process_chain 데이터 조회
                cursor.execute("SELECT * FROM process_chain ORDER BY id")
                chains = cursor.fetchall()
                print(f"\n📋 통합 공정 그룹 (process_chain): {len(chains)}개")
                
                for chain in chains:
                    print(f"   그룹 ID: {chain['id']}")
                    print(f"   그룹명: {chain['chain_name']}")
                    print(f"   시작공정: {chain['start_process_id']}")
                    print(f"   종료공정: {chain['end_process_id']}")
                    print(f"   활성상태: {chain['is_active']}")
                    
                    # 해당 그룹의 링크 조회
                    cursor.execute("""
                        SELECT * FROM process_chain_link 
                        WHERE chain_id = %s 
                        ORDER BY sequence_order
                    """, (chain['id'],))
                    links = cursor.fetchall()
                    print(f"   연결된 공정: {len(links)}개")
                    for link in links:
                        print(f"     - 공정 ID: {link['process_id']}, 순서: {link['sequence_order']}")
                    print()
            else:
                print("❌ process_chain 테이블이 존재하지 않습니다.")
                
    except Exception as e:
        print(f"❌ 통합 공정 그룹 분석 중 오류: {e}")

def check_emission_calculation_data(conn):
    """배출량 계산 데이터 확인"""
    print("\n" + "="*80)
    print("📊 배출량 계산 데이터 확인")
    print("="*80)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # process_attrdir_emission 테이블 확인
            cursor.execute("""
                SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'process_attrdir_emission')
            """)
            emission_exists = cursor.fetchone()['exists']
            
            if emission_exists:
                # 배출량 데이터 조회
                cursor.execute("""
                    SELECT 
                        process_id,
                        total_matdir_emission,
                        total_fueldir_emission,
                        attrdir_em,
                        calculation_date
                    FROM process_attrdir_emission 
                    ORDER BY process_id
                """)
                emissions = cursor.fetchall()
                
                print(f"\n🔥 공정별 배출량 데이터: {len(emissions)}개")
                for emission in emissions:
                    print(f"   공정 ID: {emission['process_id']}")
                    print(f"     원자재 배출량: {emission['total_matdir_emission']}")
                    print(f"     연료 배출량: {emission['total_fueldir_emission']}")
                    print(f"     총 배출량: {emission['attrdir_em']}")
                    print(f"     계산일시: {emission['calculation_date']}")
                    print()
            else:
                print("❌ process_attrdir_emission 테이블이 존재하지 않습니다.")
                
    except Exception as e:
        print(f"❌ 배출량 계산 데이터 확인 중 오류: {e}")

def main():
    """메인 함수"""
    print("🚀 CBAM 데이터베이스 구조 분석 시작")
    print("="*80)
    
    # 데이터베이스 연결
    conn = connect_db()
    
    try:
        # 1. 모든 테이블 목록 조회
        print("\n📋 데이터베이스 테이블 목록")
        print("-" * 50)
        tables = get_all_tables(conn)
        for i, table in enumerate(tables, 1):
            print(f"{i:2d}. {table}")
        
        # 2. 배출량 관련 테이블 분석
        analyze_emission_tables(conn)
        
        # 3. 통합 공정 그룹 데이터 분석
        analyze_process_chain_data(conn)
        
        # 4. 배출량 계산 데이터 확인
        check_emission_calculation_data(conn)
        
        print("\n" + "="*80)
        print("✅ 데이터베이스 구조 분석 완료")
        print("="*80)
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {e}")
    finally:
        conn.close()
        print("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
