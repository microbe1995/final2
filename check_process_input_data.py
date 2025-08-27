#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Railway DB 연결 정보
DATABASE_URL = os.getenv('DATABASE_URL')

def check_process_input_table():
    """process_input 테이블 구조와 데이터 확인"""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return
    
    try:
        # DB 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 process_input 테이블 구조 확인 중...")
        
        # 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'process_input'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        if not columns:
            print("❌ process_input 테이블이 존재하지 않습니다.")
            return
        
        print("📋 process_input 테이블 구조:")
        print("-" * 80)
        print(f"{'컬럼명':<20} {'데이터타입':<15} {'NULL허용':<10} {'기본값'}")
        print("-" * 80)
        
        for col in columns:
            print(f"{col['column_name']:<20} {col['data_type']:<15} {col['is_nullable']:<10} {col['column_default'] or 'NULL'}")
        
        print("\n🔍 process_input 테이블 데이터 확인 중...")
        
        # 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) as count FROM process_input")
        count_result = cursor.fetchone()
        count = count_result['count'] if count_result else 0
        
        print(f"📊 현재 process_input 테이블에 {count}개의 레코드가 있습니다.")
        
        if count > 0:
            # 실제 데이터 확인
            cursor.execute("""
                SELECT pi.*, p.process_name, pr.product_name
                FROM process_input pi
                LEFT JOIN process p ON pi.process_id = p.id
                LEFT JOIN product pr ON p.product_id = pr.id
                ORDER BY pi.id
                LIMIT 10
            """)
            
            data = cursor.fetchall()
            
            print("\n📋 현재 데이터 (최대 10개):")
            print("-" * 120)
            print(f"{'ID':<4} {'프로세스ID':<8} {'입력타입':<12} {'입력명':<20} {'수량':<10} {'배출계수':<10} {'산화계수':<10} {'직접배출':<10} {'간접배출':<10} {'프로세스명':<15} {'제품명':<15}")
            print("-" * 120)
            
            for row in data:
                print(f"{row['id']:<4} {row['process_id']:<8} {row['input_type']:<12} {row['input_name'][:18]:<20} {row['amount']:<10.2f} {row['factor'] or 0:<10.2f} {row['oxy_factor'] or 0:<10.2f} {row['direm_emission'] or 0:<10.2f} {row['indirem_emission'] or 0:<10.2f} {row['process_name'][:13]:<15} {row['product_name'][:13]:<15}")
        
        # process 테이블과의 관계 확인
        print("\n🔍 process 테이블 확인...")
        cursor.execute("SELECT COUNT(*) as count FROM process")
        process_count = cursor.fetchone()['count']
        print(f"📊 process 테이블에 {process_count}개의 레코드가 있습니다.")
        
        if process_count > 0:
            cursor.execute("""
                SELECT p.id, p.process_name, pr.product_name, 
                       COUNT(pi.id) as input_count
                FROM process p
                LEFT JOIN product pr ON p.product_id = pr.id
                LEFT JOIN process_input pi ON p.id = pi.process_id
                GROUP BY p.id, p.process_name, pr.product_name
                ORDER BY p.id
            """)
            
            processes = cursor.fetchall()
            
            print("\n📋 프로세스별 입력 데이터 현황:")
            print("-" * 80)
            print(f"{'프로세스ID':<10} {'프로세스명':<20} {'제품명':<15} {'입력데이터수'}")
            print("-" * 80)
            
            for proc in processes:
                print(f"{proc['id']:<10} {proc['process_name'][:18]:<20} {proc['product_name'][:13]:<15} {proc['input_count']}")
        
        conn.close()
        print("\n✅ process_input 테이블 확인 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_process_input_table()
