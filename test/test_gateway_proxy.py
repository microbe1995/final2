#!/usr/bin/env python3
"""
Gateway 프록시 기능 테스트 스크립트
- /api/v1/cbam/install 요청이 Gateway → CAL_BOUNDARY_URL로 정상 프록시되는지 확인
- 307/ERR_FAILED/CSP 경고가 없는지 확인
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_gateway_proxy():
    """Gateway 프록시 기능 테스트"""
    
    # 테스트 설정
    gateway_url = "https://gateway-production-22ef.up.railway.app"
    test_endpoints = [
        "/api/v1/cbam/install",
        "/api/v1/cbam/install",  # 🔴 수정: boundary → cbam으로 통일
        "/api/v1/cbam/product",
        "/api/v1/cbam/product"   # 🔴 수정: boundary → cbam으로 통일
    ]
    
    print("🚀 Gateway 프록시 기능 테스트 시작")
    print(f"📍 Gateway URL: {gateway_url}")
    print("=" * 60)
    
    for endpoint in test_endpoints:
        print(f"\n🔍 테스트 엔드포인트: {endpoint}")
        
        try:
            # GET 요청 테스트
            url = urljoin(gateway_url, endpoint)
            response = requests.get(url, timeout=30)
            
            print(f"   📤 요청: GET {url}")
            print(f"   📥 응답: {response.status_code} {response.reason}")
            
            # 응답 헤더 확인
            print(f"   📋 응답 헤더:")
            for key, value in response.headers.items():
                if key.lower() in ['content-type', 'content-length', 'server', 'date']:
                    print(f"      {key}: {value}")
            
            # 응답 내용 확인 (짧게)
            content = response.text[:200] if response.text else "빈 응답"
            print(f"   📄 응답 내용 (처음 200자): {content}")
            
            # 307 리다이렉트 확인
            if response.status_code == 307:
                location = response.headers.get('location', 'N/A')
                print(f"   ⚠️  307 리다이렉트 감지! Location: {location}")
            elif response.status_code >= 400:
                print(f"   ❌ 에러 응답: {response.status_code}")
            else:
                print(f"   ✅ 정상 응답: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 요청 실패: {e}")
        except Exception as e:
            print(f"   ❌ 예상치 못한 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    
    # 추가 테스트: 헬스 체크
    print(f"\n🔍 Gateway 헬스 체크: {urljoin(gateway_url, '/health')}")
    try:
        health_response = requests.get(urljoin(gateway_url, '/health'), timeout=10)
        print(f"   📥 헬스 체크 응답: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   📋 서비스 상태: {json.dumps(health_data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 헬스 체크 실패: {e}")

if __name__ == "__main__":
    test_gateway_proxy()
