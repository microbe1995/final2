#!/usr/bin/env python3
"""
Install API 라우팅 테스트 스크립트
Gateway → CBAM 서비스 간 install API 호출 테스트
"""

import requests
import sys

# 테스트 환경 설정
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"
CBAM_SERVICE_URL = "https://lcafinal-production.up.railway.app"

def test_install_routing():
    """Install API 라우팅 테스트"""
    print("🔍 Install API 라우팅 테스트 시작")
    print("=" * 50)
    
    # 1. Gateway를 통한 install 목록 조회
    print("\n1️⃣ Gateway → Install 목록 조회")
    try:
        response = requests.get(f"{GATEWAY_URL}/api/v1/install", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {len(data)}개 항목")
            if data:
                print(f"   첫 번째 항목: {data[0]}")
        elif response.status_code == 404:
            print("   ❌ 404 Not Found - 경로는 올바르지만 데이터 없음")
            print(f"   응답 내용: {response.text}")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    # 2. CBAM 서비스 직접 접근
    print("\n2️⃣ CBAM 서비스 직접 접근")
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/install", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {len(data)}개 항목")
            if data:
                print(f"   첫 번째 항목: {data[0]}")
        elif response.status_code == 404:
            print("   ❌ 404 Not Found - install 경로 없음")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    # 3. CBAM 서비스 루트 경로
    print("\n3️⃣ CBAM 서비스 루트 경로")
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {data.get('message', 'N/A')}")
            print(f"   사용 가능한 엔드포인트: {data.get('endpoints', {})}")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    # 4. Gateway 헬스체크
    print("\n4️⃣ Gateway 헬스체크")
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: {data.get('service', 'N/A')}")
            print(f"   등록된 서비스: {data.get('services', {})}")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    # 5. Gateway 라우팅 정보 확인
    print("\n5️⃣ Gateway 라우팅 정보 확인")
    try:
        response = requests.get(f"{GATEWAY_URL}/debug/routes", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: 총 {data.get('total_routes', 0)}개 라우트")
            
            # Install 관련 라우트 확인
            install_routes = data.get('install_routes', [])
            if install_routes:
                print(f"   Install 라우트: {len(install_routes)}개")
                for route in install_routes[:3]:
                    print(f"     - {route['path']} [{', '.join(route['methods'])}]")
            else:
                print("   ⚠️ Install 라우트를 찾을 수 없음")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
    
    # 6. CBAM 서비스 라우팅 정보 확인
    print("\n6️⃣ CBAM 서비스 라우팅 정보 확인")
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/debug/routes", timeout=10)
        print(f"   상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 성공: 총 {data.get('total_routes', 0)}개 라우트")
            
            # Install 관련 라우트 확인
            install_routes = data.get('install_routes', [])
            if install_routes:
                print(f"   Install 라우트: {len(install_routes)}개")
                for route in install_routes[:3]:
                    print(f"     - {route['path']} [{', '.join(route['methods'])}]")
            else:
                print("   ⚠️ Install 라우트를 찾을 수 없음")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")

if __name__ == "__main__":
    test_install_routing()
    print("\n" + "=" * 50)
    print("🏁 테스트 완료")
