#!/usr/bin/env python3
"""
제품명 조회 문제 디버깅 스크립트
기간별 제품명 조회가 왜 안 되는지 확인
"""

import asyncio
import aiohttp
import json
from datetime import datetime, date
import sys

# Railway DB 연결 정보 (실제 환경변수에서 가져와야 함)
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

# 테스트할 기간 (이미지에서 설정된 기간)
START_DATE = "2025-08-01"
END_DATE = "2025-09-09"

async def test_dummy_api_directly():
    """CBAM 서비스의 Dummy API를 직접 테스트"""
    print("🔍 CBAM 서비스 Dummy API 직접 테스트")
    print("=" * 50)
    
    # CBAM 서비스 URL (로컬에서 실행 중이라면)
    cbam_base_url = "http://localhost:8001"  # 또는 실제 Railway URL
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 전체 제품명 목록 조회
            print(f"📋 1. 전체 제품명 목록 조회")
            url = f"{cbam_base_url}/dummy/products/names"
            print(f"   URL: {url}")
            
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   응답: {data}")
                    print(f"   제품명 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    text = await response.text()
                    print(f"   에러: {text}")
            
            print()
            
            # 2. 기간별 제품명 목록 조회
            print(f"📅 2. 기간별 제품명 목록 조회")
            url = f"{cbam_base_url}/dummy/products/names/by-period?start_date={START_DATE}&end_date={END_DATE}"
            print(f"   URL: {url}")
            print(f"   기간: {START_DATE} ~ {END_DATE}")
            
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   응답: {data}")
                    print(f"   제품명 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    text = await response.text()
                    print(f"   에러: {text}")
            
            print()
            
            # 3. Dummy 테이블 전체 데이터 확인
            print(f"📊 3. Dummy 테이블 전체 데이터 확인")
            url = f"{cbam_base_url}/dummy"
            print(f"   URL: {url}")
            
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   전체 데이터 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                    
                    # 8월 데이터가 있는지 확인
                    if isinstance(data, list) and len(data) > 0:
                        august_data = []
                        for item in data:
                            if '투입일' in item and item['투입일']:
                                try:
                                    input_date = datetime.strptime(item['투입일'], '%Y-%m-%d').date()
                                    if input_date.month == 8:  # 8월 데이터
                                        august_data.append({
                                            'id': item.get('id'),
                                            '생산품명': item.get('생산품명'),
                                            '투입일': item.get('투입일'),
                                            '종료일': item.get('종료일')
                                        })
                                except:
                                    pass
                        
                        print(f"   8월 데이터 개수: {len(august_data)}")
                        if august_data:
                            print("   첫 5개 8월 데이터:")
                            for item in august_data[:5]:
                                print(f"     - {item}")
                        else:
                            print("   ⚠️ 8월 데이터가 없습니다!")
                else:
                    text = await response.text()
                    print(f"   에러: {text}")
            
        except Exception as e:
            print(f"❌ API 테스트 실패: {e}")

async def test_gateway_api():
    """Gateway를 통한 API 테스트"""
    print("\n🌐 Gateway를 통한 API 테스트")
    print("=" * 50)
    
    # Gateway URL (실제 환경변수에서 가져와야 함)
    gateway_base_url = "https://gateway-production-22ef.up.railway.app"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 기간별 제품명 목록 조회 (Gateway 경로)
            print(f"📅 1. Gateway를 통한 기간별 제품명 목록 조회")
            url = f"{gateway_base_url}/api/v1/cbam/dummy/products/names/by-period?start_date={START_DATE}&end_date={END_DATE}"
            print(f"   URL: {url}")
            print(f"   기간: {START_DATE} ~ {END_DATE}")
            
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   응답: {data}")
                    print(f"   제품명 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    text = await response.text()
                    print(f"   에러: {text}")
            
            print()
            
            # 2. 전체 제품명 목록 조회 (Gateway 경로)
            print(f"📋 2. Gateway를 통한 전체 제품명 목록 조회")
            url = f"{gateway_base_url}/api/v1/cbam/dummy/products/names"
            print(f"   URL: {url}")
            
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   응답: {data}")
                    print(f"   제품명 개수: {len(data) if isinstance(data, list) else 'N/A'}")
                else:
                    text = await response.text()
                    print(f"   에러: {text}")
            
        except Exception as e:
            print(f"❌ Gateway API 테스트 실패: {e}")

async def test_database_query():
    """데이터베이스 쿼리 직접 테스트"""
    print("\n🗄️ 데이터베이스 쿼리 직접 테스트")
    print("=" * 50)
    
    try:
        import asyncpg
        
        # 데이터베이스 연결
        print("🔌 Railway DB 연결 시도...")
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 전체 제품명 개수 확인
        print("\n📊 1. 전체 제품명 개수 확인")
        count_query = "SELECT COUNT(DISTINCT 생산품명) FROM dummy WHERE 생산품명 IS NOT NULL;"
        count = await conn.fetchval(count_query)
        print(f"   전체 고유 제품명 개수: {count}")
        
        # 2. 8월 데이터 개수 확인
        print("\n📅 2. 8월 데이터 개수 확인")
        august_count_query = """
        SELECT COUNT(*) 
        FROM dummy 
        WHERE 투입일 >= '2025-08-01'::DATE 
        AND 투입일 <= '2025-08-31'::DATE;
        """
        august_count = await conn.fetchval(august_count_query)
        print(f"   8월 투입일 데이터 개수: {august_count}")
        
        # 3. 기간별 제품명 쿼리 테스트
        print(f"\n🔍 3. 기간별 제품명 쿼리 테스트 ({START_DATE} ~ {END_DATE})")
        period_query = """
        SELECT DISTINCT 생산품명 
        FROM dummy 
        WHERE 생산품명 IS NOT NULL
        AND 투입일 >= $1::DATE 
        AND 종료일 <= $2::DATE 
        ORDER BY 생산품명;
        """
        
        rows = await conn.fetch(period_query, START_DATE, END_DATE)
        product_names = [row['생산품명'] for row in rows]
        
        print(f"   쿼리 결과 제품명 개수: {len(product_names)}")
        if product_names:
            print("   제품명 목록:")
            for name in product_names:
                print(f"     - {name}")
        else:
            print("   ⚠️ 해당 기간에 제품명이 없습니다!")
            
            # 왜 없는지 디버깅
            print("\n🔍 디버깅: 왜 제품명이 없는지 확인")
            
            # 투입일 범위 확인
            input_date_query = """
            SELECT MIN(투입일), MAX(투입일), COUNT(*) 
            FROM dummy 
            WHERE 투입일 IS NOT NULL;
            """
            input_date_result = await conn.fetchrow(input_date_query)
            if input_date_result:
                min_date, max_date, total_count = input_date_result
                print(f"   투입일 범위: {min_date} ~ {max_date}")
                print(f"   투입일이 있는 데이터 총 개수: {total_count}")
            
            # 종료일 범위 확인
            end_date_query = """
            SELECT MIN(종료일), MAX(종료일), COUNT(*) 
            FROM dummy 
            WHERE 종료일 IS NOT NULL;
            """
            end_date_result = await conn.fetchrow(end_date_query)
            if end_date_result:
                min_date, max_date, total_count = end_date_result
                print(f"   종료일 범위: {min_date} ~ {max_date}")
                print(f"   종료일이 있는 데이터 총 개수: {total_count}")
            
            # 8월 데이터 샘플 확인
            august_sample_query = """
            SELECT id, 생산품명, 투입일, 종료일, 공정
            FROM dummy 
            WHERE 투입일 >= '2025-08-01'::DATE 
            AND 투입일 <= '2025-08-31'::DATE
            LIMIT 5;
            """
            august_samples = await conn.fetch(august_sample_query)
            print(f"\n   8월 데이터 샘플 (최대 5개):")
            for row in august_samples:
                print(f"     - ID: {row['id']}, 제품: {row['생산품명']}, 투입일: {row['투입일']}, 종료일: {row['종료일']}")
        
        await conn.close()
        print("\n✅ 데이터베이스 연결 종료")
        
    except ImportError:
        print("❌ asyncpg가 설치되지 않았습니다. 설치 명령어:")
        print("   pip install asyncpg")
    except Exception as e:
        print(f"❌ 데이터베이스 테스트 실패: {e}")

async def main():
    """메인 함수"""
    print("🚀 제품명 조회 문제 디버깅 시작")
    print(f"📅 테스트 기간: {START_DATE} ~ {END_DATE}")
    print("=" * 60)
    
    # 1. CBAM 서비스 직접 테스트
    await test_dummy_api_directly()
    
    # 2. Gateway를 통한 테스트
    await test_gateway_api()
    
    # 3. 데이터베이스 직접 쿼리 테스트
    await test_database_query()
    
    print("\n" + "=" * 60)
    print("🎯 디버깅 완료!")
    print("\n💡 문제 해결 방법:")
    print("1. 백엔드 서비스가 실행 중인지 확인")
    print("2. 데이터베이스에 8월 데이터가 실제로 있는지 확인")
    print("3. 날짜 형식이 올바른지 확인")
    print("4. API 엔드포인트 경로가 올바른지 확인")

if __name__ == "__main__":
    asyncio.run(main())
