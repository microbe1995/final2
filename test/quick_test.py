#!/usr/bin/env python3
"""
빠른 Gateway 테스트 스크립트
"""

import requests
import time

def test_gateway():
    """Gateway 테스트"""
    print("🚀 Gateway 테스트 시작")
    print("=" * 40)
    
    # 테스트 URL들
    test_urls = [
        "https://gateway-production-22ef.up.railway.app/health",
        "https://gateway-production-22ef.up.railway.app/api/v1/install",
        "https://lcafinal-production.up.railway.app/install",
        "https://lcafinal-production.up.railway.app/"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}️⃣ {url}")
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            print(f"   상태 코드: {response.status_code}")
            print(f"   응답 시간: {(end_time - start_time):.2f}초")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   ✅ 성공: {len(data)}개 항목")
                        if data:
                            print(f"   첫 번째 항목: {data[0]}")
                    else:
                        print(f"   ✅ 성공: {data}")
                except:
                    print(f"   ✅ 성공: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"   ❌ 404 Not Found")
                print(f"   응답: {response.text}")
            else:
                print(f"   ⚠️ 상태 코드: {response.status_code}")
                print(f"   응답: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    print("\n" + "=" * 40)
    print("🏁 테스트 완료")

if __name__ == "__main__":
    test_gateway()
