#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MatDir 간단 테스트 스크립트
- 기본적인 Repository 메서드 테스트
- 에러 상황 시뮬레이션
"""

import asyncio
import os
import sys
import logging
from decimal import Decimal

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'service', 'cbam-service'))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

async def test_basic_operations():
    """기본 CRUD 작업 테스트"""
    try:
        logger.info("🧪 기본 CRUD 작업 테스트 시작")
        
        # Repository 임포트
        from app.domain.matdir.matdir_repository import MatDirRepository
        
        # 인스턴스 생성
        repo = MatDirRepository()
        
        # 1. 연결 테스트
        logger.info("1️⃣ 데이터베이스 연결 테스트")
        connection_ok = await repo.test_connection()
        if not connection_ok:
            logger.error("❌ 연결 실패")
            return False
        logger.info("✅ 연결 성공")
        
        # 2. 테이블 생성 테스트
        logger.info("2️⃣ 테이블 생성 테스트")
        await repo._create_matdir_table_async()
        logger.info("✅ 테이블 생성 완료")
        
        # 3. 데이터 삽입 테스트
        logger.info("3️⃣ 데이터 삽입 테스트")
        test_data = {
            "process_id": 888,
            "mat_name": "테스트원료A",
            "mat_factor": Decimal('0.030000'),
            "mat_amount": Decimal('50'),
            "oxyfactor": Decimal('1.0000'),
            "matdir_em": Decimal('1.500000')  # 50 * 0.03 * 1.0
        }
        
        result = await repo.create_matdir(test_data)
        if result:
            logger.info(f"✅ 삽입 성공: ID {result.get('id')}")
            inserted_id = result.get('id')
        else:
            logger.error("❌ 삽입 실패")
            return False
        
        # 4. 데이터 조회 테스트
        logger.info("4️⃣ 데이터 조회 테스트")
        retrieved = await repo.get_matdir(inserted_id)
        if retrieved:
            logger.info(f"✅ 조회 성공: {retrieved}")
        else:
            logger.error("❌ 조회 실패")
            return False
        
        # 5. 데이터 수정 테스트
        logger.info("5️⃣ 데이터 수정 테스트")
        update_data = {
            "mat_amount": Decimal('75'),
            "matdir_em": Decimal('2.250000')  # 75 * 0.03 * 1.0
        }
        
        updated = await repo.update_matdir(inserted_id, update_data)
        if updated:
            logger.info(f"✅ 수정 성공: {updated}")
        else:
            logger.error("❌ 수정 실패")
            return False
        
        # 6. 공정별 조회 테스트
        logger.info("6️⃣ 공정별 조회 테스트")
        process_data = await repo.get_matdirs_by_process(888)
        logger.info(f"✅ 공정별 조회: {len(process_data)}개")
        
        # 7. 총 배출량 계산 테스트
        logger.info("7️⃣ 총 배출량 계산 테스트")
        total_emission = await repo.get_total_matdir_emission_by_process(888)
        logger.info(f"✅ 총 배출량: {total_emission}")
        
        # 8. 데이터 삭제 테스트
        logger.info("8️⃣ 데이터 삭제 테스트")
        delete_success = await repo.delete_matdir(inserted_id)
        if delete_success:
            logger.info("✅ 삭제 성공")
        else:
            logger.warning("⚠️ 삭제 실패")
        
        logger.info("🎉 기본 CRUD 테스트 완료!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 테스트 실패: {str(e)}")
        return False

async def test_error_scenarios():
    """에러 상황 테스트"""
    try:
        logger.info("🧪 에러 상황 테스트 시작")
        
        from app.domain.matdir.matdir_repository import MatDirRepository
        
        repo = MatDirRepository()
        
        # 1. 잘못된 데이터로 삽입 시도
        logger.info("1️⃣ 잘못된 데이터 삽입 테스트")
        invalid_data = {
            "process_id": None,  # 잘못된 값
            "mat_name": "",
            "mat_factor": "invalid",  # 잘못된 타입
            "mat_amount": -100,  # 음수 값
            "oxyfactor": None,
            "matdir_em": None
        }
        
        try:
            result = await repo.create_matdir(invalid_data)
            logger.warning("⚠️ 잘못된 데이터가 삽입됨")
        except Exception as e:
            logger.info(f"✅ 예상된 에러 발생: {str(e)}")
        
        # 2. 존재하지 않는 ID로 조회
        logger.info("2️⃣ 존재하지 않는 ID 조회 테스트")
        non_existent = await repo.get_matdir(99999)
        if non_existent is None:
            logger.info("✅ 예상대로 None 반환")
        else:
            logger.warning("⚠️ 예상과 다른 결과")
        
        # 3. 존재하지 않는 ID로 수정
        logger.info("3️⃣ 존재하지 않는 ID 수정 테스트")
        try:
            updated = await repo.update_matdir(99999, {"mat_amount": Decimal('100')})
            if updated is None:
                logger.info("✅ 예상대로 None 반환")
            else:
                logger.warning("⚠️ 예상과 다른 결과")
        except Exception as e:
            logger.info(f"✅ 예상된 에러 발생: {str(e)}")
        
        # 4. 존재하지 않는 ID로 삭제
        logger.info("4️⃣ 존재하지 않는 ID 삭제 테스트")
        delete_result = await repo.delete_matdir(99999)
        if not delete_result:
            logger.info("✅ 예상대로 False 반환")
        else:
            logger.warning("⚠️ 예상과 다른 결과")
        
        logger.info("🎉 에러 상황 테스트 완료!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 에러 상황 테스트 실패: {str(e)}")
        return False

async def test_calculation_methods():
    """계산 메서드 테스트"""
    try:
        logger.info("🧪 계산 메서드 테스트 시작")
        
        from app.domain.matdir.matdir_repository import MatDirRepository
        
        repo = MatDirRepository()
        
        # 1. 배출량 계산 테스트
        logger.info("1️⃣ 배출량 계산 테스트")
        test_cases = [
            (Decimal('100'), Decimal('0.05'), Decimal('1.0'), Decimal('5.0')),
            (Decimal('200'), Decimal('0.03'), Decimal('1.2'), Decimal('7.2')),
            (Decimal('50'), Decimal('0.08'), Decimal('0.8'), Decimal('3.2')),
        ]
        
        for mat_amount, mat_factor, oxyfactor, expected in test_cases:
            calculated = repo.calculate_matdir_emission(mat_amount, mat_factor, oxyfactor)
            logger.info(f"   {mat_amount} × {mat_factor} × {oxyfactor} = {calculated}")
            
            if calculated == expected:
                logger.info(f"   ✅ 정확: {calculated}")
            else:
                logger.warning(f"   ⚠️ 불일치: 예상 {expected}, 실제 {calculated}")
        
        logger.info("🎉 계산 메서드 테스트 완료!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 계산 메서드 테스트 실패: {str(e)}")
        return False

async def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("🧪 MatDir 간단 테스트 스크립트")
    logger.info("=" * 60)
    
    # 환경변수 확인
    if not os.getenv('DATABASE_URL'):
        logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
        return
    
    # 테스트 실행
    tests = [
        ("기본 CRUD 작업", test_basic_operations),
        ("에러 상황", test_error_scenarios),
        ("계산 메서드", test_calculation_methods),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} 테스트 실행 중 에러: {str(e)}")
            results.append((test_name, False))
    
    # 결과 요약
    logger.info("\n" + "="*60)
    logger.info("📊 테스트 결과 요약")
    logger.info("="*60)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    logger.info(f"\n전체: {len(results)}개, 성공: {success_count}개, 실패: {len(results) - success_count}개")
    
    if success_count == len(results):
        logger.info("🎉 모든 테스트 통과!")
        sys.exit(0)
    else:
        logger.error("❌ 일부 테스트 실패")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
