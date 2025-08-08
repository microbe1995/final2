"""
Auth Service 테스트 스크립트
"""
import requests
import json

# 서비스 URL
AUTH_SERVICE_URL = "http://localhost:8001"
GATEWAY_URL = "http://localhost:8080/api/v1"

def test_auth_service_direct():
    """Auth Service 직접 테스트"""
    print("🔐 Auth Service 직접 테스트")
    print("=" * 50)
    
    # 1. 헬스 체크
    print("1. 헬스 체크")
    response = requests.get(f"{AUTH_SERVICE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 2. 회원가입
    print("2. 회원가입")
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "test123"
    }
    response = requests.post(f"{AUTH_SERVICE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 3. 로그인
    print("3. 로그인")
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    response = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Token: {token[:50]}...")
        print()
        
        # 4. 현재 사용자 정보 조회
        print("4. 현재 사용자 정보 조회")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{AUTH_SERVICE_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # 5. 토큰 검증
        print("5. 토큰 검증")
        response = requests.post(f"{AUTH_SERVICE_URL}/auth/verify-token", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

def test_gateway_auth():
    """Gateway를 통한 Auth Service 테스트"""
    print("🌐 Gateway를 통한 Auth Service 테스트")
    print("=" * 50)
    
    # 1. Gateway 헬스 체크
    print("1. Gateway 헬스 체크")
    response = requests.get(f"{GATEWAY_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 2. Auth Service 헬스 체크 (Gateway 경유)
    print("2. Auth Service 헬스 체크 (Gateway 경유)")
    response = requests.get(f"{GATEWAY_URL}/auth/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 3. 회원가입 (Gateway 경유)
    print("3. 회원가입 (Gateway 경유)")
    register_data = {
        "email": "gateway@example.com",
        "username": "gatewayuser",
        "password": "gateway123"
    }
    response = requests.post(f"{GATEWAY_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # 4. 로그인 (Gateway 경유)
    print("4. 로그인 (Gateway 경유)")
    login_data = {
        "email": "gateway@example.com",
        "password": "gateway123"
    }
    response = requests.post(f"{GATEWAY_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Token: {token[:50]}...")
        print()
        
        # 5. 현재 사용자 정보 조회 (Gateway 경유)
        print("5. 현재 사용자 정보 조회 (Gateway 경유)")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{GATEWAY_URL}/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()
        
        # 6. 토큰 검증 (Gateway 경유)
        print("6. 토큰 검증 (Gateway 경유)")
        response = requests.post(f"{GATEWAY_URL}/auth/verify-token", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print()

if __name__ == "__main__":
    print("🚀 Auth Service 테스트 시작")
    print()
    
    try:
        # Auth Service 직접 테스트
        test_auth_service_direct()
        
        print("\n" + "="*60 + "\n")
        
        # Gateway를 통한 테스트
        test_gateway_auth()
        
        print("✅ 모든 테스트 완료!")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 연결 오류: {e}")
        print("서비스가 실행 중인지 확인하세요:")
        print("- Auth Service: python app/main.py (포트 8001)")
        print("- Gateway Service: python app/main.py (포트 8080)")
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
