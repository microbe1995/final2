#!/usr/bin/env python3
"""
새로 추가된 CBAM 배출량 전파 API 엔드포인트 테스트 스크립트
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# API 기본 URL (Railway 배포 환경)
BASE_URL = "https://lcafinal-production.up.railway.app"

async def test_api_endpoints():
    """새로 추가된 API 엔드포인트들을 테스트합니다."""
    
    print("🚀 CBAM 배출량 전파 API 엔드포인트 테스트 시작")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. 공정 체인 배출량 요약 조회 테스트
        print("\n🔍 1. 공정 체인 배출량 요약 조회 테스트")
        print("=" * 60)
        
        try:
            url = f"{BASE_URL}/edge/chain-emission-summary/1"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 공정 체인 배출량 요약 조회 성공!")
                    print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 공정 체인 배출량 요약 조회 실패: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
        
        # 2. 공정별 배출량 정보 조회 테스트
        print("\n🔍 2. 공정별 배출량 정보 조회 테스트")
        print("=" * 60)
        
        for process_id in [156, 157]:
            try:
                url = f"{BASE_URL}/edge/process-emission/{process_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 공정 {process_id} 배출량 정보 조회 성공!")
                        print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"❌ 공정 {process_id} 배출량 정보 조회 실패: {response.status}")
                        error_text = await response.text()
                        print(f"오류 내용: {error_text}")
            except Exception as e:
                print(f"❌ API 호출 실패: {e}")
        
        # 3. continue 엣지 조회 테스트
        print("\n🔍 3. continue 엣지 조회 테스트")
        print("=" * 60)
        
        for process_id in [156, 157]:
            try:
                url = f"{BASE_URL}/edge/continue-edges/{process_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 공정 {process_id} continue 엣지 조회 성공!")
                        print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"❌ 공정 {process_id} continue 엣지 조회 실패: {response.status}")
                        error_text = await response.text()
                        print(f"오류 내용: {error_text}")
            except Exception as e:
                print(f"❌ API 호출 실패: {e}")
        
        # 4. 공정 간 배출량 누적 전달 테스트
        print("\n🔍 4. 공정 간 배출량 누적 전달 테스트")
        print("=" * 60)
        
        try:
            url = f"{BASE_URL}/edge/propagate-emissions-continue"
            params = {
                'source_process_id': 156,
                'target_process_id': 157
            }
            async with session.post(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 공정 간 배출량 누적 전달 성공!")
                    print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 공정 간 배출량 누적 전달 실패: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
        
        # 5. 공정 체인 전체 배출량 누적 전달 테스트
        print("\n🔍 5. 공정 체인 전체 배출량 누적 전달 테스트")
        print("=" * 60)
        
        try:
            url = f"{BASE_URL}/edge/propagate-emissions/1"
            async with session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 공정 체인 전체 배출량 누적 전달 성공!")
                    print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 공정 체인 전체 배출량 누적 전달 실패: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
        
        # 6. 최종 결과 확인
        print("\n🔍 6. 최종 결과 확인")
        print("=" * 60)
        
        try:
            url = f"{BASE_URL}/edge/chain-emission-summary/1"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ 최종 공정 체인 배출량 요약 조회 성공!")
                    print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                else:
                    print(f"❌ 최종 공정 체인 배출량 요약 조회 실패: {response.status}")
                    error_text = await response.text()
                    print(f"오류 내용: {error_text}")
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
    
    print("\n🎯 API 테스트 완료!")

if __name__ == "__main__":
    print("🚀 Railway 배포된 CBAM 서비스 API 테스트 시작")
    print(f"📍 테스트 대상: {BASE_URL}")
    print("=" * 60)
    
    # 바로 테스트 실행
    asyncio.run(test_api_endpoints())
