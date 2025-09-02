#!/usr/bin/env python3
"""
최종 수정된 쿼리 테스트 - 더 정확한 날짜 겹침 로직
"""

import asyncio
import asyncpg
from datetime import datetime, date

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_final_query():
    """최종 수정된 쿼리 테스트"""
    print("🧪 최종 수정된 쿼리 테스트")
    print("=" * 50)
    
    try:
        # 데이터베이스 연결
        print("🔌 Railway DB 연결 시도...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 현재 데이터 상태 확인
        print("\n📊 1. 현재 데이터 상태")
        total_count = await conn.fetchval("SELECT COUNT(*) FROM dummy;")
        print(f"   전체 데이터 개수: {total_count}")
        
        # 2. 전체 제품명 확인
        print("\n📋 2. 전체 제품명 확인")
        all_names = await conn.fetch("SELECT DISTINCT 생산품명 FROM dummy WHERE 생산품명 IS NOT NULL ORDER BY 생산품명;")
        all_product_names = [row['생산품명'] for row in all_names]
        print(f"   전체 제품명: {all_product_names}")
        
        # 3. 최종 수정된 쿼리 테스트 (2025-08-01 ~ 2025-08-14)
        print("\n🔍 3. 최종 수정된 쿼리 테스트 (2025-08-01 ~ 2025-08-14)")
        
        # 프론트엔드에서 실제로 요청하는 기간
        start_date = "2025-08-01"
        end_date = "2025-08-14"
        
        print(f"   시작일: {start_date}")
        print(f"   종료일: {end_date}")
        
        # 최종 수정된 쿼리: 더 정확한 날짜 겹침 로직
        query = """
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
            AND (
                (투입일 <= $2 AND 종료일 >= $1)  -- 기간이 겹치는 경우
                OR (투입일 BETWEEN $1 AND $2)     -- 투입일이 기간 내에 있는 경우
                OR (종료일 BETWEEN $1 AND $2)     -- 종료일이 기간 내에 있는 경우
            )
            ORDER BY 생산품명;
        """
        
        print(f"   쿼리: {query.strip()}")
        
        # DATE 객체로 변환
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        print(f"   시작일 객체: {start_date_obj} (타입: {type(start_date_obj)})")
        print(f"   종료일 객체: {end_date_obj} (타입: {type(end_date_obj)})")
        
        rows = await conn.fetch(query, start_date_obj, end_date_obj)
        product_names = [row['생산품명'] for row in rows]
        
        print(f"   결과: {len(product_names)}개 제품명")
        print(f"   제품명 목록: {product_names}")
        
        # 4. 개별 데이터 확인 (디버깅용)
        print("\n🔍 4. 개별 데이터 확인 (디버깅용)")
        debug_query = """
            SELECT id, 생산품명, 투입일, 종료일
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
            AND (
                (투입일 <= $2 AND 종료일 >= $1)
                OR (투입일 BETWEEN $1 AND $2)
                OR (종료일 BETWEEN $1 AND $2)
            )
            ORDER BY 생산품명, 투입일;
        """
        
        debug_rows = await conn.fetch(debug_query, start_date_obj, end_date_obj)
        print(f"   매칭된 데이터 개수: {len(debug_rows)}개")
        
        for row in debug_rows:
            print(f"     - ID: {row['id']}, 제품: {row['생산품명']}, 투입일: {row['투입일']}, 종료일: {row['종료일']}")
        
        # 5. 날짜 범위 확인
        print("\n📅 5. 날짜 범위 확인")
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
        
        await conn.close()
        print("\n✅ 데이터베이스 연결 종료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_query())
