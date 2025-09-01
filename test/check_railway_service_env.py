#!/usr/bin/env python3
"""
Railway 서비스의 환경변수와 데이터베이스 연결 상태를 확인하는 스크립트
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime

async def check_railway_service():
    """Railway 서비스의 상태를 확인합니다."""
    
    # Railway 서비스 URL
    service_url = "https://lcafinal-production.up.railway.app"
    
    print(f"🚀 Railway 서비스 상태 확인 시작")
    print(f"📍 서비스 URL: {service_url}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # 1. 서비스 상태 확인
            print("\n🔍 1. 서비스 상태 확인...")
            try:
                async with session.get(f"{service_url}/docs") as response:
                    if response.status == 200:
                        print("✅ 서비스가 정상적으로 실행 중입니다.")
                        print(f"📊 응답 상태: {response.status}")
                    else:
                        print(f"⚠️ 서비스 응답: {response.status}")
            except Exception as e:
                print(f"❌ 서비스 연결 실패: {e}")
                return
            
            # 2. 환경변수 확인 (가능한 경우)
            print("\n🔍 2. 환경변수 확인...")
            try:
                async with session.get(f"{service_url}/debug/env") as response:
                    if response.status == 200:
                        env_data = await response.json()
                        print("✅ 환경변수 조회 성공!")
                        print(f"📊 DATABASE_URL: {env_data.get('DATABASE_URL', '설정되지 않음')}")
                    else:
                        print(f"⚠️ 환경변수 조회 실패: {response.status}")
            except Exception as e:
                print(f"ℹ️ 환경변수 조회 불가: {e}")
            
            # 3. 데이터베이스 연결 테스트
            print("\n🔍 3. 데이터베이스 연결 테스트...")
            try:
                # 간단한 API 엔드포인트 테스트
                async with session.get(f"{service_url}/edge/continue-edges/156") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ 데이터베이스 연결 성공!")
                        print(f"📊 응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    else:
                        error_text = await response.text()
                        print(f"❌ 데이터베이스 연결 실패: {response.status}")
                        print(f"오류 내용: {error_text}")
                        
                        # 오류 분석
                        if "sqlite3" in error_text.lower():
                            print("🔍 문제: 서비스가 SQLite를 사용하고 있습니다.")
                            print("💡 해결: Railway 서비스의 DATABASE_URL을 PostgreSQL로 설정해야 합니다.")
                        elif "no such table" in error_text.lower():
                            print("🔍 문제: 테이블이 존재하지 않습니다.")
                            print("💡 해결: 데이터베이스 스키마를 확인해야 합니다.")
                        
            except Exception as e:
                print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
            
            # 4. 서비스 정보 확인
            print("\n🔍 4. 서비스 정보 확인...")
            try:
                async with session.get(f"{service_url}/info") as response:
                    if response.status == 200:
                        info_data = await response.json()
                        print("✅ 서비스 정보 조회 성공!")
                        print(f"📊 서비스 정보: {json.dumps(info_data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"ℹ️ 서비스 정보 엔드포인트 없음: {response.status}")
            except Exception as e:
                print(f"ℹ️ 서비스 정보 조회 불가: {e}")
    
    except Exception as e:
        print(f"❌ 전체 확인 과정에서 오류 발생: {e}")
    
    print("\n🎯 Railway 서비스 상태 확인 완료!")

if __name__ == "__main__":
    asyncio.run(check_railway_service())
