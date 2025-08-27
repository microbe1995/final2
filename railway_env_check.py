import os

def check_railway_environment():
    """Railway 환경변수 설정 확인"""
    
    print("🔍 Railway 환경변수 확인")
    print("=" * 50)
    
    # 주요 환경변수들 확인
    env_vars = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT'),
        'PORT': os.getenv('PORT'),
        'DEBUG_MODE': os.getenv('DEBUG_MODE'),
        'AUTH_SERVICE_URL': os.getenv('AUTH_SERVICE_URL'),
        'CAL_BOUNDARY_URL': os.getenv('CAL_BOUNDARY_URL')
    }
    
    for key, value in env_vars.items():
        if value:
            if key == 'DATABASE_URL':
                # 민감한 정보는 일부만 표시
                masked_value = value[:50] + "..." if len(value) > 50 else value
                print(f"✅ {key}: {masked_value}")
            else:
                print(f"✅ {key}: {value}")
        else:
            print(f"❌ {key}: 설정되지 않음")
    
    print("\n📋 Railway 설정 가이드:")
    print("1. Railway 대시보드 접속")
    print("2. CBAM 서비스 프로젝트 선택")
    print("3. Variables 탭에서 다음 환경변수 설정:")
    print("   - DATABASE_URL: postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway")
    print("   - PORT: 8001")
    print("   - DEBUG_MODE: true")
    print("4. 서비스 재배포")

if __name__ == "__main__":
    check_railway_environment()
