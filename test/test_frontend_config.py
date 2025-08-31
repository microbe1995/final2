#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프론트엔드 설정 종합 테스트 스크립트
Frontend Configuration Comprehensive Test Script

이 스크립트는 프론트엔드의 다음 항목들을 테스트합니다:
1. 환경변수 설정 확인
2. API 엔드포인트 구성 확인
3. Gateway 연결 테스트
4. 실제 API 호출 테스트
"""

import os
import sys
import json
import requests
from urllib.parse import urljoin, urlparse
import time

# 색상 출력을 위한 ANSI 코드
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(title):
    """헤더 출력"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}{Colors.END}")

def print_success(message):
    """성공 메시지 출력"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """에러 메시지 출력"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """경고 메시지 출력"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def print_info(message):
    """정보 메시지 출력"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def test_environment_variables():
    """환경변수 테스트"""
    print_header("환경변수 설정 테스트")
    
    # 필요한 환경변수들
    required_vars = [
        'NEXT_PUBLIC_API_BASE_URL',
        'NEXT_PUBLIC_GATEWAY_URL'
    ]
    
    print("📋 환경변수 확인 중...")
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value}")
            
            # URL 유효성 검사
            try:
                parsed = urlparse(value)
                if parsed.scheme and parsed.netloc:
                    print_success(f"  → URL 형식 유효: {parsed.scheme}://{parsed.netloc}")
                else:
                    print_error(f"  → URL 형식 무효: {value}")
            except Exception as e:
                print_error(f"  → URL 파싱 실패: {e}")
        else:
            print_error(f"{var}: 설정되지 않음")
    
    # 기본값 확인
    print("\n📋 기본값 확인:")
    default_gateway = "https://gateway-production-22ef.up.railway.app"
    print_info(f"기본 Gateway URL: {default_gateway}")
    
    return True

def test_gateway_connection():
    """Gateway 연결 테스트"""
    print_header("Gateway 연결 테스트")
    
    # 테스트할 URL들
    test_urls = [
        "https://gateway-production-22ef.up.railway.app",
        "https://gateway-production-da31.up.railway.app"  # 이전 URL
    ]
    
    for url in test_urls:
        print(f"\n🔗 {url} 연결 테스트 중...")
        
        try:
            # 헬스 체크
            health_url = f"{url}/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print_success(f"헬스 체크 성공: {response.status_code}")
                try:
                    data = response.json()
                    print_info(f"응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print_info(f"응답 내용: {response.text[:200]}")
            else:
                print_error(f"헬스 체크 실패: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"연결 실패: {e}")
    
    return True

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print_header("API 엔드포인트 테스트")
    
    base_url = "https://gateway-production-22ef.up.railway.app"
    
    # 테스트할 API 엔드포인트들
    test_endpoints = [
        "/api/v1/boundary/install",
        "/api/v1/boundary/install/names",
        "/api/v1/boundary/product",
        "/api/v1/boundary/process"
    ]
    
    print(f"🔗 Base URL: {base_url}")
    
    for endpoint in test_endpoints:
        full_url = urljoin(base_url, endpoint)
        print(f"\n📡 테스트: {endpoint}")
        
        try:
            start_time = time.time()
            response = requests.get(full_url, timeout=10)
            response_time = time.time() - start_time
            
            print(f"  상태코드: {response.status_code}")
            print(f"  응답시간: {response_time:.3f}초")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print_success(f"  성공: {len(data)}개 항목 반환")
                        if data:
                            print(f"  📋 첫 번째 항목: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
                    else:
                        print_success(f"  성공: {type(data).__name__} 데이터 반환")
                        print(f"  📋 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print_success(f"  성공: 텍스트 응답 ({len(response.text)}자)")
            else:
                print_error(f"  실패: {response.status_code}")
                print(f"  📋 응답: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print_error(f"  요청 실패: {e}")

def test_frontend_config_files():
    """프론트엔드 설정 파일 테스트"""
    print_header("프론트엔드 설정 파일 테스트")
    
    # 확인할 파일들
    config_files = [
        "frontend/next.config.js",
        "frontend/vercel.json",
        "frontend/src/lib/env.ts",
        "frontend/src/lib/axiosClient.ts",
        "frontend/public/manifest.json"
    ]
    
    print("📁 설정 파일 존재 여부 확인:")
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print_success(f"✅ {file_path}")
            
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            print_info(f"  → 크기: {file_size:,} bytes")
            
            # 파일 내용 일부 확인
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(500)  # 처음 500자만
                    lines = content.split('\n')
                    print_info(f"  → 첫 {len(lines)}줄")
                    
                    # 중요 설정 확인
                    if 'gateway-production-22ef' in content:
                        print_success(f"  → 올바른 Gateway URL 포함")
                    elif 'gateway-production-da31' in content:
                        print_warning(f"  → 이전 Gateway URL 포함 (수정 필요)")
                    
                    if 'baseURL' in content and 'env.NEXT_PUBLIC_API_BASE_URL' in content:
                        print_success(f"  → env.ts 사용 설정")
                    else:
                        print_warning(f"  → env.ts 미사용 (수정 필요)")
                        
            except Exception as e:
                print_error(f"  → 파일 읽기 실패: {e}")
        else:
            print_error(f"❌ {file_path} (파일 없음)")

def test_axios_configuration():
    """Axios 설정 테스트"""
    print_header("Axios 설정 테스트")
    
    # axiosClient.ts 파일 분석
    file_path = "frontend/src/lib/axiosClient.ts"
    
    if not os.path.exists(file_path):
        print_error("axiosClient.ts 파일을 찾을 수 없습니다.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("🔍 Axios 설정 분석:")
        
        # env.ts import 확인
        if "import { env } from './env';" in content:
            print_success("✅ env.ts import 확인")
        else:
            print_error("❌ env.ts import 없음")
        
        # baseURL 설정 확인
        if "baseURL: env.NEXT_PUBLIC_API_BASE_URL" in content:
            print_success("✅ baseURL이 env.ts 사용")
        elif "baseURL: ''" in content:
            print_error("❌ baseURL이 빈 문자열")
        else:
            print_warning("⚠️  baseURL 설정 불명확")
        
        # API 엔드포인트 확인
        if "/api/v1/boundary/install" in content:
            print_success("✅ boundary/install 엔드포인트 설정")
        else:
            print_error("❌ boundary/install 엔드포인트 없음")
            
        # 디버깅 로그 확인
        if "🚀 API 요청:" in content:
            print_success("✅ 디버깅 로그 포함")
        else:
            print_warning("⚠️  디버깅 로그 없음")
            
    except Exception as e:
        print_error(f"파일 분석 실패: {e}")

def main():
    """메인 테스트 실행"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🚀 프론트엔드 설정 종합 테스트 시작")
    print("=" * 60)
    print(f"{Colors.END}")
    
    try:
        # 1. 환경변수 테스트
        test_environment_variables()
        
        # 2. Gateway 연결 테스트
        test_gateway_connection()
        
        # 3. API 엔드포인트 테스트
        test_api_endpoints()
        
        # 4. 프론트엔드 설정 파일 테스트
        test_frontend_config_files()
        
        # 5. Axios 설정 테스트
        test_axios_configuration()
        
        print_header("테스트 완료")
        print_success("모든 테스트가 완료되었습니다!")
        print("\n📋 다음 단계:")
        print("1. 로컬에서 'npm run dev' 실행")
        print("2. 브라우저에서 사업장 관리 페이지 접속")
        print("3. 개발자 도구 Console에서 '🚀 API 요청:' 로그 확인")
        print("4. Network 탭에서 실제 API 요청 URL 확인")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트가 중단되었습니다.")
    except Exception as e:
        print_error(f"테스트 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
