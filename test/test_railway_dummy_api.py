import requests
import json
import time
from datetime import datetime

# Railway에 배포된 CBAM 서비스 URL
# 실제 Railway 배포 URL로 변경해야 함
RAILWAY_CBAM_URL = "https://your-railway-cbam-service.railway.app"  # 실제 URL로 변경 필요

# Railway PostgreSQL DB 연결 정보 (참고용)
RAILWAY_DB_INFO = {
    "host": "shortline.proxy.rlwy.net",
    "port": "46071",
    "database": "railway",
    "user": "postgres"
}

def test_railway_dummy_api():
    """Railway에 배포된 CBAM 서비스의 Dummy API 테스트"""
    print("=" * 70)
    print("🚀 Railway CBAM 서비스 Dummy API 테스트")
    print("=" * 70)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Railway 서비스 URL: {RAILWAY_CBAM_URL}")
    print(f"Railway DB: {RAILWAY_DB_INFO['host']}:{RAILWAY_DB_INFO['port']}")
    print()
    
    # 1. Railway 서비스 연결 테스트
    print("1️⃣ Railway 서비스 연결 테스트")
    print("-" * 50)
    try:
        response = requests.get(f"{RAILWAY_CBAM_URL}/health", timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Railway 서비스 연결 성공!")
            print(f"서비스 상태: {health_data.get('status', 'unknown')}")
            print(f"서비스명: {health_data.get('service', 'unknown')}")
            print(f"버전: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Railway 서비스 연결 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Railway 서비스 연결 실패: {e}")
        print("💡 Railway 서비스가 배포되지 않았거나 URL이 잘못되었을 수 있습니다.")
        return False
    print()
    
    # 2. Railway 서비스 루트 엔드포인트 테스트
    print("2️⃣ Railway 서비스 루트 엔드포인트 테스트")
    print("-" * 50)
    try:
        response = requests.get(f"{RAILWAY_CBAM_URL}/", timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            root_data = response.json()
            print(f"✅ Railway 서비스 정상 동작!")
            print(f"서비스 메시지: {root_data.get('message', 'unknown')}")
            print(f"사용 가능한 엔드포인트:")
            for endpoint, path in root_data.get('endpoints', {}).items():
                print(f"  - {endpoint}: {path}")
        else:
            print(f"❌ Railway 서비스 루트 엔드포인트 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Railway 서비스 루트 엔드포인트 연결 실패: {e}")
    print()
    
    # 3. Railway DB의 Dummy 데이터 조회 테스트
    print("3️⃣ Railway DB의 Dummy 데이터 조회 테스트")
    print("-" * 50)
    try:
        response = requests.get(f"{RAILWAY_CBAM_URL}/dummy", timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            dummy_data = response.json()
            print(f"✅ Railway DB 연결 및 데이터 조회 성공!")
            print(f"총 데이터 수: {len(dummy_data)}")
            
            if dummy_data:
                print("\n📊 Railway DB의 실제 데이터:")
                for i, item in enumerate(dummy_data[:5]):  # 처음 5개 표시
                    print(f"  {i+1}. ID: {item.get('id')}")
                    print(f"     로트번호: {item.get('로트번호')}")
                    print(f"     생산품명: {item.get('생산품명')}")
                    print(f"     생산수량: {item.get('생산수량')}")
                    print(f"     투입일: {item.get('투입일')}")
                    print(f"     종료일: {item.get('종료일')}")
                    print(f"     공정: {item.get('공정')}")
                    print(f"     투입물명: {item.get('투입물명')}")
                    print(f"     수량: {item.get('수량')}")
                    print(f"     단위: {item.get('단위')}")
                    print(f"     생성일: {item.get('created_at')}")
                    print()
            else:
                print("⚠️ Railway DB에 데이터가 없습니다.")
                print("💡 dummy_db.xlsx 파일을 업로드했는지 확인하세요.")
        else:
            print(f"❌ Railway DB 데이터 조회 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Railway DB 데이터 조회 실패: {e}")
    print()
    
    # 4. 특정 Dummy 데이터 조회 테스트
    print("4️⃣ Railway DB의 특정 Dummy 데이터 조회 테스트")
    print("-" * 50)
    try:
        # ID 1번 데이터 조회
        response = requests.get(f"{RAILWAY_CBAM_URL}/dummy/1", timeout=30)
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
            print("💡 Railway DB에 데이터가 업로드되지 않았을 수 있습니다.")
        else:
            print(f"❌ 특정 데이터 조회 실패: {response.status_code}")
            if response.text:
                print(f"에러 메시지: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 특정 데이터 API 연결 실패: {e}")
    print()
    
    # 5. Railway 서비스 성능 테스트
    print("5️⃣ Railway 서비스 성능 테스트 (응답 시간 측정)")
    print("-" * 50)
    try:
        start_time = time.time()
        response = requests.get(f"{RAILWAY_CBAM_URL}/dummy", timeout=30)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 밀리초 단위
        
        if response.status_code == 200:
            print(f"✅ Railway 서비스 응답 성공")
            print(f"응답 시간: {response_time:.2f}ms")
            
            if response_time < 100:
                print("🚀 매우 빠른 응답 (100ms 미만)")
            elif response_time < 500:
                print("⚡ 빠른 응답 (500ms 미만)")
            elif response_time < 1000:
                print("🐌 보통 응답 (1초 미만)")
            elif response_time < 3000:
                print("🐌 느린 응답 (3초 미만)")
            else:
                print("🐌 매우 느린 응답 (3초 이상)")
                print("💡 Railway 서비스 성능을 확인해보세요.")
        else:
            print(f"❌ 응답 실패: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 성능 테스트 실패: {e}")
    print()
    
    # 6. Railway 서비스 상태 요약
    print("6️⃣ Railway 서비스 상태 요약")
    print("-" * 50)
    try:
        # 여러 엔드포인트 상태 확인
        endpoints = ["/health", "/", "/dummy"]
        status_summary = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{RAILWAY_CBAM_URL}{endpoint}", timeout=30)
                status_summary[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                status_summary[endpoint] = {"error": str(e)}
        
        print("📊 엔드포인트별 상태:")
        for endpoint, info in status_summary.items():
            if "error" in info:
                print(f"  ❌ {endpoint}: 연결 실패 - {info['error']}")
            else:
                status_icon = "✅" if info["status_code"] == 200 else "⚠️"
                print(f"  {status_icon} {endpoint}: {info['status_code']} ({info['response_time']:.1f}ms)")
        
    except Exception as e:
        print(f"❌ 상태 요약 생성 실패: {e}")
    print()
    
    print("=" * 70)
    print("🏁 Railway 테스트 완료!")
    print("=" * 70)

def test_railway_database_connection():
    """Railway PostgreSQL DB 직접 연결 테스트 (선택사항)"""
    print("\n" + "=" * 70)
    print("🗄️ Railway PostgreSQL DB 직접 연결 테스트 (선택사항)")
    print("=" * 70)
    print("참고: psycopg2 패키지가 설치되어 있어야 합니다.")
    print()
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Railway PostgreSQL 연결
        DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
        
        print("🔗 Railway PostgreSQL DB에 직접 연결 시도...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # dummy 테이블 확인
        cursor.execute("SELECT COUNT(*) as count FROM dummy")
        result = cursor.fetchone()
        total_count = result['count']
        
        print(f"✅ Railway DB 직접 연결 성공!")
        print(f"dummy 테이블 총 데이터 수: {total_count}")
        
        # 샘플 데이터 확인
        if total_count > 0:
            cursor.execute("SELECT * FROM dummy LIMIT 3")
            sample_data = cursor.fetchall()
            
            print("\n📊 Railway DB의 실제 데이터 (직접 연결):")
            for i, row in enumerate(sample_data):
                print(f"  {i+1}. ID: {row['id']}")
                print(f"     로트번호: {row['로트번호']}")
                print(f"     생산품명: {row['생산품명']}")
                print(f"     생산수량: {row['생산수량']}")
                print(f"     공정: {row['공정']}")
                print()
        
        cursor.close()
        conn.close()
        print("✅ Railway DB 연결 종료")
        
    except ImportError:
        print("❌ psycopg2 패키지가 설치되지 않았습니다.")
        print("💡 pip install psycopg2-binary로 설치하세요.")
    except Exception as e:
        print(f"❌ Railway DB 직접 연결 실패: {e}")
        print("💡 Railway DB 연결 정보를 확인하세요.")

def main():
    """메인 실행 함수"""
    print("🚀 Railway CBAM 서비스 테스트 시작")
    print("=" * 70)
    
    # Railway 서비스 API 테스트
    if test_railway_dummy_api():
        print("✅ Railway 서비스 API 테스트 완료")
    else:
        print("❌ Railway 서비스 API 테스트 실패")
        print("💡 Railway 서비스가 배포되지 않았거나 URL이 잘못되었습니다.")
    
    # Railway DB 직접 연결 테스트 (선택사항)
    test_railway_database_connection()
    
    print("\n" + "=" * 70)
    print("🎯 테스트 결과 요약")
    print("=" * 70)
    print("1. Railway 서비스가 정상 배포되어 있는지 확인")
    print("2. dummy API가 Railway DB와 정상 연결되어 있는지 확인")
    print("3. 실제 데이터가 Railway DB에 업로드되어 있는지 확인")
    print("4. 응답 시간이 적절한지 확인")
    print("=" * 70)

if __name__ == "__main__":
    main()
