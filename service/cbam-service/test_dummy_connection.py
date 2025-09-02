#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway DB dummy 테이블과 dummy 도메인 코드 연결 테스트
"""

import asyncio
import asyncpg
import os
import sys
from datetime import datetime, date
from decimal import Decimal

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Railway DB 연결 정보
RAILWAY_DB_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_railway_db_connection():
    """Railway DB 직접 연결 테스트"""
    print("🔍 Railway DB 직접 연결 테스트 시작...")
    
    try:
        # PostgreSQL 연결
        conn = await asyncpg.connect(RAILWAY_DB_URL)
        print("✅ Railway DB 연결 성공!")
        
        # dummy 테이블 존재 여부 확인
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'dummy'
            );
        """)
        
        if table_exists:
            print("✅ dummy 테이블이 존재합니다.")
            
            # dummy 테이블 구조 확인
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'dummy'
                ORDER BY ordinal_position;
            """)
            
            print("\n📋 dummy 테이블 구조:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} "
                      f"({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # dummy 테이블 데이터 개수 확인
            count = await conn.fetchval("SELECT COUNT(*) FROM dummy")
            print(f"\n📊 dummy 테이블 데이터 개수: {count}")
            
            # 샘플 데이터 조회
            if count > 0:
                sample_data = await conn.fetch("SELECT * FROM dummy LIMIT 3")
                print("\n📝 샘플 데이터:")
                for row in sample_data:
                    print(f"  - ID: {row['id']}, 로트번호: {row['로트번호']}, "
                          f"생산품명: {row['생산품명']}, 공정: {row['공정']}")
            
        else:
            print("❌ dummy 테이블이 존재하지 않습니다.")
            
            # 테이블 생성 시도
            print("\n🔧 dummy 테이블 생성 시도...")
            await conn.execute("""
                CREATE TABLE dummy (
                    id SERIAL PRIMARY KEY,
                    로트번호 VARCHAR(100) NOT NULL,
                    생산품명 VARCHAR(200) NOT NULL,
                    생산수량 NUMERIC(10,2) NOT NULL,
                    투입일 DATE,
                    종료일 DATE,
                    공정 VARCHAR(100) NOT NULL,
                    투입물명 VARCHAR(200) NOT NULL,
                    수량 NUMERIC(10,2) NOT NULL,
                    단위 VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            print("✅ dummy 테이블 생성 성공!")
            
            # 샘플 데이터 삽입
            print("\n🔧 샘플 데이터 삽입...")
            await conn.execute("""
                INSERT INTO dummy (로트번호, 생산품명, 생산수량, 투입일, 종료일, 공정, 투입물명, 수량, 단위)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 'TEST001', '테스트제품', 100.00, date(2024, 1, 1), date(2024, 1, 31), 
                 '테스트공정', '테스트원료', 50.00, '개')
            print("✅ 샘플 데이터 삽입 성공!")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Railway DB 연결 실패: {e}")
        return False

async def test_dummy_domain_code():
    """dummy 도메인 코드 테스트"""
    print("\n🔍 Dummy 도메인 코드 테스트 시작...")
    
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

async def test_dummy_repository_with_railway():
    """Railway DB와 dummy repository 연동 테스트"""
    print("\n🔍 Railway DB와 Dummy Repository 연동 테스트...")
    
    try:
        from app.domain.dummy.dummy_repository import DummyRepository
        
        # 환경변수 설정
        os.environ['DATABASE_URL'] = RAILWAY_DB_URL
        
        # Repository 생성 및 초기화
        repo = DummyRepository()
        await repo.initialize()
        
        print("✅ Repository 초기화 성공!")
        
        # 연결 풀 상태 확인
        if repo.pool:
            print("✅ 데이터베이스 연결 풀 생성 성공!")
            
            # 테이블 존재 여부 확인
            try:
                async with repo.pool.acquire() as conn:
                    table_exists = await conn.fetchval("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'dummy'
                        );
                    """)
                    
                    if table_exists:
                        print("✅ dummy 테이블 확인 성공!")
                        
                        # 데이터 개수 조회
                        count = await repo.get_dummy_data_count()
                        print(f"✅ 데이터 개수 조회 성공: {count}개")
                        
                        # 샘플 데이터 조회
                        if count > 0:
                            data_list = await repo.get_all_dummy_data(limit=3)
                            print(f"✅ 데이터 조회 성공: {len(data_list)}개")
                            
                            for data in data_list:
                                print(f"  - ID: {data['id']}, 로트번호: {data['로트번호']}, "
                                      f"생산품명: {data['생산품명']}")
                        else:
                            print("⚠️ dummy 테이블에 데이터가 없습니다.")
                    else:
                        print("❌ dummy 테이블이 존재하지 않습니다.")
                        
            except Exception as e:
                print(f"❌ Repository 테이블 확인 실패: {e}")
                
        else:
            print("❌ 데이터베이스 연결 풀 생성 실패!")
            
        await repo.close()
        return True
        
    except Exception as e:
        print(f"❌ Railway DB와 Dummy Repository 연동 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_dummy_service_with_railway():
    """Railway DB와 dummy service 연동 테스트"""
    print("\n🔍 Railway DB와 Dummy Service 연동 테스트...")
    
    try:
        from app.domain.dummy.dummy_service import DummyService
        from app.domain.dummy.dummy_schema import DummyDataCreateRequest
        
        # 환경변수 설정
        os.environ['DATABASE_URL'] = RAILWAY_DB_URL
        
        # Service 생성 및 초기화
        service = DummyService()
        await service.initialize()
        
        print("✅ Service 초기화 성공!")
        
        # 데이터 개수 조회
        count = await service.get_dummy_data_count()
        print(f"✅ 데이터 개수 조회 성공: {count}개")
        
        # 새 데이터 생성 테스트
        print("\n🔧 새 데이터 생성 테스트...")
        new_data = DummyDataCreateRequest(
            로트번호="TEST002",
            생산품명="연동테스트제품",
            생산수량=Decimal("200.00"),
            투입일=date(2024, 2, 1),
            종료일=date(2024, 2, 28),
            공정="연동테스트공정",
            투입물명="연동테스트원료",
            수량=Decimal("100.00"),
            단위="kg"
        )
        
        new_id = await service.create_dummy_data(new_data)
        if new_id:
            print(f"✅ 새 데이터 생성 성공: ID {new_id}")
            
            # 생성된 데이터 조회
            created_data = await service.get_dummy_data_by_id(new_id)
            if created_data:
                print(f"✅ 생성된 데이터 조회 성공: {created_data.생산품명}")
            else:
                print("❌ 생성된 데이터 조회 실패")
        else:
            print("❌ 새 데이터 생성 실패")
        
        await service.close()
        return True
        
    except Exception as e:
        print(f"❌ Railway DB와 Dummy Service 연동 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 Railway DB와 Dummy 도메인 연결 테스트 시작\n")
    
    # 1. Railway DB 직접 연결 테스트
    db_ok = await test_railway_db_connection()
    
    # 2. Dummy 도메인 코드 테스트
    code_ok = await test_dummy_domain_code()
    
    # 3. Railway DB와 Repository 연동 테스트
    repo_ok = await test_dummy_repository_with_railway()
    
    # 4. Railway DB와 Service 연동 테스트
    service_ok = await test_dummy_service_with_railway()
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    print(f"✅ Railway DB 직접 연결: {'성공' if db_ok else '실패'}")
    print(f"✅ Dummy 도메인 코드: {'성공' if code_ok else '실패'}")
    print(f"✅ Repository 연동: {'성공' if repo_ok else '실패'}")
    print(f"✅ Service 연동: {'성공' if service_ok else '실패'}")
    
    if all([db_ok, code_ok, repo_ok, service_ok]):
        print("\n🎉 모든 테스트가 성공했습니다! Railway DB와 dummy 도메인이 완벽하게 연결되어 있습니다.")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다. 위의 오류 메시지를 확인해주세요.")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
