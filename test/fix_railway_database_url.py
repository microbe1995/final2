#!/usr/bin/env python3
"""
Railway 서비스의 DATABASE_URL을 올바른 PostgreSQL 주소로 설정하는 스크립트
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime

async def fix_railway_database_url():
    """Railway 서비스의 DATABASE_URL을 수정합니다."""
    
    # Railway 서비스 URL
    service_url = "https://lcafinal-production.up.railway.app"
    
    # 올바른 PostgreSQL DATABASE_URL
    correct_database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    print(f"🚀 Railway 서비스 DATABASE_URL 수정 시작")
    print(f"📍 서비스 URL: {service_url}")
    print(f"🔧 올바른 DATABASE_URL: {correct_database_url.split('@')[1] if '@' in correct_database_url else correct_database_url}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. 현재 서비스 상태 확인
            print("\n🔍 1. 현재 서비스 상태 확인...")
            try:
                async with session.get(f"{service_url}/docs") as response:
                    if response.status == 200:
                        print("✅ 서비스가 정상적으로 실행 중입니다.")
                    else:
                        print(f"⚠️ 서비스 응답: {response.status}")
            except Exception as e:
                print(f"❌ 서비스 연결 실패: {e}")
                return
            
            # 2. 현재 데이터베이스 연결 상태 확인
            print("\n🔍 2. 현재 데이터베이스 연결 상태 확인...")
            try:
                # process_chain_link 테이블을 사용하는 API 테스트
                async with session.get(f"{service_url}/edge/chain-emission-summary/1") as response:
                    if response.status == 200:
                        print("✅ PostgreSQL 연결이 정상적으로 작동하고 있습니다!")
                        return
                    else:
                        error_text = await response.text()
                        print(f"❌ 현재 데이터베이스 연결 실패: {response.status}")
                        
                        if "sqlite3" in error_text.lower():
                            print("🔍 문제: 서비스가 SQLite를 사용하고 있습니다.")
                            print("💡 해결: Railway 서비스의 DATABASE_URL을 PostgreSQL로 설정해야 합니다.")
                        elif "no such table" in error_text.lower():
                            print("🔍 문제: process_chain_link 테이블에 접근할 수 없습니다.")
                            print("💡 해결: PostgreSQL 연결이 필요합니다.")
                        
            except Exception as e:
                print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
            
            # 3. 해결 방안 제시
            print("\n💡 해결 방안:")
            print("1. Railway 대시보드에서 환경변수 수정:")
            print(f"   DATABASE_URL = {correct_database_url}")
            print("2. 서비스 재배포")
            print("3. API 테스트 재실행")
            
            print("\n📋 Railway 환경변수 설정 방법:")
            print("1. Railway 대시보드 접속")
            print("2. cbam-service 프로젝트 선택")
            print("3. Variables 탭에서 DATABASE_URL 수정")
            print("4. Deploy 버튼 클릭")
            
    except Exception as e:
        print(f"❌ 전체 확인 과정에서 오류 발생: {e}")
    
    print("\n🎯 Railway 서비스 DATABASE_URL 수정 가이드 완료!")

if __name__ == "__main__":
    asyncio.run(fix_railway_database_url())
