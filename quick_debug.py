#!/usr/bin/env python3
"""
빠른 디버깅 - 현재 상황 확인
"""

import asyncio
import asyncpg

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def quick_debug():
    """빠른 디버깅"""
    print("🔍 빠른 디버깅 - 현재 상황 확인")
    print("=" * 40)
    
    try:
        # 데이터베이스 연결
        print("🔌 Railway DB 연결 시도...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 현재 데이터 상태 확인
        print("\n📊 1. 현재 데이터 상태")
        total_count = await conn.fetchval("SELECT COUNT(*) FROM dummy;")
        print(f"   전체 데이터 개수: {total_count}")
        
        # 2. 8월 데이터 확인 (2025-08-01 ~ 2025-08-30)
        print("\n📅 2. 8월 데이터 확인 (2025-08-01 ~ 2025-08-30)")
        
        # 투입일이 8월인 데이터
        input_august = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM dummy 
            WHERE 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-30'::DATE;
        """)
        print(f"   투입일이 8월인 데이터: {input_august}개")
        
        # 종료일이 8월인 데이터
        end_august = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM dummy 
            WHERE 종료일 >= '2025-08-01'::DATE 
            AND 종료일 <= '2025-08-30'::DATE;
        """)
        print(f"   종료일이 8월인 데이터: {end_august}개")
        
        # 3. 실제 8월 데이터 샘플
        print("\n📋 3. 실제 8월 데이터 샘플")
        august_samples = await conn.fetch("""
            SELECT id, 생산품명, 투입일, 종료일, 공정
            FROM dummy 
            WHERE 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-30'::DATE
            LIMIT 3;
        """)
        
        if august_samples:
            print("   투입일이 8월인 데이터:")
            for row in august_samples:
                print(f"     - ID: {row['id']}, 제품: {row['생산품명']}, 투입일: {row['투입일']}, 종료일: {row['종료일']}")
        else:
            print("   ⚠️ 투입일이 8월인 데이터가 없습니다!")
        
        # 4. 날짜 범위 확인
        print("\n📅 4. 날짜 범위 확인")
        date_range = await conn.fetchrow("""
            SELECT 
                MIN(투입일) as min_input,
                MAX(투입일) as max_input,
                MIN(종료일) as min_end,
                MAX(종료일) as max_end
            FROM dummy 
            WHERE 투입일 IS NOT NULL OR 종료일 IS NOT NULL;
        """)
        
        if date_range:
            print(f"   투입일 범위: {date_range['min_input']} ~ {date_range['max_input']}")
            print(f"   종료일 범위: {date_range['min_end']} ~ {date_range['max_end']}")
        
        # 5. 간단한 기간별 제품명 쿼리 테스트
        print("\n🔍 5. 간단한 기간별 제품명 쿼리 테스트")
        
        # 투입일만으로 제품명 찾기
        input_names = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL
            AND 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-30'::DATE
            ORDER BY 생산품명;
        """)
        
        input_product_names = [row['생산품명'] for row in input_names]
        print(f"   투입일 기준 제품명: {len(input_product_names)}개")
        for name in input_product_names:
            print(f"     - {name}")
        
        await conn.close()
        print("\n✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")

if __name__ == "__main__":
    asyncio.run(quick_debug())
