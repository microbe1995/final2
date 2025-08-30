#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HS-CN 매핑 테이블 상태 확인 스크립트
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_mapping_table():
    """HS-CN 매핑 테이블 상태 확인"""
    
    # Railway DB 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    print("🔍 HS-CN 매핑 테이블 상태 확인 시작...")
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 1. hs_cn_mapping 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hs_cn_mapping'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ hs_cn_mapping 테이블이 존재하지 않습니다.")
            return
        
        print("✅ hs_cn_mapping 테이블 존재 확인")
        
        # 2. 테이블 구조 확인
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'hs_cn_mapping'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 테이블 구조:")
        for col in columns:
            print(f"   📝 {col[0]} ({col[1]}) - NULL 허용: {col[2]}")
        
        # 3. 데이터 개수 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping")
        total_count = cursor.fetchone()[0]
        print(f"\n📊 총 매핑 데이터 수: {total_count}개")
        
        if total_count == 0:
            print("⚠️ 테이블에 데이터가 없습니다!")
            return
        
        # 4. HS 코드 샘플 데이터 확인
        cursor.execute("""
            SELECT DISTINCT hscode, COUNT(*) as count
            FROM hs_cn_mapping 
            GROUP BY hscode 
            ORDER BY hscode 
            LIMIT 10;
        """)
        
        hs_samples = cursor.fetchall()
        print(f"\n🔍 HS 코드 샘플 (상위 10개):")
        for hs_code, count in hs_samples:
            print(f"   📝 {hs_code}: {count}개 매핑")
        
        # 5. CN 코드 샘플 데이터 확인
        cursor.execute("""
            SELECT DISTINCT cncode_total, COUNT(*) as count
            FROM hs_cn_mapping 
            GROUP BY cncode_total 
            ORDER BY cncode_total 
            LIMIT 10;
        """)
        
        cn_samples = cursor.fetchall()
        print(f"\n🔍 CN 코드 샘플 (상위 10개):")
        for cn_code, count in cn_samples:
            print(f"   📝 {cn_code}: {count}개 매핑")
        
        # 6. 특정 HS 코드로 테스트 검색
        test_hs_codes = ["72", "720", "7208", "720851"]
        print(f"\n🧪 테스트 검색 결과:")
        
        for test_hs in test_hs_codes:
            cursor.execute("""
                SELECT hscode, cncode_total, goods_name
                FROM hs_cn_mapping 
                WHERE hscode LIKE %s
                LIMIT 3;
            """, (f"{test_hs}%",))
            
            results = cursor.fetchall()
            print(f"   🔍 HS 코드 '{test_hs}' 검색 결과: {len(results)}개")
            
            for result in results:
                print(f"      📝 {result[0]} → {result[1]} ({result[2]})")
        
        # 7. 데이터 품질 확인
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN hscode IS NULL OR hscode = '' THEN 1 END) as null_hs,
                COUNT(CASE WHEN cncode_total IS NULL OR cncode_total = '' THEN 1 END) as null_cn,
                COUNT(CASE WHEN goods_name IS NULL OR goods_name = '' THEN 1 END) as null_name
            FROM hs_cn_mapping;
        """)
        
        quality_stats = cursor.fetchone()
        print(f"\n📊 데이터 품질 통계:")
        print(f"   📝 총 데이터: {quality_stats[0]}개")
        print(f"   ❌ HS 코드 누락: {quality_stats[1]}개")
        print(f"   ❌ CN 코드 누락: {quality_stats[2]}개")
        print(f"   ❌ 품목명 누락: {quality_stats[3]}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()
            print("\n🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    check_mapping_table()
