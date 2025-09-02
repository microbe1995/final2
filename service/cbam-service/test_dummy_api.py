#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dummy API 엔드포인트 테스트 스크립트
"""

import asyncio
import httpx
import json

# CBAM 서비스 URL (Railway 상)
BASE_URL = "https://lcafinal-production.up.railway.app"

async def test_dummy_api():
    """Dummy API 엔드포인트 테스트"""
    print("🚀 Dummy API 엔드포인트 테스트 시작\n")
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. 헬스체크 테스트
            print("🔍 1. 헬스체크 테스트...")
            response = await client.get(f"{BASE_URL}/dummy/health")
            print(f"  - GET /dummy/health: {response.status_code}")
            if response.status_code == 200:
                print(f"  - 응답: {response.json()}")
            else:
                print(f"  - 오류: {response.text}")
            
            # 2. 전체 데이터 조회 테스트
            print("\n🔍 2. 전체 데이터 조회 테스트...")
            response = await client.get(f"{BASE_URL}/dummy/")
            print(f"  - GET /dummy/: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  - 데이터 개수: {data.get('total', 0)}")
                print(f"  - 첫 번째 항목: {data.get('items', [])[0] if data.get('items') else 'None'}")
            else:
                print(f"  - 오류: {response.text}")
            
            # 3. 특정 ID로 데이터 조회 테스트
            print("\n🔍 3. 특정 ID로 데이터 조회 테스트...")
            response = await client.get(f"{BASE_URL}/dummy/1")
            print(f"  - GET /dummy/1: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  - 데이터: {data}")
            else:
                print(f"  - 오류: {response.text}")
            
            # 4. OPTIONS 메서드 테스트
            print("\n🔍 4. OPTIONS 메서드 테스트...")
            response = await client.options(f"{BASE_URL}/dummy/")
            print(f"  - OPTIONS /dummy/: {response.status_code}")
            if response.status_code == 200:
                print(f"  - 응답: {response.json()}")
            else:
                print(f"  - 오류: {response.text}")
            
            # 5. 데이터 개수 통계 테스트
            print("\n🔍 5. 데이터 개수 통계 테스트...")
            response = await client.get(f"{BASE_URL}/dummy/stats/count")
            print(f"  - GET /dummy/stats/count: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  - 응답: {data}")
            else:
                print(f"  - 오류: {response.text}")
            
            print("\n✅ 모든 테스트 완료!")
            
        except httpx.ConnectError:
            print(f"❌ 서버에 연결할 수 없습니다: {BASE_URL}")
            print("  - CBAM 서비스가 실행 중인지 확인해주세요.")
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")

async def main():
    """메인 함수"""
    await test_dummy_api()

if __name__ == "__main__":
    asyncio.run(main())
