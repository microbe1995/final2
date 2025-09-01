# ============================================================================
# 🔗 Edge Service - CBAM 배출량 전파 서비스
# ============================================================================

import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone
import asyncpg

logger = logging.getLogger(__name__)

class EdgeService:
    """엣지 기반 배출량 전파 서비스 (asyncpg 패턴)"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            logger.warning("DATABASE_URL 환경변수가 설정되지 않았습니다. 데이터베이스 기능이 제한됩니다.")
            return
        
        self.pool = None
        self._initialization_attempted = False
        logger.info("✅ Edge Service 초기화 완료")
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if self._initialization_attempted:
            return  # 이미 초기화 시도했으면 다시 시도하지 않음
            
        if not self.database_url:
            logger.warning("DATABASE_URL이 없어 데이터베이스 초기화를 건너뜁니다.")
            self._initialization_attempted = True
            return
        
        self._initialization_attempted = True
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'cbam-service-edge'
                }
            )
            logger.info("✅ Edge Service 데이터베이스 연결 풀 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ Edge Service 초기화 실패: {str(e)}")
            logger.warning("데이터베이스 연결 실패로 인해 일부 기능이 제한됩니다.")
            self.pool = None
    
    async def _ensure_pool_initialized(self):
        """연결 풀이 초기화되었는지 확인하고, 필요시 초기화"""
        if not self.pool and not self._initialization_attempted:
            await self.initialize()
        
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않았습니다.")
    
    async def get_process_emission_data(self, process_id: int) -> Optional[Dict[str, Any]]:
        """공정의 배출량 데이터를 조회합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        process_id,
                        attrdir_em,
                        cumulative_emission,
                        total_matdir_emission,
                        total_fueldir_emission
                    FROM process_attrdir_emission 
                    WHERE process_id = $1
                """
                row = await conn.fetchrow(query, process_id)
                
                if row:
                    return {
                        'process_id': row['process_id'],
                        'attrdir_em': float(row['attrdir_em']) if row['attrdir_em'] else 0.0,
                        'cumulative_emission': float(row['cumulative_emission']) if row['cumulative_emission'] else 0.0,
                        'total_matdir_emission': float(row['total_matdir_emission']) if row['total_matdir_emission'] else 0.0,
                        'total_fueldir_emission': float(row['total_fueldir_emission']) if row['total_fueldir_emission'] else 0.0
                    }
                return None
                
        except Exception as e:
            logger.error(f"공정 {process_id} 배출량 데이터 조회 실패: {e}")
            return None
    
    async def get_continue_edges(self, source_process_id: int) -> List[Dict[str, Any]]:
        """특정 공정에서 나가는 continue 엣지들을 조회합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT 
                        id,
                        source_node_type,
                        source_id,
                        target_node_type,
                        target_id,
                        edge_kind
                    FROM edge 
                    WHERE source_node_type = 'process' 
                    AND source_id = $1 
                    AND edge_kind = 'continue'
                """
                rows = await conn.fetch(query, source_process_id)
                
                return [
                    {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind']
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"공정 {source_process_id}의 continue 엣지 조회 실패: {e}")
            return []
    
    async def update_process_cumulative_emission(self, process_id: int, cumulative_emission: float) -> bool:
        """공정의 누적 배출량을 업데이트합니다."""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    UPDATE process_attrdir_emission 
                    SET 
                        cumulative_emission = $2,
                        updated_at = NOW()
                    WHERE process_id = $1
                """
                await conn.execute(query, process_id, cumulative_emission)
                
                logger.info(f"공정 {process_id} 누적 배출량 업데이트: {cumulative_emission}")
                return True
                
        except Exception as e:
            logger.error(f"공정 {process_id} 누적 배출량 업데이트 실패: {e}")
            return False
    
    async def propagate_emissions_continue(self, source_process_id: int, target_process_id: int) -> bool:
        """
        규칙 1: 공정→공정 배출량 누적 전달 (edge_kind = "continue")
        source.attr_em이 target으로 누적 전달되어 target.cumulative_emission = source.cumulative_emission + target.attrdir_em
        """
        try:
            logger.info(f"🔗 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 시작")
            
            # 1. 소스 공정의 누적 배출량 조회
            source_emission = await self.get_process_emission_data(source_process_id)
            if not source_emission:
                logger.error(f"소스 공정 {source_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 2. 타겟 공정의 배출량 데이터 조회
            target_emission = await self.get_process_emission_data(target_process_id)
            if not target_emission:
                logger.error(f"타겟 공정 {target_process_id}의 배출량 데이터를 찾을 수 없습니다.")
                return False
            
            # 3. 배출량 누적 계산
            source_cumulative = source_emission['cumulative_emission']
            target_own = target_emission['attrdir_em']
            target_cumulative = source_cumulative + target_own
            
            logger.info(f"🧮 배출량 누적 계산:")
            logger.info(f"  소스 공정 {source_process_id} 누적 배출량: {source_cumulative}")
            logger.info(f"  타겟 공정 {target_process_id} 자체 배출량: {target_own}")
            logger.info(f"  타겟 공정 {target_process_id} 최종 누적 배출량: {target_cumulative}")
            
            # 4. 타겟 공정의 누적 배출량 업데이트
            success = await self.update_process_cumulative_emission(target_process_id, target_cumulative)
            
            if success:
                logger.info(f"✅ 공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 완료")
                return True
            else:
                logger.error(f"❌ 공정 {target_process_id} 누적 배출량 업데이트 실패")
                return False
                
        except Exception as e:
            logger.error(f"공정 {source_process_id} → 공정 {target_process_id} 배출량 누적 전달 실패: {e}")
            return False
    
    async def propagate_emissions_chain(self, process_chain_id: int) -> Dict[str, Any]:
        """
        공정 체인 전체에 대해 배출량 누적 전달을 실행합니다.
        """
        try:
            logger.info(f"🔗 공정 체인 {process_chain_id} 배출량 누적 전달 시작")
            
            # 1. 공정 체인의 순서 정보 조회
            chain_query = text("""
                SELECT pcl.process_id, pcl.sequence_order, pcl.is_continue_edge
                FROM process_chain_link pcl
                WHERE pcl.chain_id = :chain_id
                ORDER BY pcl.sequence_order
            """)
            
            result = await self.db_session.execute(chain_query, {'chain_id': process_chain_id})
            chain_processes = result.fetchall()
            
            if not chain_processes:
                logger.error(f"공정 체인 {process_chain_id}의 공정 정보를 찾을 수 없습니다.")
                return {'success': False, 'error': '공정 체인 정보 없음'}
            
            logger.info(f"📋 공정 체인 {process_chain_id} 공정 순서: {len(chain_processes)}개")
            
            # 2. 순서대로 배출량 누적 전달 실행
            propagation_results = []
            previous_process_id = None
            
            for i, (process_id, sequence_order, is_continue_edge) in enumerate(chain_processes):
                logger.info(f"🔍 공정 {process_id} (순서: {sequence_order}) 처리 중...")
                
                if i == 0:
                    # 첫 번째 공정: 누적 배출량 = 자체 배출량
                    emission_data = await self.get_process_emission_data(process_id)
                    if emission_data:
                        own_emission = emission_data['attrdir_em']
                        success = await self.update_process_cumulative_emission(process_id, own_emission)
                        
                        propagation_results.append({
                            'process_id': process_id,
                            'sequence_order': sequence_order,
                            'own_emission': own_emission,
                            'cumulative_emission': own_emission,
                            'propagation_type': 'first_process',
                            'success': success
                        })
                        
                        previous_process_id = process_id
                        logger.info(f"✅ 첫 번째 공정 {process_id} 누적 배출량 설정: {own_emission}")
                    else:
                        logger.error(f"첫 번째 공정 {process_id} 배출량 데이터 없음")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 없음'}
                        
                elif is_continue_edge and previous_process_id:
                    # continue 엣지가 있는 경우: 이전 공정에서 배출량 누적 전달
                    success = await self.propagate_emissions_continue(previous_process_id, process_id)
                    
                    if success:
                        # 업데이트된 누적 배출량 조회
                        updated_emission = await self.get_process_emission_data(process_id)
                        if updated_emission:
                            propagation_results.append({
                                'process_id': process_id,
                                'sequence_order': sequence_order,
                                'own_emission': updated_emission['attrdir_em'],
                                'cumulative_emission': updated_emission['cumulative_emission'],
                                'propagation_type': 'continue_edge',
                                'source_process_id': previous_process_id,
                                'success': True
                            })
                            
                            previous_process_id = process_id
                            logger.info(f"✅ 공정 {process_id} 배출량 누적 전달 완료")
                        else:
                            logger.error(f"공정 {process_id} 업데이트된 배출량 데이터 조회 실패")
                            return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 조회 실패'}
                    else:
                        logger.error(f"공정 {previous_process_id} → 공정 {process_id} 배출량 누적 전달 실패")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 누적 전달 실패'}
                        
                else:
                    # continue 엣지가 없는 경우: 자체 배출량만 설정
                    emission_data = await self.get_process_emission_data(process_id)
                    if emission_data:
                        own_emission = emission_data['attrdir_em']
                        success = await self.update_process_cumulative_emission(process_id, own_emission)
                        
                        propagation_results.append({
                            'process_id': process_id,
                            'sequence_order': sequence_order,
                            'own_emission': own_emission,
                            'cumulative_emission': own_emission,
                            'propagation_type': 'no_continue_edge',
                            'success': success
                        })
                        
                        previous_process_id = process_id
                        logger.info(f"✅ 공정 {process_id} 자체 배출량만 설정: {own_emission}")
                    else:
                        logger.error(f"공정 {process_id} 배출량 데이터 없음")
                        return {'success': False, 'error': f'공정 {process_id} 배출량 데이터 없음'}
            
            # 3. 결과 요약
            total_processes = len(propagation_results)
            successful_propagations = len([r for r in propagation_results if r['success']])
            
            final_result = {
                'success': True,
                'chain_id': process_chain_id,
                'total_processes': total_processes,
                'successful_propagations': successful_propagations,
                'propagation_results': propagation_results,
                'final_emission_summary': {
                    'total_own_emissions': sum(r['own_emission'] for r in propagation_results),
                    'total_cumulative_emissions': sum(r['cumulative_emission'] for r in propagation_results),
                    'last_process_cumulative': propagation_results[-1]['cumulative_emission'] if propagation_results else 0
                }
            }
            
            logger.info(f"🎯 공정 체인 {process_chain_id} 배출량 누적 전달 완료!")
            logger.info(f"  총 공정 수: {total_processes}")
            logger.info(f"  성공한 전파: {successful_propagations}")
            logger.info(f"  최종 누적 배출량: {final_result['final_emission_summary']['last_process_cumulative']}")
            
            return final_result
            
        except Exception as e:
            logger.error(f"공정 체인 {process_chain_id} 배출량 누적 전달 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_process_chain_emission_summary(self, process_chain_id: int) -> Dict[str, Any]:
        """공정 체인의 배출량 요약 정보를 조회합니다."""
        try:
            summary_query = text("""
                SELECT 
                    pcl.sequence_order,
                    pcl.process_id,
                    p.process_name,
                    pae.attrdir_em,
                    pae.cumulative_emission,
                    pae.calculation_date
                FROM process_chain_link pcl
                JOIN process p ON pcl.process_id = p.id
                LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
                WHERE pcl.chain_id = :chain_id
                ORDER BY pcl.sequence_order
            """)
            
            result = await self.db_session.execute(summary_query, {'chain_id': process_chain_id})
            processes = result.fetchall()
            
            if not processes:
                return {'success': False, 'error': '공정 체인 정보 없음'}
            
            summary = {
                'chain_id': process_chain_id,
                'total_processes': len(processes),
                'processes': [
                    {
                        'sequence_order': proc.sequence_order,
                        'process_id': proc.process_id,
                        'process_name': proc.process_name,
                        'own_emission': float(proc.attrdir_em) if proc.attrdir_em else 0.0,
                        'cumulative_emission': float(proc.cumulative_emission) if proc.cumulative_emission else 0.0,
                        'calculation_date': proc.calculation_date.isoformat() if proc.calculation_date else None
                    }
                    for proc in processes
                ],
                'total_own_emissions': sum(float(proc.attrdir_em) if proc.attrdir_em else 0.0 for proc in processes),
                'total_cumulative_emissions': sum(float(proc.cumulative_emission) if proc.cumulative_emission else 0.0 for proc in processes)
            }
            
            return {'success': True, 'summary': summary}
            
        except Exception as e:
            logger.error(f"공정 체인 {process_chain_id} 배출량 요약 조회 실패: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================================================
    # 🔗 기존 Edge CRUD 메서드들
    # ============================================================================
    
    async def create_edge(self, edge_data) -> Optional[Dict[str, Any]]:
        """엣지 생성 (asyncpg 패턴)"""
        await self._ensure_pool_initialized()
        try:
            logger.info(f"엣지 생성 시작: {edge_data}")
            
            async with self.pool.acquire() as conn:
                query = """
                    INSERT INTO edge (source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $6)
                    RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                """
                
                now = datetime.now(timezone.utc)
                row = await conn.fetchrow(
                    query,
                    edge_data.source_node_type,
                    edge_data.source_id,
                    edge_data.target_node_type,
                    edge_data.target_id,
                    edge_data.edge_kind,
                    now
                )
                
                if row:
                    result = {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                    logger.info(f"✅ 엣지 생성 완료: ID {row['id']}")
                    return result
                else:
                    logger.error("엣지 생성 실패: 데이터베이스에서 결과를 반환하지 않았습니다.")
                    return None
                    
        except Exception as e:
            logger.error(f"엣지 생성 실패: {e}")
            import traceback
            logger.error(f"스택 트레이스: {traceback.format_exc()}")
            raise e
    
    async def get_edges(self) -> List[Dict[str, Any]]:
        """모든 엣지 조회 (asyncpg 패턴)"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    ORDER BY id
                """
                rows = await conn.fetch(query)
                
                return [
                    {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                    for row in rows
                ]
        except Exception as e:
            logger.error(f"엣지 조회 실패: {e}")
            return []
    
    async def get_edge(self, edge_id: int) -> Optional[Dict[str, Any]]:
        """특정 엣지 조회 (asyncpg 패턴)"""
        await self._ensure_pool_initialized()
        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    FROM edge
                    WHERE id = $1
                """
                row = await conn.fetchrow(query, edge_id)
                
                if row:
                    return {
                        'id': row['id'],
                        'source_node_type': row['source_node_type'],
                        'source_id': row['source_id'],
                        'target_node_type': row['target_node_type'],
                        'target_id': row['target_id'],
                        'edge_kind': row['edge_kind'],
                        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                        'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                    }
                return None
        except Exception as e:
            logger.error(f"엣지 {edge_id} 조회 실패: {e}")
            return None
    
    async def update_edge(self, edge_id: int, edge_data) -> Optional[Dict[str, Any]]:
        """엣지 수정 (asyncpg 패턴)"""
        await self._ensure_pool_initialized()
        try:
            logger.info(f"엣지 {edge_id} 수정: {edge_data}")
            
            # 기존 엣지 조회
            existing_edge = await self.get_edge(edge_id)
            if not existing_edge:
                return None
            
            async with self.pool.acquire() as conn:
                # 업데이트할 필드들을 동적으로 구성
                update_fields = []
                params = []
                param_count = 1
                
                if edge_data.source_node_type is not None:
                    update_fields.append(f"source_node_type = ${param_count}")
                    params.append(edge_data.source_node_type)
                    param_count += 1
                
                if edge_data.source_id is not None:
                    update_fields.append(f"source_id = ${param_count}")
                    params.append(edge_data.source_id)
                    param_count += 1
                
                if edge_data.target_node_type is not None:
                    update_fields.append(f"target_node_type = ${param_count}")
                    params.append(edge_data.target_node_type)
                    param_count += 1
                
                if edge_data.target_id is not None:
                    update_fields.append(f"target_id = ${param_count}")
                    params.append(edge_data.target_id)
                    param_count += 1
                
                if edge_data.edge_kind is not None:
                    update_fields.append(f"edge_kind = ${param_count}")
                    params.append(edge_data.edge_kind)
                    param_count += 1
                
                # updated_at 필드 추가
                update_fields.append(f"updated_at = ${param_count}")
                params.append(datetime.now(timezone.utc))
                param_count += 1
                
                # ID 파라미터 추가
                params.append(edge_id)
                
                if update_fields:
                    query = f"""
                        UPDATE edge 
                        SET {', '.join(update_fields)}
                        WHERE id = ${param_count}
                        RETURNING id, source_node_type, source_id, target_node_type, target_id, edge_kind, created_at, updated_at
                    """
                    
                    row = await conn.fetchrow(query, *params)
                    
                    if row:
                        result = {
                            'id': row['id'],
                            'source_node_type': row['source_node_type'],
                            'source_id': row['source_id'],
                            'target_node_type': row['target_node_type'],
                            'target_id': row['target_id'],
                            'edge_kind': row['edge_kind'],
                            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                            'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                        }
                        logger.info(f"✅ 엣지 {edge_id} 수정 완료")
                        return result
                
                return None
                
        except Exception as e:
            logger.error(f"엣지 {edge_id} 수정 실패: {e}")
            raise e
    
    async def delete_edge(self, edge_id: int) -> bool:
        """엣지 삭제 (asyncpg 패턴)"""
        await self._ensure_pool_initialized()
        try:
            logger.info(f"엣지 {edge_id} 삭제")
            
            # 기존 엣지 조회
            existing_edge = await self.get_edge(edge_id)
            if not existing_edge:
                return False
            
            async with self.pool.acquire() as conn:
                query = """
                    DELETE FROM edge 
                    WHERE id = $1
                    RETURNING id
                """
                
                row = await conn.fetchrow(query, edge_id)
                
                if row:
                    logger.info(f"✅ 엣지 {edge_id} 삭제 완료")
                    return True
                else:
                    logger.warning(f"엣지 {edge_id} 삭제 실패: 해당 엣지를 찾을 수 없습니다.")
                    return False
                    
        except Exception as e:
            logger.error(f"엣지 {edge_id} 삭제 실패: {e}")
            raise e
