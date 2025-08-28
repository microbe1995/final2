#!/usr/bin/env python3
"""
Gateway 환경변수 설정 확인 테스트
"""

import requests
import json

# 테스트 URL들
GATEWAY_URL = "https://gateway-production-da31.up.railway.app"

def test_gateway_environment():
    """Gateway 환경변수 확인"""
    print("🔍 Gateway 환경변수 확인")
    print("=" * 50)
    
    try:
        # Gateway 헬스 체크를 통해 환경변수 정보 확인
        url = f"{GATEWAY_URL}/health"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Gateway 정상 작동")
            print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # domains 정보에서 boundary 서비스 상태 확인
            if 'domains' in data:
                domains = data['domains']
                print(f"\n🔧 도메인 상태:")
                for domain, status in domains.items():
                    print(f"   - {domain}: {status}")
                    
        else:
            print(f"❌ Gateway 오류")
            print(f"📥 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_gateway_logs():
    """Gateway 로그 확인 (간접적 방법)"""
    print("\n🔍 Gateway 로그 확인")
    print("=" * 50)
    
    try:
        # 간단한 요청을 보내서 로그 확인
        url = f"{GATEWAY_URL}/api/v1/boundary/matdir"
        print(f"📡 테스트 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ 404 오류 - 라우팅 실패")
            print("💡 가능한 원인:")
            print("   1. CAL_BOUNDARY_URL 환경변수가 설정되지 않음")
            print("   2. Railway에서 환경변수가 올바르게 로드되지 않음")
            print("   3. cbam-service URL이 잘못됨")
        else:
            print(f"✅ 예상과 다른 응답: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def test_direct_cbam_access():
    """cbam-service 직접 접근 테스트"""
    print("\n🔍 cbam-service 직접 접근 테스트")
    print("=" * 50)
    
    try:
        # cbam-service에 직접 접근
        url = "https://lcafinal-production.up.railway.app/matdir"
        print(f"📡 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📥 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ cbam-service 정상 작동")
            print(f"📊 데이터 개수: {len(data)}개")
        else:
            print(f"❌ cbam-service 오류: {response.text}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")

def check_railway_variables():
    """Railway 환경변수 설정 가이드"""
    print("\n🔧 Railway 환경변수 설정 가이드")
    print("=" * 50)
    
    print("📋 Railway 대시보드에서 다음 환경변수를 설정하세요:")
    print()
    print("🔑 필수 환경변수:")
    print("   CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app")
    print()
    print("🔑 선택적 환경변수:")
    print("   AUTH_SERVICE_URL=http://auth-service:8000")
    print("   CORS_URL=https://lca-final.vercel.app,http://localhost:3000")
    print()
    print("📝 설정 방법:")
    print("   1. Railway 대시보드 접속")
    print("   2. Gateway 서비스 선택")
    print("   3. Variables 탭 클릭")
    print("   4. 위의 환경변수들을 추가")
    print("   5. Deploy 버튼으로 재배포")
    print()
    print("⚠️  주의사항:")
    print("   - 환경변수 설정 후 반드시 재배포 필요")
    print("   - URL 끝에 슬래시(/) 제거")
    print("   - https:// 프로토콜 사용")

if __name__ == "__main__":
    print("🚀 Gateway 환경변수 확인 테스트 시작")
    print()
    
    # 1. Gateway 환경변수 확인
    test_gateway_environment()
    
    # 2. Gateway 로그 확인
    test_gateway_logs()
    
    # 3. cbam-service 직접 접근 테스트
    test_direct_cbam_access()
    
    # 4. Railway 환경변수 설정 가이드
    check_railway_variables()
    
    print("\n✅ 모든 테스트 완료")
