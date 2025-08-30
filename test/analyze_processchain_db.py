#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합공정 그룹 DB 분석 스크립트
Edge 생성 시 자동으로 통합공정 그룹이 생성되는지 확인합니다.
"""

import psycopg2
import logging
from typing import Dict, Any, List
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Railway DB 연결 정보
DB_CONFIG = {
    "host": "shortline.proxy.rlwy.net",
    "port": 46071,
    "database": "railway",
    "user": "postgres",
    "password": "eQGfytQNhXYAZxsJYlFhYagpJAgstrni"
}

def connect_to_db():
    """Railway DB에 연결"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Railway DB 연결 성공")
        return connection
    except Exception as e:
        logger.error(f"❌ Railway DB 연결 실패: {e}")
        return None

def analyze_table_structure(connection):
    """통합공정 그룹 관련 테이블 구조 분석"""
    logger.info("🔍 통합공정 그룹 관련 테이블 구조 분석")
    logger.info("="*80)
    
    tables_to_analyze = [
        'edge',           # 공정 간 연결 정보
        'process_chain',  # 통합공정 그룹
        'process_chain_link', # 그룹 내 공정 연결
        'process',        # 공정 정보
        'process_attrdir_emission' # 공정별 배출량
    ]
    
    for table_name in tables_to_analyze:
        try:
            with connection.cursor() as cursor:
                # 테이블 존재 여부 확인
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table_name,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    logger.info(f"📋 테이블 '{table_name}' 존재함")
                    
                    # 테이블 구조 확인
                    cursor.execute("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position;
                    """, (table_name,))
                    
                    columns = cursor.fetchall()
                    logger.info(f"   📊 컬럼 구조 ({len(columns)}개):")
                    for col in columns:
                        nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {col[3]}" if col[3] else ""
                        logger.info(f"     - {col[0]}: {col[1]} {nullable}{default}")
                    
                    # 데이터 개수 확인
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    logger.info(f"   📈 데이터 개수: {count}")
                    
                    # 샘플 데이터 확인 (처음 3개)
                    if count > 0:
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                        samples = cursor.fetchall()
                        logger.info(f"   🔍 샘플 데이터:")
                        for i, sample in enumerate(samples, 1):
                            logger.info(f"     {i}. {sample}")
                    
                else:
                    logger.warning(f"⚠️ 테이블 '{table_name}' 존재하지 않음")
                    
        except Exception as e:
            logger.error(f"❌ 테이블 '{table_name}' 분석 실패: {e}")
    
    logger.info("="*80)

def analyze_edge_data(connection):
    """Edge 테이블 데이터 분석"""
    logger.info("🔗 Edge 테이블 데이터 분석")
    logger.info("="*80)
    
    try:
        with connection.cursor() as cursor:
            # Edge 데이터 조회
            cursor.execute("""
                SELECT e.*, 
                       ps.process_name as source_process_name,
                       pt.process_name as target_process_name
                FROM edge e
                LEFT JOIN process ps ON e.source_id = ps.id
                LEFT JOIN process pt ON e.target_id = pt.id
                ORDER BY e.created_at DESC
                LIMIT 10;
            """)
            
            edges = cursor.fetchall()
            logger.info(f"📋 최근 Edge 데이터 ({len(edges)}개):")
            
            for edge in edges:
                logger.info(f"   - Edge ID: {edge[0]}")
                logger.info(f"     소스: {edge[1]} ({edge[6]})")
                logger.info(f"     타겟: {edge[2]} ({edge[7]})")
                logger.info(f"     종류: {edge[3]}")
                logger.info(f"     생성일: {edge[4]}")
                logger.info("")
                
    except Exception as e:
        logger.error(f"❌ Edge 데이터 분석 실패: {e}")

def analyze_process_chain_data(connection):
    """Process Chain 테이블 데이터 분석"""
    logger.info("🔄 Process Chain 테이블 데이터 분석")
    logger.info("="*80)
    
    try:
        with connection.cursor() as cursor:
            # Process Chain 데이터 조회
            cursor.execute("""
                SELECT pc.*, 
                       ps.process_name as start_process_name,
                       pe.process_name as end_process_name
                FROM process_chain pc
                LEFT JOIN process ps ON pc.start_process_id = ps.id
                LEFT JOIN pe.process_name as end_process_name
                ORDER BY pc.created_at DESC;
            """)
            
            chains = cursor.fetchall()
            logger.info(f"📋 Process Chain 데이터 ({len(chains)}개):")
            
            for chain in chains:
                logger.info(f"   - Chain ID: {chain[0]}")
                logger.info(f"     그룹명: {chain[1]}")
                logger.info(f"     시작공정: {chain[2]} ({chain[6]})")
                logger.info(f"     종료공정: {chain[3]} ({chain[7]})")
                logger.info(f"     공정개수: {chain[4]}")
                logger.info(f"     활성상태: {chain[5]}")
                logger.info(f"     생성일: {chain[6]}")
                logger.info("")
                
                # Chain Link 데이터 조회
                cursor.execute("""
                    SELECT pcl.*, p.process_name
                    FROM process_chain_link pcl
                    LEFT JOIN process p ON pcl.process_id = p.id
                    WHERE pcl.chain_id = %s
                    ORDER BY pcl.sequence_order;
                """, (chain[0],))
                
                links = cursor.fetchall()
                logger.info(f"     🔗 연결된 공정들 ({len(links)}개):")
                for link in links:
                    logger.info(f"       - 순서 {link[3]}: 공정 {link[2]} ({link[5]})")
                logger.info("")
                
    except Exception as e:
        logger.error(f"❌ Process Chain 데이터 분석 실패: {e}")

def analyze_process_emissions(connection):
    """공정별 배출량 데이터 분석"""
    logger.info("📊 공정별 배출량 데이터 분석")
    logger.info("="*80)
    
    try:
        with connection.cursor() as cursor:
            # 공정별 배출량 조회
            cursor.execute("""
                SELECT pae.*, p.process_name
                FROM process_attrdir_emission pae
                LEFT JOIN process p ON pae.process_id = p.id
                ORDER BY pae.total_matdir_emission + pae.total_fueldir_emission DESC
                LIMIT 10;
            """)
            
            emissions = cursor.fetchall()
            logger.info(f"📋 공정별 배출량 데이터 ({len(emissions)}개):")
            
            for emission in emissions:
                total_emission = float(emission[2] or 0) + float(emission[3] or 0)
                logger.info(f"   - 공정 ID: {emission[1]} ({emission[6]})")
                logger.info(f"     원료직접배출량: {emission[2]}")
                logger.info(f"     연료직접배출량: {emission[3]}")
                logger.info(f"     총 배출량: {total_emission}")
                logger.info(f"     계산일: {emission[4]}")
                logger.info("")
                
    except Exception as e:
        logger.error(f"❌ 공정별 배출량 분석 실패: {e}")

def check_foreign_key_constraints(connection):
    """외래키 제약조건 확인"""
    logger.info("🔗 외래키 제약조건 확인")
    logger.info("="*80)
    
    try:
        with connection.cursor() as cursor:
            # Edge 테이블 외래키 확인
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name IN ('edge', 'process_chain', 'process_chain_link');
            """)
            
            constraints = cursor.fetchall()
            logger.info(f"📋 외래키 제약조건 ({len(constraints)}개):")
            
            for constraint in constraints:
                logger.info(f"   - {constraint[1]}.{constraint[2]} → {constraint[3]}.{constraint[4]}")
                
    except Exception as e:
        logger.error(f"❌ 외래키 제약조건 확인 실패: {e}")

def main():
    """메인 함수"""
    logger.info("🚀 통합공정 그룹 DB 분석 시작")
    logger.info("="*80)
    
    # 1. DB 연결
    connection = connect_to_db()
    if not connection:
        logger.error("❌ DB 연결 실패로 인해 스크립트 종료")
        return
    
    try:
        # 2. 테이블 구조 분석
        analyze_table_structure(connection)
        
        # 3. Edge 데이터 분석
        analyze_edge_data(connection)
        
        # 4. Process Chain 데이터 분석
        analyze_process_chain_data(connection)
        
        # 5. 공정별 배출량 분석
        analyze_process_emissions(connection)
        
        # 6. 외래키 제약조건 확인
        check_foreign_key_constraints(connection)
        
        logger.info("="*80)
        logger.info("✅ 통합공정 그룹 DB 분석 완료!")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"❌ 분석 중 오류 발생: {e}")
        
    finally:
        # 7. DB 연결 종료
        if connection:
            connection.close()
            logger.info("🔌 DB 연결 종료")

if __name__ == "__main__":
    main()
