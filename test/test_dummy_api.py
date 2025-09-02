import requests
import json
import time
from datetime import datetime

# Railway에 배포된 CBAM 서비스 URL
# Gateway를 통해 접근하므로 실제 CBAM 서비스 포트 사용
CBAM_SERVICE_URL = "http://localhost:8001"  # 로컬 테스트용
# 실제 Railway 배포 시에는 아래 URL 사용
# CBAM_SERVICE_URL = "https://your-railway-app-url.railway.app"

def test_dummy_api():
    """Dummy API 테스트"""
    print("=" * 60)
    print("🚀 Railway CBAM 서비스 Dummy API 테스트")
    print("=" * 60)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"서비스 URL: {CBAM_SERVICE_URL}")
    print()
    
    # 1. 서비스 헬스체크
    print("1️⃣ 서비스 헬스체크 테스트")
    print("-" * 40)
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 서비스 상태: {health_data.get('status', 'unknown')}")
            print(f"서비스명: {health_data.get('service', 'unknown')}")
            print(f"버전: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 서비스 연결 실패: {e}")
        return False
    print()
    
    # 2. 서비스 루트 엔드포인트 테스트
    print("2️⃣ 서비스 루트 엔드포인트 테스트")
    print("-" * 40)
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ 서비스 메시지: {root_data.get('message', 'unknown')}")
            print(f"사용 가능한 엔드포인트:")
            for endpoint, path in root_data.get('endpoints', {}).items():
                print(f"  - {endpoint}: {path}")
        else:
            print(f"❌ 루트 엔드포인트 실패: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 루트 엔드포인트 연결 실패: {e}")
    print()
    
    # 3. Dummy 데이터 전체 조회 테스트
    print("3️⃣ Dummy 데이터 전체 조회 테스트")
    print("-" * 40)
    try:
        response = requests.get(f"{CBAM_SERVICE_URL}/dummy", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            dummy_data = response.json()
            print(f"✅ 데이터 조회 성공!")
            print(f"총 데이터 수: {len(dummy_data)}")
            
            if dummy_data:
                print("\n📊 샘플 데이터:")
                for i, item in enumerate(dummy_data[:3]):  # 처음 3개만 표시
                    print(f"  {i+1}. ID: {item.get('id')}")
                    print(f"     로트번호: {item.get('로트번호')}")
                    print(f"     생산품명: {item.get('생산품명')}")
                    print(f"     생산수량: {item.get('생산수량')}")
                    print(f"     공정: {item.get('공정')}")
                    print(f"     투입물명: {item.get('투입물명')}")
                    print(f"     수량: {item.get('수량')}")
                    print(f"     단위: {item.get('단위')}")
                    print()
            else:
                print("⚠️ 데이터가 없습니다.")
        else:
            print(f"❌ Dummy 데이터 조회 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Dummy API 연결 실패: {e}")
    print()
    
    # 4. 특정 Dummy 데이터 조회 테스트
    print("4️⃣ 특정 Dummy 데이터 조회 테스트")
    print("-" * 40)
    try:
        # ID 1번 데이터 조회
        response = requests.get(f"{CBAM_SERVICE_URL}/dummy/1", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            item = response.json()
            print(f"✅ ID 1번 데이터 조회 성공!")
            print(f"로트번호: {item.get('로트번호')}")
            print(f"생산품명: {item.get('생산품명')}")
            print(f"생산수량: {item.get('생산수량')}")
            print(f"투입일: {item.get('투입일')}")
            print(f"종료일: {item.get('종료일')}")
            print(f"공정: {item.get('공정')}")
            print(f"투입물명: {item.get('투입물명')}")
            print(f"수량: {item.get('수량')}")
            print(f"단위: {item.get('단위')}")
        elif response.status_code == 404:
            print("⚠️ ID 1번 데이터를 찾을 수 없습니다.")
        else:
            print(f"❌ 특정 데이터 조회 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 특정 데이터 API 연결 실패: {e}")
    print()
    
    # 5. 존재하지 않는 데이터 조회 테스트 (404 에러 테스트)
    print("5️⃣ 존재하지 않는 데이터 조회 테스트 (404 에러)")
    print("-" * 40)
    try:
        # 존재하지 않는 ID로 조회
        response = requests.get(f"{CBAM_SERVICE_URL}/dummy/99999", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✅ 404 에러 정상 처리됨 (존재하지 않는 데이터)")
        else:
            print(f"⚠️ 예상과 다른 응답: {response.status_code}")
            if response.text:
                print(f"응답 내용: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 404 테스트 연결 실패: {e}")
    print()
    
    # 6. 잘못된 엔드포인트 테스트 (404 에러 테스트)
    print("6️⃣ 잘못된 엔드포인트 테스트 (404 에러)")
    print("-" * 40)
    try:
        # 존재하지 않는 엔드포인트
        response = requests.get(f"{CBAM_SERVICE_URL}/dummy/invalid", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✅ 404 에러 정상 처리됨 (잘못된 엔드포인트)")
        else:
            print(f"⚠️ 예상과 다른 응답: {response.status_code}")
            if response.text:
                print(f"응답 내용: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 잘못된 엔드포인트 테스트 연결 실패: {e}")
    print()
    
    # 7. 성능 테스트
    print("7️⃣ 성능 테스트 (응답 시간 측정)")
    print("-" * 40)
    try:
        start_time = time.time()
        response = requests.get(f"{CBAM_SERVICE_URL}/dummy", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 밀리초 단위
        
        if response.status_code == 200:
            print(f"✅ 응답 성공")
            print(f"응답 시간: {response_time:.2f}ms")
            
            if response_time < 100:
                print("🚀 매우 빠른 응답 (100ms 미만)")
            elif response_time < 500:
                print("⚡ 빠른 응답 (500ms 미만)")
            elif response_time < 1000:
                print("🐌 보통 응답 (1초 미만)")
            else:
                print("🐌 느린 응답 (1초 이상)")
        else:
            print(f"❌ 응답 실패: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 성능 테스트 실패: {e}")
    print()
    
    print("=" * 60)
    print("🏁 테스트 완료!")
    print("=" * 60)

def test_gateway_routing():
    """Gateway를 통한 라우팅 테스트 (선택사항)"""
    print("\n" + "=" * 60)
    print("🌐 Gateway 라우팅 테스트 (선택사항)")
    print("=" * 60)
    print("참고: Gateway가 실행 중인 경우에만 테스트 가능")
    print()
    
    # Gateway URL (기본 포트 8080)
    GATEWAY_URL = "http://localhost:8080"
    
    try:
        # Gateway를 통한 CBAM 서비스 접근 테스트
        response = requests.get(f"{GATEWAY_URL}/api/v1/cbam/dummy", timeout=10)
        print(f"Gateway를 통한 접근 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Gateway를 통한 라우팅 성공!")
            dummy_data = response.json()
            print(f"데이터 수: {len(dummy_data)}")
        else:
            print(f"❌ Gateway 라우팅 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Gateway 연결 실패: {e}")
        print("💡 Gateway가 실행 중이지 않거나 다른 포트에서 실행 중일 수 있습니다.")

if __name__ == "__main__":
    # 메인 테스트 실행
    test_dummy_api()
    
    # Gateway 테스트 (선택사항)
    test_gateway_routing()
