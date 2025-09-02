#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 CBAM 제품 관리 기능 테스트 실행 스크립트
Python 3.13.5 호환

간단한 명령어로 테스트를 실행할 수 있습니다.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python 버전 확인: {sys.version.split()[0]}")

def install_requirements():
    """필요한 패키지 설치"""
    print("📦 필요한 패키지 설치 중...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ 패키지 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        print(f"에러 출력: {e.stderr}")
        return False

def run_tests(test_type="all", service_url=None):
    """테스트 실행"""
    print(f"🚀 {test_type} 테스트 실행 시작")
    
    if test_type == "all":
        # 전체 테스트 실행
        test_file = "test_cbam_products.py"
    elif test_type == "quick":
        # 빠른 테스트 실행 (기본 CRUD만)
        test_file = "test_cbam_products.py"
        print("⚠️ 빠른 테스트 모드는 아직 구현되지 않았습니다. 전체 테스트를 실행합니다.")
    else:
        print(f"❌ 알 수 없는 테스트 타입: {test_type}")
        return False
    
    if not os.path.exists(test_file):
        print(f"❌ 테스트 파일을 찾을 수 없습니다: {test_file}")
        return False
    
    # 환경변수 설정
    env = os.environ.copy()
    if service_url:
        env["CBAM_SERVICE_URL"] = service_url
        print(f"📍 서비스 URL 설정: {service_url}")
    
    try:
        # 테스트 실행
        result = subprocess.run([
            sys.executable, test_file
        ], env=env, check=False)
        
        if result.returncode == 0:
            print("✅ 테스트 실행 완료")
            return True
        else:
            print(f"⚠️ 테스트 실행 중 일부 실패 (종료 코드: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="CBAM 제품 관리 기능 테스트 실행기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python run_tests.py                    # 전체 테스트 실행
  python run_tests.py --quick            # 빠른 테스트 실행
  python run_tests.py --url http://localhost:8001  # 특정 서비스 URL로 테스트
  python run_tests.py --install-only     # 패키지만 설치
        """
    )
    
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="빠른 테스트 실행 (기본 CRUD만)"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="CBAM 서비스 URL (기본값: http://localhost:8001)"
    )
    
    parser.add_argument(
        "--install-only",
        action="store_true",
        help="패키지만 설치하고 테스트는 실행하지 않음"
    )
    
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="패키지 설치를 건너뛰고 테스트만 실행"
    )
    
    args = parser.parse_args()
    
    print("🔬 CBAM 제품 관리 기능 테스트 실행기")
    print("=" * 50)
    
    # Python 버전 확인
    check_python_version()
    
    # 패키지 설치 (--no-install 옵션이 없으면)
    if not args.no_install:
        if not install_requirements():
            print("❌ 패키지 설치에 실패했습니다. 수동으로 설치해주세요.")
            print("명령어: pip install -r test_requirements.txt")
            if not args.install_only:
                sys.exit(1)
    
    # --install-only 옵션이면 여기서 종료
    if args.install_only:
        print("✅ 패키지 설치 완료. 테스트는 실행하지 않습니다.")
        return
    
    # 테스트 타입 결정
    test_type = "quick" if args.quick else "all"
    
    # 서비스 URL 결정
    service_url = args.url or os.getenv("CBAM_SERVICE_URL", "http://localhost:8001")
    
    # 테스트 실행
    success = run_tests(test_type, service_url)
    
    if success:
        print("\n🎉 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n⚠️ 테스트 실행 중 일부 문제가 발생했습니다.")
        print("로그를 확인하여 자세한 내용을 파악해주세요.")
    
    print("\n" + "=" * 50)
    print("테스트 완료")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)
