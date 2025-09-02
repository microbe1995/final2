#!/usr/bin/env python3
"""
최종 수정된 쿼리 테스트
"""

import asyncio
import asyncpg

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

# 테스트할 기간
START_DATE = "2025-08-01"
END_DATE = "2025-09-09"

async def test_final_query():
    """최종 수정된 쿼리 테스트"""
    print("🔍 최종 수정된 기간별 제품명 쿼리 테스트")
    print(f"📅 테스트 기간: {START_DATE} ~ {END_DATE}")
    print("=" * 50)
    
    try:
        # 데이터베이스 연결
        print("🔌 Railway DB 연결 시도...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 기존 쿼리 테스트 (잘못된 로직)
        print("\n❌ 1. 기존 쿼리 테스트 (잘못된 로직)")
        old_query = """
        SELECT DISTINCT 생산품명 
        FROM dummy 
        WHERE 생산품명 IS NOT NULL
        AND 투입일 >= $1::DATE 
        AND 종료일 <= $2::DATE 
        ORDER BY 생산품명;
        """
        
        rows = await conn.fetch(old_query, START_DATE, END_DATE)
        old_product_names = [row['생산품명'] for row in rows]
        print(f"   결과: {len(old_product_names)}개 제품명")
        if old_product_names:
            for name in old_product_names:
                print(f"     - {name}")
        else:
            print("     ⚠️ 제품명이 없습니다!")
        
        # 2. 수정된 쿼리 테스트 (올바른 로직)
        print("\n✅ 2. 수정된 쿼리 테스트 (올바른 로직)")
        new_query = """
        SELECT DISTINCT 생산품명 
        FROM dummy 
        WHERE 생산품명 IS NOT NULL
        AND (
            투입일 >= $1::DATE    -- 투입일이 시작일 이후
            OR 투입일 <= $2::DATE   -- 투입일이 종료일 이전
            OR 종료일 >= $1::DATE -- 종료일이 시작일 이후
            OR 종료일 <= $2::DATE   -- 종료일이 종료일 이전
        )
        ORDER BY 생산품명;
        """
        
        rows = await conn.fetch(new_query, START_DATE, END_DATE)
        new_product_names = [row['생산품명'] for row in rows]
        print(f"   결과: {len(new_product_names)}개 제품명")
        if new_product_names:
            for name in new_product_names:
                print(f"     - {name}")
        else:
            print("     ⚠️ 제품명이 없습니다!")
        
        # 3. 결과 비교
        print("\n📊 3. 결과 비교")
        print(f"   기존 쿼리: {len(old_product_names)}개")
        print(f"   수정된 쿼리: {len(new_product_names)}개")
        
        if len(new_product_names) > len(old_product_names):
            print("   🎉 수정된 쿼리가 더 많은 제품명을 찾았습니다!")
        elif len(new_product_names) == len(old_product_names):
            print("   🤔 두 쿼리 결과가 동일합니다.")
        else:
            print("   ⚠️ 수정된 쿼리가 더 적은 제품명을 찾았습니다.")
        
        # 4. 실제 데이터 확인
        print("\n📅 4. 실제 데이터 확인")
        data_query = """
        SELECT id, 생산품명, 투입일, 종료일, 공정
        FROM dummy 
        WHERE 투입일 >= '2025-08-01'::DATE 
        LIMIT 5;
        """
        
        samples = await conn.fetch(data_query)
        print(f"   8월 이후 투입일 데이터 샘플:")
        for row in samples:
            print(f"     - ID: {row['id']}, 제품: {row['생산품명']}, 투입일: {row['투입일']}, 종료일: {row['종료일']}")
        
        await conn.close()
        print("\n✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_final_query())
