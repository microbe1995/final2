#!/usr/bin/env python3
"""
API 엔드포인트 테스트 스크립트
Gateway를 통해 CBAM 서비스의 dummy API가 제대로 작동하는지 확인
"""

import requests
import json
from datetime import datetime, timedelta

# 설정
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"
CBAM_SERVICE_URL = "https://lcafinal-production.up.railway.app"

def test_gateway_dummy_api():
    """Gateway를 통해 dummy API 테스트"""
    print("🔍 Gateway를 통한 Dummy API 테스트")
    print("=" * 50)
    
    # 테스트할 엔드포인트들
    endpoints = [
        "/api/v1/cbam/dummy/products/names",
        "/api/v1/cbam/dummy/products/names/by-period?start_date=2025-08-01&end_date=2025-09-10",
        "/api/v1/cbam/dummy/processes/names",
        "/api/v1/cbam/dummy/health"
    ]
    
    for endpoint in endpoints:
        url = f"{GATEWAY_URL}{endpoint}"
        print(f"\n📡 테스트: {endpoint}")
        print(f"🌐 URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"📋 데이터 개수: {len(data)}")
                        if len(data) > 0:
                            print(f"📝 첫 번째 항목: {data[0]}")
                    else:
                        print(f"📋 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"📋 텍스트 응답: {response.text[:200]}...")
            else:
                print(f"❌ 실패: {response.status_code}")
                print(f"📋 에러 내용: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")

def test_direct_cbam_service():
    """CBAM 서비스에 직접 요청 테스트"""
    print("\n\n🔍 CBAM 서비스 직접 테스트")
    print("=" * 50)
    
    # 테스트할 엔드포인트들
    endpoints = [
        "/dummy/products/names",
        "/dummy/products/names/by-period?start_date=2025-08-01&end_date=2025-09-10",
        "/dummy/processes/names",
        "/dummy/health"
    ]
    
    for endpoint in endpoints:
        url = f"{CBAM_SERVICE_URL}{endpoint}"
        print(f"\n📡 테스트: {endpoint}")
        print(f"🌐 URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ 성공!")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"📋 데이터 개수: {len(data)}")
                        if len(data) > 0:
                            print(f"📝 첫 번째 항목: {data[0]}")
                    else:
                        print(f"📋 응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"📋 텍스트 응답: {response.text[:200]}...")
            else:
                print(f"❌ 실패: {response.status_code}")
                print(f"📋 에러 내용: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    print("🚀 API 엔드포인트 테스트 시작")
    print(f"⏰ 테스트 시간: {datetime.now()}")
    print(f"🌐 Gateway URL: {GATEWAY_URL}")
    print(f"🌐 CBAM Service URL: {CBAM_SERVICE_URL}")
    
    # 1. Gateway를 통한 테스트
    test_gateway_dummy_api()
    
    # 2. CBAM 서비스 직접 테스트
    test_direct_cbam_service()
    
    print("\n\n🏁 테스트 완료!")
