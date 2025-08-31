#!/usr/bin/env python3
"""
로컬 Gateway 테스트 스크립트
Gateway의 프록시 로직이 올바르게 작동하는지 테스트
"""

import requests
import sys

# 테스트 환경 설정 (로컬)
GATEWAY_URL = "http://localhost:8080"
CBAM_SERVICE_URL = "https://lcafinal-production.up.railway.app"

def test_local_gateway():
    """로컬 Gateway 테스트"""
    print("🔍 로컬 Gateway 테스트 시작")
    print("=" * 50)
    
    # 1. 로컬 Gateway 헬스체크
    print("\n1️⃣ 로컬 Gateway 헬스체크")
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {data.get('service', 'N/A')}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 연결 실패: 로컬 Gateway가 실행되지 않았습니다")
        print("   💡 해결방법: gateway 폴더에서 'python -m uvicorn app.main:app --reload --port 8080' 실행")
        return False
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
        return False
    
    # 2. 로컬 Gateway → Install 테스트
    print("\n2️⃣ 로컬 Gateway → Install 테스트")
    try:
        response = requests.get(f"{GATEWAY_URL}/api/v1/install", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {len(data)}개 항목")
        elif response.status_code == 404:
            print("   ❌ 404 Not Found")
            print(f"   응답 내용: {response.text}")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    return True

def start_local_gateway():
    """로컬 Gateway 시작 안내"""
    print("\n🚀 로컬 Gateway 시작 방법")
    print("=" * 50)
    print("1. 새 터미널 창을 열고 다음 명령어 실행:")
    print("   cd gateway")
    print("   python -m uvicorn app.main:app --reload --port 8080")
    print("\n2. Gateway가 시작되면 이 스크립트를 다시 실행하세요")
    print("\n3. 또는 Railway에 배포된 Gateway를 사용하세요")

if __name__ == "__main__":
    if not test_local_gateway():
        start_local_gateway()
    else:
        print("\n" + "=" * 50)
        print("🏁 테스트 완료")
