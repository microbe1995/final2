#!/usr/bin/env python3
"""
간단한 Edge 생성 테스트 스크립트
"""

import os
import asyncio
import aiohttp
import json

async def test_edge_simple():
    """간단한 Edge 생성 테스트"""
    
    service_url = "https://lcafinal-production.up.railway.app"
    
    print(f"🚀 간단한 Edge 생성 테스트")
    print(f"📍 테스트 대상: {service_url}")
    print("=" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. 서비스 상태 확인
            print("\n🔍 1. 서비스 상태 확인")
            try:
                async with session.get(f"{service_url}/docs") as response:
                    print(f"📊 서비스 상태: {response.status}")
            except Exception as e:
                print(f"❌ 서비스 연결 실패: {e}")
                return
            
            # 2. Edge 목록 조회 (현재 상태)
            print("\n🔍 2. 현재 Edge 목록 조회")
            try:
                async with session.get(f"{service_url}/edge/") as response:
                    print(f"📊 Edge 목록 응답: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"📋 현재 Edge 개수: {len(data)}개")
                    else:
                        error_text = await response.text()
                        print(f"❌ 오류: {error_text}")
            except Exception as e:
                print(f"❌ Edge 목록 조회 실패: {e}")
            
            # 3. 간단한 Edge 생성 테스트
            print("\n🔍 3. 간단한 Edge 생성 테스트")
            try:
                test_edge = {
                    "source_node_type": "process",
                    "source_id": 156,
                    "target_node_type": "process", 
                    "target_id": 157,
                    "edge_kind": "continue"
                }
                
                print(f"📝 테스트 데이터: {json.dumps(test_edge, indent=2, ensure_ascii=False)}")
                
                async with session.post(f"{service_url}/edge/", json=test_edge) as response:
                    print(f"📊 Edge 생성 응답: {response.status}")
                    
                    if response.status == 201:
                        data = await response.json()
                        print(f"✅ Edge 생성 성공!")
                        print(f"📝 생성된 Edge: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Edge 생성 실패: {error_text}")
                        
                        # 오류 분석
                        if "NoneType" in error_text:
                            print("🔍 문제: EdgeService.create_edge()가 None을 반환")
                        elif "sqlite3" in error_text.lower():
                            print("🔍 문제: SQLite 데이터베이스 사용 중")
                        elif "no such table" in error_text.lower():
                            print("🔍 문제: Edge 테이블이 존재하지 않음")
                        
            except Exception as e:
                print(f"❌ Edge 생성 테스트 실패: {e}")
    
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
    
    print("\n🎯 간단한 Edge 생성 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_edge_simple())
