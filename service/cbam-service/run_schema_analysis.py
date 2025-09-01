#!/usr/bin/env python3
"""
Railway 환경에서 DB 스키마 분석을 실행하는 스크립트
환경변수를 자동으로 설정하고 스크립트를 실행합니다.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """메인 실행 함수"""
    
    print("🚀 Railway DB 스키마 분석 실행")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    current_dir = Path.cwd()
    print(f"📍 현재 디렉토리: {current_dir}")
    
    # analyze_db_schema.py 파일 존재 확인
    schema_script = current_dir / "analyze_db_schema.py"
    if not schema_script.exists():
        print(f"❌ {schema_script} 파일을 찾을 수 없습니다.")
        return
    
    print(f"✅ 스키마 분석 스크립트 발견: {schema_script}")
    
    # 환경변수 확인
    print("\n🔧 환경변수 확인:")
    database_url = os.getenv("DATABASE_URL")
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    
    if database_url:
        # 민감한 정보 가리기
        masked_url = database_url.replace(
            database_url.split('@')[0].split(':')[2], '***'
        ) if '@' in database_url else '***'
        print(f"  ✅ DATABASE_URL: {masked_url}")
    else:
        print("  ❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        print("  💡 Railway 환경변수를 확인해주세요.")
        return
    
    if railway_env:
        print(f"  ✅ RAILWAY_ENVIRONMENT: {railway_env}")
    else:
        print("  ⚠️ RAILWAY_ENVIRONMENT 환경변수가 설정되지 않았습니다.")
    
    # 스크립트 실행
    print(f"\n🔍 스키마 분석 스크립트 실행 중...")
    print("=" * 50)
    
    try:
        # Python 스크립트 실행
        result = subprocess.run([
            sys.executable, str(schema_script)
        ], capture_output=True, text=True, env=os.environ)
        
        # 출력 결과 표시
        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("⚠️ STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ 스키마 분석 완료!")
            
            # 결과 파일 확인
            result_file = current_dir / "db_schema_analysis.json"
            if result_file.exists():
                print(f"📁 분석 결과 파일: {result_file}")
                
                # 파일 크기 확인
                file_size = result_file.stat().st_size
                print(f"📊 파일 크기: {file_size} bytes")
                
                # 파일 내용 미리보기
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"\n📋 파일 내용 미리보기 (처음 500자):")
                        print("-" * 50)
                        print(content[:500])
                        if len(content) > 500:
                            print("... (이하 생략)")
                except Exception as e:
                    print(f"❌ 파일 읽기 실패: {e}")
            else:
                print("❌ 분석 결과 파일을 찾을 수 없습니다.")
        else:
            print(f"\n❌ 스크립트 실행 실패 (종료 코드: {result.returncode})")
            
    except Exception as e:
        print(f"❌ 스크립트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 다음 단계:")
    print("1. 분석 결과 파일 확인")
    print("2. 스키마 확장 계획 수립")
    print("3. DB 마이그레이션 스크립트 작성")

if __name__ == "__main__":
    main()
