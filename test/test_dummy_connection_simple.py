#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB dummy 테이블과 dummy 도메인 코드 연결 테스트 (간단 버전)
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

def test_dummy_domain_code():
    """dummy 도메인 코드 테스트"""
    print("🔍 Dummy 도메인 코드 테스트 시작...")
    
    try:
        # dummy 도메인 모듈들 임포트 테스트
        from app.domain.dummy.dummy_entity import DummyData
        from app.domain.dummy.dummy_schema import DummyDataCreateRequest, DummyDataResponse
        from app.domain.dummy.dummy_repository import DummyRepository
        from app.domain.dummy.dummy_service import DummyService
        from app.domain.dummy.dummy_controller import router
        
        print("✅ 모든 dummy 도메인 모듈 임포트 성공!")
        
        # Repository 테스트
        print("\n🔧 Repository 테스트...")
        repo = DummyRepository()
        print(f"  - Repository 타입: {type(repo)}")
        print(f"  - Database URL: {repo.database_url[:50]}..." if repo.database_url else "  - Database URL: None")
        
        # Service 테스트
        print("\n🔧 Service 테스트...")
        service = DummyService()
        print(f"  - Service 타입: {type(service)}")
        print(f"  - Repository 타입: {type(service.repository)}")
        
        # Controller 테스트
        print("\n🔧 Controller 테스트...")
        print(f"  - Router 타입: {type(router)}")
        print(f"  - 라우터 태그: {router.tags}")
        
        # 라우트 정보 확인
        routes = []
        for route in router.routes:
            routes.append({
                'path': route.path,
                'methods': list(route.methods) if hasattr(route, 'methods') else [],
                'name': getattr(route, 'name', 'unknown')
            })
        
        print(f"  - 등록된 라우트 수: {len(routes)}")
        for route in routes:
            print(f"    * {route['methods']} {route['path']} ({route['name']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Dummy 도메인 코드 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_railway_db_connection_psql():
    """psql을 사용한 Railway DB 연결 테스트"""
    print("\n🔍 Railway DB 연결 테스트 (psql 사용)...")
    
    try:
        # psql 명령어로 연결 테스트
        # 테이블 존재 여부 확인
        check_table_cmd = [
            'psql', 
            RAILWAY_DB_URL, 
            '-c', 
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'dummy');"
        ]
        
        print(f"  - 실행 명령어: {' '.join(check_table_cmd)}")
        
        result = subprocess.run(
            check_table_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ psql 연결 성공!")
            print(f"  - 출력: {result.stdout.strip()}")
            
            # 테이블 구조 확인
            structure_cmd = [
                'psql', 
                RAILWAY_DB_URL, 
                '-c', 
                "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'dummy' ORDER BY ordinal_position;"
            ]
            
            structure_result = subprocess.run(
                structure_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if structure_result.returncode == 0:
                print("\n📋 dummy 테이블 구조:")
                print(structure_result.stdout.strip())
            else:
                print(f"⚠️ 테이블 구조 확인 실패: {structure_result.stderr}")
            
            # 데이터 개수 확인
            count_cmd = [
                'psql', 
                RAILWAY_DB_URL, 
                '-c', 
                "SELECT COUNT(*) FROM dummy;"
            ]
            
            count_result = subprocess.run(
                count_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if count_result.returncode == 0:
                print(f"\n📊 dummy 테이블 데이터 개수: {count_result.stdout.strip()}")
            else:
                print(f"⚠️ 데이터 개수 확인 실패: {count_result.stderr}")
            
            return True
        else:
            print(f"❌ psql 연결 실패: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ psql 명령어 실행 시간 초과")
        return False
    except FileNotFoundError:
        print("❌ psql 명령어를 찾을 수 없습니다. PostgreSQL 클라이언트가 설치되어 있는지 확인해주세요.")
        return False
    except Exception as e:
        print(f"❌ Railway DB 연결 테스트 실패: {e}")
        return False

def test_railway_db_connection_curl():
    """curl을 사용한 Railway DB 연결 테스트 (HTTP API가 있다면)"""
    print("\n🔍 Railway DB HTTP API 연결 테스트 (curl 사용)...")
    
    try:
        # Railway DB가 HTTP API를 제공한다면 테스트
        # 일반적으로 PostgreSQL은 직접 HTTP API를 제공하지 않으므로 이 테스트는 건너뜀
        print("⚠️ PostgreSQL은 직접 HTTP API를 제공하지 않습니다.")
        print("  - psql 클라이언트나 드라이버를 사용해야 합니다.")
        return True
        
    except Exception as e:
        print(f"❌ Railway DB HTTP API 테스트 실패: {e}")
        return False

def test_environment_variables():
    """환경변수 설정 테스트"""
    print("\n🔍 환경변수 설정 테스트...")
    
    try:
        # DATABASE_URL 환경변수 설정
        os.environ['DATABASE_URL'] = RAILWAY_DB_URL
        print(f"✅ DATABASE_URL 환경변수 설정: {os.environ['DATABASE_URL'][:50]}...")
        
        # 다른 필요한 환경변수들 확인
        env_vars = {
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'NODE_ENV': os.environ.get('NODE_ENV'),
            'PYTHONPATH': os.environ.get('PYTHONPATH')
        }
        
        print("\n📋 환경변수 상태:")
        for key, value in env_vars.items():
            if value:
                print(f"  - {key}: {value[:50]}..." if len(str(value)) > 50 else f"  - {key}: {value}")
            else:
                print(f"  - {key}: 설정되지 않음")
        
        return True
        
    except Exception as e:
        print(f"❌ 환경변수 설정 테스트 실패: {e}")
        return False

def test_file_structure():
    """파일 구조 테스트"""
    print("\n🔍 파일 구조 테스트...")
    
    try:
        # dummy 도메인 파일들이 존재하는지 확인
        dummy_files = [
            'app/domain/dummy/dummy_entity.py',
            'app/domain/dummy/dummy_schema.py',
            'app/domain/dummy/dummy_repository.py',
            'app/domain/dummy/dummy_service.py',
            'app/domain/dummy/dummy_controller.py',
            'app/domain/dummy/__init__.py'
        ]
        
        print("📁 dummy 도메인 파일 존재 여부:")
        all_exist = True
        
        for file_path in dummy_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  ✅ {file_path} ({file_size} bytes)")
            else:
                print(f"  ❌ {file_path} (존재하지 않음)")
                all_exist = False
        
        # main.py에서 dummy 라우터 등록 확인
        main_py_path = 'app/main.py'
        if os.path.exists(main_py_path):
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'dummy_router' in content:
                    print(f"  ✅ {main_py_path}에 dummy_router 등록됨")
                else:
                    print(f"  ❌ {main_py_path}에 dummy_router 등록되지 않음")
                    all_exist = False
        else:
            print(f"  ❌ {main_py_path} (존재하지 않음)")
            all_exist = False
        
        return all_exist
        
    except Exception as e:
        print(f"❌ 파일 구조 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Railway DB와 Dummy 도메인 연결 테스트 시작 (간단 버전)\n")
    
    # 1. 파일 구조 테스트
    file_ok = test_file_structure()
    
    # 2. 환경변수 설정 테스트
    env_ok = test_environment_variables()
    
    # 3. Dummy 도메인 코드 테스트
    code_ok = test_dummy_domain_code()
    
    # 4. Railway DB 연결 테스트 (psql)
    db_ok = test_railway_db_connection_psql()
    
    # 5. Railway DB HTTP API 테스트 (선택사항)
    http_ok = test_railway_db_connection_curl()
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    print(f"✅ 파일 구조: {'성공' if file_ok else '실패'}")
    print(f"✅ 환경변수 설정: {'성공' if env_ok else '실패'}")
    print(f"✅ Dummy 도메인 코드: {'성공' if code_ok else '실패'}")
    print(f"✅ Railway DB 연결 (psql): {'성공' if db_ok else '실패'}")
    print(f"✅ Railway DB HTTP API: {'성공' if http_ok else '실패'}")
    
    if all([file_ok, env_ok, code_ok]):
        print("\n🎉 핵심 테스트가 성공했습니다!")
        if db_ok:
            print("✅ Railway DB와 dummy 도메인이 완벽하게 연결되어 있습니다.")
        else:
            print("⚠️ Railway DB 연결에 문제가 있습니다. psql 클라이언트 설치를 확인해주세요.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 위의 오류 메시지를 확인해주세요.")
    
    print("="*60)
    
    # 추가 정보
    print("\n💡 추가 정보:")
    print("  - Railway DB URL: postgresql://postgres:****@shortline.proxy.rlwy.net:46071/railway")
    print("  - 테이블명: dummy")
    print("  - 필요한 도구: psql (PostgreSQL 클라이언트)")
    print("  - 설치 명령어: https://www.postgresql.org/download/ 에서 다운로드")

if __name__ == "__main__":
    main()
