#!/usr/bin/env python3
"""
TypeScript 빌드 에러 검사 스크립트
Next.js 프로젝트의 TypeScript 컴파일 에러를 미리 검사합니다.
"""

import os
import subprocess
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

class TypeScriptBuildChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.frontend_dir = self.project_root / "frontend"
        self.errors = []
        self.warnings = []
        
    def check_project_structure(self) -> bool:
        """프로젝트 구조 확인"""
        print("🔍 프로젝트 구조 확인 중...")
        
        if not self.frontend_dir.exists():
            print("❌ frontend 디렉토리를 찾을 수 없습니다.")
            return False
            
        if not (self.frontend_dir / "package.json").exists():
            print("❌ package.json을 찾을 수 없습니다.")
            return False
            
        if not (self.frontend_dir / "tsconfig.json").exists():
            print("❌ tsconfig.json을 찾을 수 없습니다.")
            return False
            
        print("✅ 프로젝트 구조 확인 완료")
        return True
    
    def check_typescript_compilation(self) -> bool:
        """TypeScript 컴파일 에러 검사"""
        print("🔍 TypeScript 컴파일 에러 검사 중...")
        
        try:
            # TypeScript 컴파일러로 타입 체크만 실행
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--project", str(self.frontend_dir / "tsconfig.json")],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ TypeScript 컴파일 에러 없음")
                return True
            else:
                # 에러 출력 파싱
                self.parse_typescript_errors(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ TypeScript 컴파일 타임아웃")
            return False
        except Exception as e:
            print(f"❌ TypeScript 컴파일 검사 실패: {e}")
            return False
    
    def parse_typescript_errors(self, stderr: str):
        """TypeScript 에러 출력 파싱"""
        lines = stderr.strip().split('\n')
        
        for line in lines:
            if line.strip():
                if 'error' in line.lower():
                    self.errors.append(line)
                elif 'warning' in line.lower():
                    self.warnings.append(line)
    
    def check_missing_imports(self) -> bool:
        """누락된 import 확인"""
        print("🔍 누락된 import 확인 중...")
        
        # @/lib/env 참조 검사
        env_imports = []
        
        for tsx_file in self.frontend_dir.rglob("*.tsx"):
            try:
                with open(tsx_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '@/lib/env' in content:
                        env_imports.append(str(tsx_file.relative_to(self.project_root)))
            except Exception as e:
                print(f"⚠️ 파일 읽기 실패: {tsx_file} - {e}")
        
        if env_imports:
            print(f"❌ @/lib/env import가 남아있는 파일들:")
            for file_path in env_imports:
                print(f"   - {file_path}")
            return False
        else:
            print("✅ @/lib/env import 모두 제거됨")
            return True
    
    def check_vercel_json(self) -> bool:
        """vercel.json 파일 존재 여부 확인"""
        print("🔍 vercel.json 파일 확인 중...")
        
        vercel_json = self.frontend_dir / "vercel.json"
        if vercel_json.exists():
            print("❌ vercel.json 파일이 아직 존재합니다.")
            return False
        else:
            print("✅ vercel.json 파일 삭제됨")
            return True
    
    def run_all_checks(self) -> bool:
        """모든 검사 실행"""
        print("🚀 TypeScript 빌드 에러 검사 시작\n")
        
        checks = [
            ("프로젝트 구조", self.check_project_structure),
            ("vercel.json 삭제", self.check_vercel_json),
            ("@/lib/env import", self.check_missing_imports),
            ("TypeScript 컴파일", self.check_typescript_compilation),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"\n📋 {check_name} 검사...")
            if not check_func():
                all_passed = False
                print(f"❌ {check_name} 검사 실패")
            else:
                print(f"✅ {check_name} 검사 통과")
        
        return all_passed
    
    def print_summary(self):
        """검사 결과 요약 출력"""
        print("\n" + "="*50)
        print("📊 검사 결과 요약")
        print("="*50)
        
        if self.errors:
            print(f"\n❌ 에러 ({len(self.errors)}개):")
            for error in self.errors[:10]:  # 최대 10개만 출력
                print(f"   {error}")
            if len(self.errors) > 10:
                print(f"   ... 및 {len(self.errors) - 10}개 더")
        
        if self.warnings:
            print(f"\n⚠️ 경고 ({len(self.warnings)}개):")
            for warning in self.warnings[:5]:  # 최대 5개만 출력
                print(f"   {warning}")
            if len(self.warnings) > 5:
                print(f"   ... 및 {len(self.warnings) - 5}개 더")
        
        if not self.errors and not self.warnings:
            print("\n🎉 모든 검사 통과! 빌드 준비 완료!")

def main():
    # 프로젝트 루트 디렉토리
    project_root = Path(__file__).parent.parent
    
    print(f"🏠 프로젝트 루트: {project_root}")
    
    # 검사기 생성 및 실행
    checker = TypeScriptBuildChecker(project_root)
    success = checker.run_all_checks()
    
    # 결과 출력
    checker.print_summary()
    
    # 종료 코드
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
