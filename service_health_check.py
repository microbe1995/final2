import requests
import json

def check_service_health():
    """서비스 배포 상태 확인"""
    
    print("🔍 서비스 배포 상태 확인")
    print("=" * 50)
    
    # 서비스 URL들
    services = {
        'Frontend': 'https://lca-final.vercel.app',
        'Gateway': 'https://gateway-production-da31.up.railway.app/health',
        'CBAM Service': 'https://cal-boundary-production.up.railway.app/health',
        'Auth Service': 'https://auth-service-production.up.railway.app/health'
    }
    
    for service_name, url in services.items():
        try:
            print(f"\n📡 {service_name} 확인 중...")
            print(f"   URL: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ 상태: 정상 (200)")
                if service_name != 'Frontend':
                    try:
                        data = response.json()
                        print(f"   📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"   📊 응답: {response.text[:100]}...")
            else:
                print(f"   ⚠️ 상태: {response.status_code}")
                print(f"   📊 응답: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 오류: {str(e)}")
        except Exception as e:
            print(f"   ❌ 예상치 못한 오류: {str(e)}")
    
    print("\n📋 문제 해결 가이드:")
    print("1. Railway 대시보드에서 서비스 상태 확인")
    print("2. 환경변수 설정 확인 (특히 DATABASE_URL)")
    print("3. 서비스 재배포")
    print("4. 로그 확인")

if __name__ == "__main__":
    check_service_health()
