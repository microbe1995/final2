#!/usr/bin/env python3
"""
간단한 날짜 형식 테스트
"""

import asyncio
import asyncpg

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_simple():
    """간단한 테스트"""
    print("🔍 간단한 날짜 형식 테스트")
    print("=" * 40)
    
    try:
        # 데이터베이스 연결
        print("🔌 Railway DB 연결 시도...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 전체 제품명 개수
        print("\n📊 1. 전체 제품명 개수")
        count_query = "SELECT COUNT(DISTINCT 생산품명) FROM dummy WHERE 생산품명 IS NOT NULL;"
        count = await conn.fetchval(count_query)
        print(f"   전체 고유 제품명 개수: {count}")
        
        # 2. 8월 데이터 개수
        print("\n📅 2. 8월 데이터 개수")
        august_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM dummy 
            WHERE 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-31'::DATE;
        """)
        print(f"   8월 투입일 데이터 개수: {august_count}")
        
        # 3. 기간별 제품명 테스트 (간단한 버전)
        print("\n🔍 3. 기간별 제품명 테스트 (간단한 버전)")
        
        # 투입일이 8월인 제품들
        input_august = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL
            AND 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-31'::DATE
            ORDER BY 생산품명;
        """)
        
        input_names = [row['생산품명'] for row in input_august]
        print(f"   투입일이 8월인 제품명: {len(input_names)}개")
        for name in input_names:
            print(f"     - {name}")
        
        # 종료일이 9월인 제품들
        end_september = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL
            AND 종료일 >= '2025-09-01'::DATE 
            AND 종료일 <= '2025-09-30'::DATE
            ORDER BY 생산품명;
        """)
        
        end_names = [row['생산품명'] for row in end_september]
        print(f"   종료일이 9월인 제품명: {len(end_names)}개")
        for name in end_names:
            print(f"     - {name}")
        
        # 4. 합집합으로 고유 제품명 찾기
        all_names = list(set(input_names + end_names))
        print(f"\n📋 4. 합집합 결과")
        print(f"   총 고유 제품명: {len(all_names)}개")
        for name in sorted(all_names):
            print(f"     - {name}")
        
        await conn.close()
        print("\n✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())
