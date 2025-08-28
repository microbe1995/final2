#!/usr/bin/env python3
"""
HS 코드 데이터 확인 스크립트
"""

import psycopg2

# Railway PostgreSQL 데이터베이스 URL
DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def check_hs_data():
    """HS 코드 데이터 확인"""
    try:
        print("🔗 데이터베이스 연결 중...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 전체 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM hs_cn_mapping;")
        total_count = cursor.fetchone()[0]
        print(f"📊 전체 데이터 수: {total_count}개")
        
        # HS 코드 72로 시작하는 데이터 확인
        cursor.execute("SELECT DISTINCT hscode FROM hs_cn_mapping WHERE hscode LIKE '72%' ORDER BY hscode LIMIT 10;")
        hs_72_data = cursor.fetchall()
        print(f"\n🔍 HS 코드 72로 시작하는 데이터 ({len(hs_72_data)}개):")
        for row in hs_72_data:
            print(f"  {row[0]}")
        
        # HS 코드 길이별 분포 확인
        cursor.execute("SELECT LENGTH(hscode), COUNT(*) FROM hs_cn_mapping GROUP BY LENGTH(hscode) ORDER BY LENGTH(hscode);")
        length_dist = cursor.fetchall()
        print(f"\n📏 HS 코드 길이별 분포:")
        for length, count in length_dist:
            print(f"  {length}자리: {count}개")
        
        # 샘플 데이터 확인
        cursor.execute("SELECT hscode, cncode_total, goods_name FROM hs_cn_mapping LIMIT 5;")
        sample_data = cursor.fetchall()
        print(f"\n📋 샘플 데이터:")
        for row in sample_data:
            print(f"  HS: {row[0]}, CN: {row[1]}, 품목: {row[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_hs_data()
