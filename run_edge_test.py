#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge 도메인 테스트 실행 스크립트
간단한 명령어로 테스트를 실행할 수 있습니다.
"""

import sys
import subprocess
import os
from datetime import datetime

def check_dependencies():
    """필요한 패키지가 설치되어 있는지 확인"""
    required_packages = ['asyncpg']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {', '.join(missing_packages)}")
        print("다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def run_test():
    """테스트 실행"""
    print("🚀 Edge 도메인 테스트 시작")
    print(f"📅 실행 시간: {datetime.now()}")
    print("=" * 60)
    
    # 의존성 확인
    if not check_dependencies():
        return False
    
    # 테스트 스크립트 실행
    try:
        result = subprocess.run([
            sys.executable, 'test_edge_functionality.py'
        ], capture_output=True, text=True, timeout=300)  # 5분 타임아웃
        
        # 출력 표시
        print("📋 테스트 출력:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ 오류 출력:")
            print(result.stderr)
        
        # 결과 확인
        if result.returncode == 0:
            print("✅ 테스트 실행 완료")
            return True
        else:
            print(f"❌ 테스트 실행 실패 (종료 코드: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 테스트 실행 시간 초과 (5분)")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {e}")
        return False

def show_help():
    """도움말 표시"""
    print("Edge 도메인 테스트 실행기")
    print("=" * 40)
    print("사용법:")
    print("  python run_edge_test.py          # 테스트 실행")
    print("  python run_edge_test.py --help   # 도움말 표시")
    print("")
    print("테스트 내용:")
    print("  - 기본 CRUD 작업 (생성, 조회, 수정, 삭제)")
    print("  - 배출량 전파 규칙 3가지 (continue, produce, consume)")
    print("  - 엣지 통계 및 분석")
    print("  - 에러 처리 및 검증")
    print("")
    print("결과:")
    print("  - 콘솔 출력 및 edge_test.log 파일에 상세 로그 저장")
    print("  - 성공률 및 오류 목록 제공")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
    else:
        success = run_test()
        sys.exit(0 if success else 1)
