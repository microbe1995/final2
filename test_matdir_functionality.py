#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MatDir 기능 테스트 스크립트
- 데이터베이스 연결 테스트
- 테이블 생성 테스트
- 데이터 삽입/조회 테스트
- 배출량 계산 테스트
"""

import asyncio
import os
import sys
import logging
from decimal import Decimal
from typing import Dict, Any

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'service', 'cbam-service'))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_matdir_functionality():
    """MatDir 기능 전체 테스트"""
    try:
        logger.info("🚀 MatDir 기능 테스트 시작")
        
        # 1. Repository 임포트 및 초기화
        logger.info("📦 Repository 임포트 중...")
        from app.domain.matdir.matdir_repository import MatDirRepository
        
        # 2. Repository 인스턴스 생성
        logger.info("🏗️ Repository 인스턴스 생성 중...")
        matdir_repo = MatDirRepository()
        
        # 3. 데이터베이스 연결 테스트
        logger.info("🔗 데이터베이스 연결 테스트 중...")
        connection_ok = await matdir_repo.test_connection()
        if not connection_ok:
            logger.error("❌ 데이터베이스 연결 실패")
            return False
        logger.info("✅ 데이터베이스 연결 성공")
        
        # 4. 테이블 생성 테스트
        logger.info("📋 테이블 생성 테스트 중...")
        await matdir_repo._create_matdir_table_async()
        logger.info("✅ 테이블 생성 테스트 완료")
        
        # 5. 테스트 데이터 준비
        logger.info("📝 테스트 데이터 준비 중...")
        test_data = {
            "process_id": 999,  # 테스트용 공정 ID
            "mat_name": "테스트원료",
            "mat_factor": Decimal('0.050000'),
            "mat_amount": Decimal('100'),
            "oxyfactor": Decimal('1.0000'),
            "matdir_em": Decimal('5.000000')  # 100 * 0.05 * 1.0
        }
        logger.info(f"📊 테스트 데이터: {test_data}")
        
        # 6. 데이터 삽입 테스트
        logger.info("💾 데이터 삽입 테스트 중...")
        try:
            result = await matdir_repo.create_matdir(test_data)
            if result:
                logger.info(f"✅ 데이터 삽입 성공: ID {result.get('id')}")
                logger.info(f"📊 삽입된 데이터: {result}")
            else:
                logger.error("❌ 데이터 삽입 실패")
                return False
        except Exception as e:
            logger.error(f"❌ 데이터 삽입 중 에러 발생: {str(e)}")
            return False
        
        # 7. 데이터 조회 테스트
        logger.info("🔍 데이터 조회 테스트 중...")
        try:
            # 전체 목록 조회
            all_matdirs = await matdir_repo.get_matdirs(limit=10)
            logger.info(f"✅ 전체 목록 조회 성공: {len(all_matdirs)}개")
            
            # 공정별 조회
            process_matdirs = await matdir_repo.get_matdirs_by_process(999)
            logger.info(f"✅ 공정별 조회 성공: {len(process_matdirs)}개")
            
            # 특정 데이터 조회
            if result and 'id' in result:
                specific_matdir = await matdir_repo.get_matdir(result['id'])
                if specific_matdir:
                    logger.info(f"✅ 특정 데이터 조회 성공: {specific_matdir}")
                else:
                    logger.error("❌ 특정 데이터 조회 실패")
                    return False
            
        except Exception as e:
            logger.error(f"❌ 데이터 조회 중 에러 발생: {str(e)}")
            return False
        
        # 8. 배출량 계산 테스트
        logger.info("🧮 배출량 계산 테스트 중...")
        try:
            calculated_emission = matdir_repo.calculate_matdir_emission(
                Decimal('100'),  # mat_amount
                Decimal('0.05'),  # mat_factor
                Decimal('1.0')    # oxyfactor
            )
            expected_emission = Decimal('5.0')  # 100 * 0.05 * 1.0
            logger.info(f"✅ 배출량 계산 성공: {calculated_emission}")
            logger.info(f"📊 예상값: {expected_emission}, 실제값: {calculated_emission}")
            
            if calculated_emission == expected_emission:
                logger.info("✅ 배출량 계산 결과 정확")
            else:
                logger.warning("⚠️ 배출량 계산 결과 불일치")
                
        except Exception as e:
            logger.error(f"❌ 배출량 계산 중 에러 발생: {str(e)}")
            return False
        
        # 9. 총 배출량 계산 테스트
        logger.info("📊 총 배출량 계산 테스트 중...")
        try:
            total_emission = await matdir_repo.get_total_matdir_emission_by_process(999)
            logger.info(f"✅ 총 배출량 계산 성공: {total_emission}")
        except Exception as e:
            logger.error(f"❌ 총 배출량 계산 중 에러 발생: {str(e)}")
            return False
        
        # 10. 테스트 데이터 정리
        logger.info("🧹 테스트 데이터 정리 중...")
        try:
            if result and 'id' in result:
                delete_success = await matdir_repo.delete_matdir(result['id'])
                if delete_success:
                    logger.info("✅ 테스트 데이터 삭제 성공")
                else:
                    logger.warning("⚠️ 테스트 데이터 삭제 실패")
        except Exception as e:
            logger.warning(f"⚠️ 테스트 데이터 정리 중 에러: {str(e)}")
        
        logger.info("🎉 모든 테스트 완료!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 모듈 임포트 실패: {str(e)}")
        logger.error("프로젝트 루트에서 실행하거나 PYTHONPATH를 확인하세요.")
        return False
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 예상치 못한 에러: {str(e)}")
        return False

async def test_database_connection_only():
    """데이터베이스 연결만 테스트"""
    try:
        logger.info("🔗 데이터베이스 연결만 테스트 중...")
        
        from app.domain.matdir.matdir_repository import MatDirRepository
        
        matdir_repo = MatDirRepository()
        
        # 연결 테스트
        connection_ok = await matdir_repo.test_connection()
        if connection_ok:
            logger.info("✅ 데이터베이스 연결 성공")
            
            # 간단한 쿼리 테스트
            async with matdir_repo.pool.acquire() as conn:
                result = await conn.fetchval("SELECT version()")
                logger.info(f"📊 PostgreSQL 버전: {result}")
                
                # matdir 테이블 존재 여부 확인
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'matdir'
                    );
                """)
                logger.info(f"📋 matdir 테이블 존재: {table_exists}")
                
                if table_exists:
                    # 테이블 구조 확인
                    columns = await conn.fetch("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = 'matdir'
                        ORDER BY ordinal_position;
                    """)
                    logger.info("📊 matdir 테이블 구조:")
                    for col in columns:
                        logger.info(f"   {col['column_name']}: {col['data_type']} "
                                  f"({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'}) "
                                  f"기본값: {col['column_default']}")
                
        else:
            logger.error("❌ 데이터베이스 연결 실패")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 연결 테스트 실패: {str(e)}")
        return False

async def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("🧪 MatDir 기능 테스트 스크립트")
    logger.info("=" * 60)
    
    # 환경변수 확인
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        logger.error("Railway 환경변수를 확인하거나 .env 파일을 설정하세요.")
        return
    
    logger.info(f"🔧 DATABASE_URL: {database_url[:50]}...")
    
    # 명령행 인수 확인
    if len(sys.argv) > 1 and sys.argv[1] == '--connection-only':
        # 연결만 테스트
        success = await test_database_connection_only()
    else:
        # 전체 기능 테스트
        success = await test_matdir_functionality()
    
    if success:
        logger.info("✅ 테스트 성공!")
        sys.exit(0)
    else:
        logger.error("❌ 테스트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    # asyncio 이벤트 루프 실행
    asyncio.run(main())
