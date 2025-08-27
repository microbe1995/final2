#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import time

def run_script(script_name, description):
    """스크립트 실행"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"📁 실행 파일: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"✅ {description} 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패!")
        print(f"오류: {e.stderr}")
        return False

def main():
    """DB 확장 스크립트들을 순서대로 실행"""
    
    print("🔧 CBAM DB 스키마 확장 시작")
    print("📋 실행 순서:")
    print("1. 배출계수 테이블 생성")
    print("2. 배출량 귀속 테이블 생성")
    print("3. process_input 테이블 확장")
    
    # 실행할 스크립트들
    scripts = [
        ("create_emission_factors_table.py", "배출계수 테이블 생성"),
        ("create_emission_attribution_table.py", "배출량 귀속 테이블 생성"),
        ("expand_process_input_table.py", "process_input 테이블 확장")
    ]
    
    success_count = 0
    
    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"⚠️ {description} 실패로 중단합니다.")
            break
        
        # 스크립트 간 잠시 대기
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"📊 실행 결과: {success_count}/{len(scripts)} 성공")
    
    if success_count == len(scripts):
        print("🎉 모든 DB 확장이 성공적으로 완료되었습니다!")
        print("\n📋 확장된 DB 구조:")
        print("✅ emission_factors - 배출계수 데이터")
        print("✅ emission_attribution - 배출량 귀속 정보")
        print("✅ product_emissions - 제품별 총 배출량")
        print("✅ process_input - CBAM 규정 준수 확장")
    else:
        print("❌ 일부 스크립트 실행에 실패했습니다.")
        print("개별 스크립트를 수동으로 실행해주세요.")

if __name__ == "__main__":
    main()
