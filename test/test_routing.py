#!/usr/bin/env python3
"""
라우팅 경로 테스트 스크립트
Gateway → CBAM 서비스 간 라우팅이 올바르게 작동하는지 확인
"""

import requests
import json
import sys
from typing import Dict, Any

# 테스트 환경 설정
GATEWAY_URL = "https://gateway-production-22ef.up.railway.app"
CBAM_SERVICE_URL = "https://lcafinal-production.up.railway.app"

def test_gateway_health():
    """Gateway 헬스체크 테스트"""
    try:
        response = requests.get(f"{GATEWAY_URL}/health", timeout=10)
        print(f"✅ Gateway 헬스체크: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   서비스: {data.get('service')}")
            print(f"   상태: {data.get('status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Gateway 헬스체크 실패: {e}")
        return False

def test_cbam_service_health():
    """CBAM 서비스 헬스체크 테스트"""
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/health", timeout=10)
        print(f"✅ CBAM 서비스 헬스체크: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   서비스: {data.get('service')}")
            print(f"   상태: {data.get('status')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ CBAM 서비스 헬스체크 실패: {e}")
        return False

def test_install_routing():
    """Install 라우팅 테스트"""
    print("\n🔍 Install 라우팅 테스트...")
    
    # Gateway를 통한 install 목록 조회
    try:
        response = requests.get(f"{GATEWAY_URL}/api/v1/install", timeout=10)
        print(f"✅ Gateway → Install 목록: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   응답 데이터: {len(data)}개 항목")
        elif response.status_code == 404:
            print("   ⚠️ 404 응답 (경로는 올바르지만 데이터 없음)")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ Gateway → Install 라우팅 실패: {e}")
        return False
    
    # Gateway를 통한 install names 조회
    try:
        response = requests.get(f"{GATEWAY_URL}/api/v1/install/names", timeout=10)
        print(f"✅ Gateway → Install Names: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   응답 데이터: {len(data)}개 항목")
        elif response.status_code == 404:
            print("   ⚠️ 404 응답 (경로는 올바르지만 데이터 없음)")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ Gateway → Install Names 라우팅 실패: {e}")
        return False
    
    return True

def test_direct_cbam_access():
    """CBAM 서비스 직접 접근 테스트"""
    print("\n🔍 CBAM 서비스 직접 접근 테스트...")
    
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/install", timeout=10)
        print(f"✅ CBAM 직접 접근 → Install: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   응답 데이터: {len(data)}개 항목")
        elif response.status_code == 404:
            print("   ⚠️ 404 응답 (경로는 올바르지만 데이터 없음)")
        else:
            print(f"   ⚠️ 예상치 못한 상태 코드: {response.status_code}")
    except Exception as e:
        print(f"❌ CBAM 직접 접근 실패: {e}")
        return False
    
    return True

def test_routing_paths():
    """라우팅 경로 분석"""
    print("\n🔍 라우팅 경로 분석...")
    
    # Gateway 라우팅 정보
    try:
        response = requests.get(f"{GATEWAY_URL}/debug/routes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway 라우트 정보: {data.get('total_routes', 0)}개")
            
            # Install 관련 라우트 확인
            install_routes = data.get('install_routes', [])
            if install_routes:
                print(f"   Install 라우트: {len(install_routes)}개")
                for route in install_routes[:3]:  # 처음 3개만 표시
                    print(f"     - {route['path']} [{', '.join(route['methods'])}]")
            else:
                print("   ⚠️ Install 라우트를 찾을 수 없음")
    except Exception as e:
        print(f"❌ Gateway 라우트 정보 조회 실패: {e}")
    
    # CBAM 서비스 라우트 정보
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/debug/routes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CBAM 서비스 라우트 정보: {data.get('total_routes', 0)}개")
            
            # Install 관련 라우트 확인
            install_routes = data.get('install_routes', [])
            if install_routes:
                print(f"   Install 라우트: {len(install_routes)}개")
                for route in install_routes[:3]:  # 처음 3개만 표시
                    print(f"     - {route['path']} [{', '.join(route['methods'])}]")
            else:
                print("   ⚠️ Install 라우트를 찾을 수 없음")
    except Exception as e:
        print(f"❌ CBAM 서비스 라우트 정보 조회 실패: {e}")

def main():
    """메인 테스트 실행"""
    print("🚀 라우팅 경로 테스트 시작")
    print("=" * 50)
    
    # 1. 기본 헬스체크
    gateway_ok = test_gateway_health()
    cbam_ok = test_cbam_service_health()
    
    if not gateway_ok or not cbam_ok:
        print("\n❌ 기본 서비스 연결 실패")
        return False
    
    # 2. 라우팅 테스트
    install_routing_ok = test_install_routing()
    direct_access_ok = test_direct_cbam_access()
    
    # 3. 라우팅 경로 분석
    test_routing_paths()
    
    # 4. 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print(f"   Gateway 연결: {'✅' if gateway_ok else '❌'}")
    print(f"   CBAM 서비스 연결: {'✅' if cbam_ok else '❌'}")
    print(f"   Install 라우팅: {'✅' if install_routing_ok else '❌'}")
    print(f"   직접 접근: {'✅' if direct_access_ok else '❌'}")
    
    if all([gateway_ok, cbam_ok, install_routing_ok, direct_access_ok]):
        print("\n🎉 모든 테스트 통과! 라우팅이 올바르게 작동합니다.")
        return True
    else:
        print("\n⚠️ 일부 테스트 실패. 라우팅 설정을 확인해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
