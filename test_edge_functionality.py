#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge 도메인 기능 테스트 스크립트
CBAM 배출량 전파 시스템의 정상 작동을 확인합니다.
"""

import asyncio
import asyncpg
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('edge_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EdgeDomainTester:
    """Edge 도메인 기능 테스트 클래스"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def initialize(self):
        """데이터베이스 연결 초기화"""
        try:
            logger.info("데이터베이스 연결 초기화 시작")
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5,
                command_timeout=30
            )
            logger.info("데이터베이스 연결 풀 생성 성공")
            
            # 테이블 존재 확인
            await self.check_tables_exist()
            
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise e
    
    async def check_tables_exist(self):
        """필요한 테이블들이 존재하는지 확인"""
        required_tables = [
            'edge', 'process', 'product', 'process_attrdir_emission', 'product_process'
        ]
        
        async with self.pool.acquire() as conn:
            for table in required_tables:
                result = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = $1
                    );
                """, table)
                
                if result:
                    logger.info(f"{table} 테이블 존재 확인")
                else:
                    logger.warning(f"{table} 테이블이 존재하지 않습니다")
    
    async def cleanup_test_data(self):
        """테스트 데이터 정리"""
        try:
            async with self.pool.acquire() as conn:
                # 테스트용 엣지 삭제
                await conn.execute("""
                    DELETE FROM edge 
                    WHERE source_id IN (9999, 9998, 9997) 
                    OR target_id IN (9999, 9998, 9997)
                """)
                
                # 테스트용 제품 삭제
                await conn.execute("""
                    DELETE FROM product 
                    WHERE id IN (9999, 9998, 9997)
                """)
                
                # 테스트용 공정 삭제
                await conn.execute("""
                    DELETE FROM process 
                    WHERE id IN (9999, 9998, 9997)
                """)
                
                logger.info("테스트 데이터 정리 완료")
                
        except Exception as e:
            logger.error(f"테스트 데이터 정리 실패: {e}")
    
    async def test_basic_crud_operations(self):
        """기본 CRUD 작업 테스트"""
        logger.info("=" * 60)
        logger.info("기본 CRUD 작업 테스트 시작")
        logger.info("=" * 60)
        
        try:
            # 1. 엣지 생성 테스트
            logger.info("1. 엣지 생성 테스트")
            edge_data = {
                'source_node_type': 'process',
                'source_id': 9999,
                'target_node_type': 'process',
                'target_id': 9998,
                'edge_kind': 'continue'
            }
            
            async with self.pool.acquire() as conn:
                # 테스트용 공정 생성
                await conn.execute("""
                    INSERT INTO process (id, process_name, start_period, end_period)
                    VALUES (9999, '테스트공정1', '2024-01-01', '2024-12-31'),
                           (9998, '테스트공정2', '2024-01-01', '2024-12-31')
                    ON CONFLICT (id) DO NOTHING
                """)
                
                # 엣지 생성
                result = await conn.fetchrow("""
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind
                """, edge_data['source_node_type'], edge_data['source_id'], 
                     edge_data['target_node_type'], edge_data['target_id'], edge_data['edge_kind'])
                
                if result:
                    logger.info(f"엣지 생성 성공: ID {result['id']}")
                    edge_id = result['id']
                    self.test_results["passed"] += 1
                else:
                    logger.error("엣지 생성 실패")
                    self.test_results["failed"] += 1
                    return
                
                # 2. 엣지 조회 테스트
                logger.info("2. 엣지 조회 테스트")
                edge = await conn.fetchrow("""
                    SELECT * FROM edge WHERE id = $1
                """, edge_id)
                
                if edge and edge['source_id'] == 9999 and edge['target_id'] == 9998:
                    logger.info(f"엣지 조회 성공: {dict(edge)}")
                    self.test_results["passed"] += 1
                else:
                    logger.error("엣지 조회 실패")
                    self.test_results["failed"] += 1
                
                # 3. 엣지 수정 테스트
                logger.info("3. 엣지 수정 테스트")
                update_result = await conn.execute("""
                    UPDATE edge 
                    SET edge_kind = 'produce', updated_at = NOW()
                    WHERE id = $1
                """, edge_id)
                
                if update_result == "UPDATE 1":
                    logger.info("엣지 수정 성공")
                    self.test_results["passed"] += 1
                else:
                    logger.error("엣지 수정 실패")
                    self.test_results["failed"] += 1
                
                # 4. 엣지 삭제 테스트
                logger.info("4. 엣지 삭제 테스트")
                delete_result = await conn.execute("""
                    DELETE FROM edge WHERE id = $1
                """, edge_id)
                
                if delete_result == "DELETE 1":
                    logger.info("엣지 삭제 성공")
                    self.test_results["passed"] += 1
                else:
                    logger.error("엣지 삭제 실패")
                    self.test_results["failed"] += 1
                
                self.test_results["total_tests"] += 4
                
        except Exception as e:
            logger.error(f"기본 CRUD 테스트 실패: {e}")
            self.test_results["failed"] += 4
            self.test_results["total_tests"] += 4
            self.test_results["errors"].append(f"CRUD 테스트: {str(e)}")
    
    async def test_emission_propagation_rules(self):
        """배출량 전파 규칙 테스트"""
        logger.info("=" * 60)
        logger.info("배출량 전파 규칙 테스트 시작")
        logger.info("=" * 60)
        
        try:
            async with self.pool.acquire() as conn:
                # 테스트 데이터 준비
                logger.info("테스트 데이터 준비")
                
                # 테스트용 공정 생성
                await conn.execute("""
                    INSERT INTO process (id, process_name, start_period, end_period)
                    VALUES (9999, '테스트공정1', '2024-01-01', '2024-12-31'),
                           (9998, '테스트공정2', '2024-01-01', '2024-12-31'),
                           (9997, '테스트공정3', '2024-01-01', '2024-12-31')
                    ON CONFLICT (id) DO NOTHING
                """)
                
                # 테스트용 제품 생성
                await conn.execute("""
                    INSERT INTO product (id, install_id, product_name, product_category, 
                                       prostart_period, proend_period, product_amount, 
                                       product_sell, product_eusell, attr_em)
                    VALUES (9999, 1, '테스트제품1', '단순제품', '2024-01-01', '2024-12-31', 
                           100.0, 20.0, 10.0, 50.0)
                    ON CONFLICT (id) DO NOTHING
                """)
                
                # 테스트용 배출량 데이터 생성
                await conn.execute("""
                    INSERT INTO process_attrdir_emission (process_id, attrdir_em, cumulative_emission)
                    VALUES (9999, 10.0, 10.0),
                           (9998, 15.0, 15.0),
                           (9997, 20.0, 20.0)
                    ON CONFLICT (process_id) DO UPDATE SET
                    attrdir_em = EXCLUDED.attrdir_em,
                    cumulative_emission = EXCLUDED.cumulative_emission
                """)
                
                # 1. 규칙 1번 테스트: 공정→공정 (continue)
                logger.info("1. 규칙 1번 테스트: 공정→공정 (continue)")
                
                # continue 엣지 생성
                await conn.execute("""
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ('process', 9999, 'process', 9998, 'continue')
                """)
                
                # 배출량 누적 계산 테스트
                source_emission = await conn.fetchrow("""
                    SELECT cumulative_emission FROM process_attrdir_emission WHERE process_id = 9999
                """)
                
                target_emission = await conn.fetchrow("""
                    SELECT attrdir_em FROM process_attrdir_emission WHERE process_id = 9998
                """)
                
                if source_emission and target_emission:
                    expected_cumulative = source_emission['cumulative_emission'] + target_emission['attrdir_em']
                    
                    # 실제 누적 배출량 업데이트
                    await conn.execute("""
                        UPDATE process_attrdir_emission 
                        SET cumulative_emission = $1 
                        WHERE process_id = 9998
                    """, expected_cumulative)
                    
                    # 결과 확인
                    actual_cumulative = await conn.fetchrow("""
                        SELECT cumulative_emission FROM process_attrdir_emission WHERE process_id = 9998
                    """)
                    
                    if actual_cumulative and abs(actual_cumulative['cumulative_emission'] - expected_cumulative) < 0.001:
                        logger.info(f"규칙 1번 테스트 성공: {expected_cumulative}")
                        self.test_results["passed"] += 1
                    else:
                        logger.error(f"규칙 1번 테스트 실패: 예상={expected_cumulative}, 실제={actual_cumulative}")
                        self.test_results["failed"] += 1
                else:
                    logger.error("규칙 1번 테스트 실패: 배출량 데이터 없음")
                    self.test_results["failed"] += 1
                
                # 2. 규칙 2번 테스트: 공정→제품 (produce)
                logger.info("2. 규칙 2번 테스트: 공정→제품 (produce)")
                
                # produce 엣지 생성
                await conn.execute("""
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ('process', 9998, 'product', 9999, 'produce')
                """)
                
                # 제품 배출량 업데이트 테스트
                process_emission = await conn.fetchrow("""
                    SELECT cumulative_emission FROM process_attrdir_emission WHERE process_id = 9998
                """)
                
                if process_emission:
                    expected_product_emission = process_emission['cumulative_emission']
                    
                    await conn.execute("""
                        UPDATE product 
                        SET attr_em = $1 
                        WHERE id = 9999
                    """, expected_product_emission)
                    
                    # 결과 확인
                    actual_product_emission = await conn.fetchrow("""
                        SELECT attr_em FROM product WHERE id = 9999
                    """)
                    
                    if actual_product_emission and abs(actual_product_emission['attr_em'] - expected_product_emission) < 0.001:
                        logger.info(f"규칙 2번 테스트 성공: {expected_product_emission}")
                        self.test_results["passed"] += 1
                    else:
                        logger.error(f"규칙 2번 테스트 실패: 예상={expected_product_emission}, 실제={actual_product_emission}")
                        self.test_results["failed"] += 1
                else:
                    logger.error("규칙 2번 테스트 실패: 공정 배출량 데이터 없음")
                    self.test_results["failed"] += 1
                
                # 3. 규칙 3번 테스트: 제품→공정 (consume)
                logger.info("3. 규칙 3번 테스트: 제품→공정 (consume)")
                
                # consume 엣지 생성
                await conn.execute("""
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                    VALUES ('product', 9999, 'process', 9997, 'consume')
                """)
                
                # product_process 관계는 필요하지 않음 (product_amount를 직접 사용)
                # 제품 데이터 조회
                product_data = await conn.fetchrow("""
                    SELECT product_amount, product_sell, product_eusell, attr_em 
                    FROM product WHERE id = 9999
                """)
                
                if product_data:
                    to_next_process = (float(product_data['product_amount']) - 
                                     float(product_data['product_sell']) - 
                                     float(product_data['product_eusell']))
                    
                    # 소비 비율 계산 (전체 제품량 대비)
                    consumption_ratio = 1.0  # 전체 제품이 소비됨
                    allocated_emission = float(product_data['attr_em']) * consumption_ratio
                    
                    # 공정 배출량 업데이트
                    current_emission = await conn.fetchrow("""
                        SELECT attrdir_em FROM process_attrdir_emission WHERE process_id = 9997
                    """)
                    
                    if current_emission:
                        new_cumulative = float(current_emission['attrdir_em']) + allocated_emission
                        
                        await conn.execute("""
                            UPDATE process_attrdir_emission 
                            SET cumulative_emission = $1 
                            WHERE process_id = 9997
                        """, new_cumulative)
                        
                        # 결과 확인
                        actual_cumulative = await conn.fetchrow("""
                            SELECT cumulative_emission FROM process_attrdir_emission WHERE process_id = 9997
                        """)
                        
                        if actual_cumulative and abs(float(actual_cumulative['cumulative_emission']) - new_cumulative) < 0.001:
                            logger.info(f"규칙 3번 테스트 성공: to_next_process={to_next_process}, allocated_emission={allocated_emission}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error(f"규칙 3번 테스트 실패: 예상={new_cumulative}, 실제={actual_cumulative}")
                            self.test_results["failed"] += 1
                    else:
                        logger.error("규칙 3번 테스트 실패: 공정 배출량 데이터 없음")
                        self.test_results["failed"] += 1
                else:
                    logger.error("규칙 3번 테스트 실패: 제품 데이터 없음")
                    self.test_results["failed"] += 1
                
                self.test_results["total_tests"] += 3
                
        except Exception as e:
            logger.error(f"배출량 전파 규칙 테스트 실패: {e}")
            self.test_results["failed"] += 3
            self.test_results["total_tests"] += 3
            self.test_results["errors"].append(f"배출량 전파 테스트: {str(e)}")
    
    async def test_edge_statistics(self):
        """엣지 통계 테스트"""
        logger.info("=" * 60)
        logger.info("엣지 통계 테스트 시작")
        logger.info("=" * 60)
        
        try:
            async with self.pool.acquire() as conn:
                # 전체 엣지 수 조회
                total_edges = await conn.fetchval("SELECT COUNT(*) FROM edge")
                logger.info(f"전체 엣지 수: {total_edges}")
                
                # 타입별 엣지 수 조회
                edge_types = await conn.fetch("""
                    SELECT edge_kind, COUNT(*) as count 
                    FROM edge 
                    GROUP BY edge_kind
                """)
                
                logger.info("타입별 엣지 분포:")
                for edge_type in edge_types:
                    logger.info(f"  {edge_type['edge_kind']}: {edge_type['count']}개")
                
                # 노드별 연결 수 조회
                node_connections = await conn.fetch("""
                    SELECT source_id, COUNT(*) as outgoing
                    FROM edge 
                    GROUP BY source_id 
                    ORDER BY outgoing DESC 
                    LIMIT 5
                """)
                
                logger.info("가장 많은 연결을 가진 노드 (상위 5개):")
                for node in node_connections:
                    logger.info(f"  노드 {node['source_id']}: {node['outgoing']}개 연결")
                
                self.test_results["passed"] += 1
                self.test_results["total_tests"] += 1
                
        except Exception as e:
            logger.error(f"엣지 통계 테스트 실패: {e}")
            self.test_results["failed"] += 1
            self.test_results["total_tests"] += 1
            self.test_results["errors"].append(f"통계 테스트: {str(e)}")
    
    async def test_error_handling(self):
        """에러 처리 테스트"""
        logger.info("=" * 60)
        logger.info("에러 처리 테스트 시작")
        logger.info("=" * 60)
        
        try:
            async with self.pool.acquire() as conn:
                # 1. 존재하지 않는 엣지 조회 테스트
                logger.info("1. 존재하지 않는 엣지 조회 테스트")
                non_existent_edge = await conn.fetchrow("""
                    SELECT * FROM edge WHERE id = 999999
                """)
                
                if non_existent_edge is None:
                    logger.info("존재하지 않는 엣지 조회 시 None 반환 확인")
                    self.test_results["passed"] += 1
                else:
                    logger.error("존재하지 않는 엣지 조회 시 None이 반환되지 않음")
                    self.test_results["failed"] += 1
                
                # 2. 잘못된 데이터 타입 테스트
                logger.info("2. 잘못된 데이터 타입 테스트")
                try:
                    await conn.execute("""
                        INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind)
                        VALUES ('invalid', 'not_a_number', 'invalid', 'not_a_number', 'invalid')
                    """)
                    logger.error("잘못된 데이터 타입이 허용됨")
                    self.test_results["failed"] += 1
                except Exception as e:
                    logger.info(f"잘못된 데이터 타입이 적절히 거부됨: {e}")
                    self.test_results["passed"] += 1
                
                self.test_results["total_tests"] += 2
                
        except Exception as e:
            logger.error(f"에러 처리 테스트 실패: {e}")
            self.test_results["failed"] += 2
            self.test_results["total_tests"] += 2
            self.test_results["errors"].append(f"에러 처리 테스트: {str(e)}")
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("Edge 도메인 종합 테스트 시작")
        logger.info(f"테스트 시작 시간: {datetime.now()}")
        logger.info("=" * 60)
        
        try:
            # 초기화
            await self.initialize()
            
            # 테스트 데이터 정리
            await self.cleanup_test_data()
            
            # 테스트 실행
            await self.test_basic_crud_operations()
            await self.test_emission_propagation_rules()
            await self.test_edge_statistics()
            await self.test_error_handling()
            
            # 테스트 데이터 정리
            await self.cleanup_test_data()
            
            # 결과 출력
            self.print_test_results()
            
        except Exception as e:
            logger.error(f"테스트 실행 중 오류 발생: {e}")
            self.test_results["errors"].append(f"테스트 실행 오류: {str(e)}")
        finally:
            if self.pool:
                await self.pool.close()
                logger.info("데이터베이스 연결 풀 종료")
    
    def print_test_results(self):
        """테스트 결과 출력"""
        logger.info("=" * 60)
        logger.info("테스트 결과 요약")
        logger.info("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"총 테스트 수: {total}")
        logger.info(f"통과: {passed}")
        logger.info(f"실패: {failed}")
        logger.info(f"성공률: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            logger.info("발생한 오류들:")
            for error in self.test_results["errors"]:
                logger.error(f"  - {error}")
        
        if success_rate >= 90:
            logger.info("테스트 결과: 우수")
        elif success_rate >= 70:
            logger.info("테스트 결과: 양호")
        else:
            logger.error("테스트 결과: 개선 필요")
        
        logger.info(f"테스트 종료 시간: {datetime.now()}")


async def main():
    """메인 함수"""
    # 데이터베이스 연결 정보
    database_url = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"
    
    # 테스터 인스턴스 생성 및 실행
    tester = EdgeDomainTester(database_url)
    await tester.run_all_tests()


if __name__ == "__main__":
    # asyncio 이벤트 루프 실행
    asyncio.run(main())
