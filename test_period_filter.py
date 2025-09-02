#!/usr/bin/env python3
"""
기간별 제품명 조회 기능 테스트 스크립트
"""

import asyncio
import asyncpg
import os
from datetime import date, datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

async def test_period_filter():
    """기간별 제품명 조회 기능 테스트"""
    
    # Railway DB 연결
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        print("✅ Railway DB 연결 성공")
        
        # dummy 테이블 확인
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dummy'
            );
        """)
        
        if not table_exists:
            print("❌ dummy 테이블이 존재하지 않습니다.")
            await conn.close()
            return
        
        print("✅ dummy 테이블 확인 완료")
        
        # 전체 제품명 목록 조회
        print("\n📋 전체 제품명 목록:")
        all_products = await conn.fetch("SELECT DISTINCT 생산품명 FROM dummy WHERE 생산품명 IS NOT NULL ORDER BY 생산품명;")
        for i, row in enumerate(all_products, 1):
            print(f"  {i}. {row['생산품명']}")
        
        # 기간별 제품명 목록 조회 테스트
        print("\n📅 기간별 제품명 목록 테스트:")
        
        # 테스트 1: 2024년 1월
        print("\n🔍 테스트 1: 2024년 1월 (2024-01-01 ~ 2024-01-31)")
        period1_products = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
              AND 투입일 >= '2024-01-01' 
              AND 종료일 <= '2024-01-31'
            ORDER BY 생산품명;
        """)
        for i, row in enumerate(period1_products, 1):
            print(f"  {i}. {row['생산품명']}")
        
        # 테스트 2: 2024년 2월
        print("\n🔍 테스트 2: 2024년 2월 (2024-02-01 ~ 2024-02-29)")
        period2_products = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
              AND 투입일 >= '2024-02-01' 
              AND 종료일 <= '2024-02-29'
            ORDER BY 생산품명;
        """)
        for i, row in enumerate(period2_products, 1):
            print(f"  {i}. {row['생산품명']}")
        
        # 테스트 3: 시작일만 설정
        print("\n🔍 테스트 3: 2024년 1월 1일 이후 (시작일만)")
        start_only_products = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
              AND 투입일 >= '2024-01-01'
            ORDER BY 생산품명;
        """)
        for i, row in enumerate(start_only_products, 1):
            print(f"  {i}. {row['생산품명']}")
        
        # 테스트 4: 종료일만 설정
        print("\n🔍 테스트 4: 2024년 2월 29일 이전 (종료일만)")
        end_only_products = await conn.fetch("""
            SELECT DISTINCT 생산품명 
            FROM dummy 
            WHERE 생산품명 IS NOT NULL 
              AND 종료일 <= '2024-02-29'
            ORDER BY 생산품명;
        """)
        for i, row in enumerate(end_only_products, 1):
            print(f"  {i}. {row['생산품명']}")
        
        await conn.close()
        print("\n✅ 테스트 완료")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    asyncio.run(test_period_filter())
