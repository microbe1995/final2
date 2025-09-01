#!/usr/bin/env python3
"""
Edge CRUD 기능을 테스트하는 스크립트
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_edge_crud():
    """Edge CRUD 기능을 테스트합니다."""
    
    # Railway 서비스 URL
    service_url = "https://lcafinal-production.up.railway.app"
    
    print(f"🚀 Edge CRUD 기능 테스트 시작")
    print(f"📍 테스트 대상: {service_url}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. Edge 목록 조회 테스트 (GET /edge/)
            print("\n🔍 1. Edge 목록 조회 테스트 (GET /edge/)")
            print("-" * 40)
            try:
                async with session.get(f"{service_url}/edge/") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Edge 목록 조회 성공!")
                        print(f"📊 응답 상태: {response.status}")
                        print(f"📋 Edge 개수: {len(data)}개")
                        if data:
                            print(f"📝 첫 번째 Edge: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Edge 목록 조회 실패: {response.status}")
                        print(f"오류 내용: {error_text}")
            except Exception as e:
                print(f"❌ Edge 목록 조회 테스트 실패: {e}")
            
            # 2. Edge 생성 테스트 (POST /edge/)
            print("\n🔍 2. Edge 생성 테스트 (POST /edge/)")
            print("-" * 40)
            try:
                # 테스트용 Edge 데이터
                test_edge = {
                    "source_node_type": "process",
                    "source_id": 156,
                    "target_node_type": "process", 
                    "target_id": 157,
                    "edge_kind": "continue"
                }
                
                async with session.post(f"{service_url}/edge/", json=test_edge) as response:
                    if response.status == 201:
                        data = await response.json()
                        print(f"✅ Edge 생성 성공!")
                        print(f"📊 응답 상태: {response.status}")
                        print(f"📝 생성된 Edge: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        
                        # 생성된 Edge ID 저장
                        created_edge_id = data.get('id')
                        print(f"🆔 생성된 Edge ID: {created_edge_id}")
                        
                    else:
                        error_text = await response.text()
                        print(f"❌ Edge 생성 실패: {response.status}")
                        print(f"오류 내용: {error_text}")
                        created_edge_id = None
                        
            except Exception as e:
                print(f"❌ Edge 생성 테스트 실패: {e}")
                created_edge_id = None
            
            # 3. 생성된 Edge 상세 조회 테스트 (GET /edge/{id})
            if created_edge_id:
                print(f"\n🔍 3. Edge 상세 조회 테스트 (GET /edge/{created_edge_id})")
                print("-" * 40)
                try:
                    async with session.get(f"{service_url}/edge/{created_edge_id}") as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Edge 상세 조회 성공!")
                            print(f"📊 응답 상태: {response.status}")
                            print(f"📝 Edge 정보: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        else:
                            error_text = await response.text()
                            print(f"❌ Edge 상세 조회 실패: {response.status}")
                            print(f"오류 내용: {error_text}")
                except Exception as e:
                    print(f"❌ Edge 상세 조회 테스트 실패: {e}")
                
                # 4. Edge 수정 테스트 (PUT /edge/{id})
                print(f"\n🔍 4. Edge 수정 테스트 (PUT /edge/{created_edge_id})")
                print("-" * 40)
                try:
                    update_data = {
                        "edge_kind": "produce"  # continue에서 produce로 변경
                    }
                    
                    async with session.put(f"{service_url}/edge/{created_edge_id}", json=update_data) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Edge 수정 성공!")
                            print(f"📊 응답 상태: {response.status}")
                            print(f"📝 수정된 Edge: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        else:
                            error_text = await response.text()
                            print(f"❌ Edge 수정 실패: {response.status}")
                            print(f"오류 내용: {error_text}")
                except Exception as e:
                    print(f"❌ Edge 수정 테스트 실패: {e}")
                
                # 5. Edge 삭제 테스트 (DELETE /edge/{id})
                print(f"\n🔍 5. Edge 삭제 테스트 (DELETE /edge/{created_edge_id})")
                print("-" * 40)
                try:
                    async with session.delete(f"{service_url}/edge/{created_edge_id}") as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"✅ Edge 삭제 성공!")
                            print(f"📊 응답 상태: {response.status}")
                            print(f"📝 삭제 결과: {json.dumps(data, indent=2, ensure_ascii=False)}")
                        else:
                            error_text = await response.text()
                            print(f"❌ Edge 삭제 실패: {response.status}")
                            print(f"오류 내용: {error_text}")
                except Exception as e:
                    print(f"❌ Edge 삭제 테스트 실패: {e}")
            
            # 6. 최종 Edge 목록 확인
            print(f"\n🔍 6. 최종 Edge 목록 확인 (GET /edge/)")
            print("-" * 40)
            try:
                async with session.get(f"{service_url}/edge/") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 최종 Edge 목록 조회 성공!")
                        print(f"📊 응답 상태: {response.status}")
                        print(f"📋 최종 Edge 개수: {len(data)}개")
                    else:
                        error_text = await response.text()
                        print(f"❌ 최종 Edge 목록 조회 실패: {response.status}")
                        print(f"오류 내용: {error_text}")
            except Exception as e:
                print(f"❌ 최종 Edge 목록 조회 테스트 실패: {e}")
    
    except Exception as e:
        print(f"❌ 전체 테스트 과정에서 오류 발생: {e}")
    
    print("\n🎯 Edge CRUD 기능 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_edge_crud())
