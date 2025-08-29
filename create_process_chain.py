#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 공정 그룹 생성 스크립트
기존 공정들을 연결하여 통합 그룹을 만들고 배출량 합계를 계산합니다.
"""

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

# 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'shortline.proxy.rlwy.net',
    'port': 46071,
    'database': 'railway',
    'user': 'postgres',
    'password': 'eQGfytQNhXYAZxsJYlFhYagpJAgstrni'
}

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 데이터베이스 연결 성공")
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def create_process_chain(conn):
    """통합 공정 그룹 생성"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 1. 기존 공정들의 배출량 데이터 확인
            cursor.execute("""
                SELECT 
                    process_id,
                    total_matdir_emission,
                    total_fueldir_emission,
                    attrdir_em
                FROM process_attrdir_emission 
                ORDER BY process_id
            """)
            processes = cursor.fetchall()
            
            if not processes:
                print("❌ 배출량 데이터가 있는 공정이 없습니다.")
                return
            
            print(f"📊 배출량 데이터가 있는 공정: {len(processes)}개")
            for proc in processes:
                print(f"   공정 ID: {proc['process_id']}, 총 배출량: {proc['attrdir_em']}")
            
            # 2. 통합 공정 그룹 생성
            chain_name = f"통합공정그룹-{processes[0]['process_id']}-{processes[-1]['process_id']}"
            start_process_id = processes[0]['process_id']
            end_process_id = processes[-1]['process_id']
            chain_length = len(processes)
            
            cursor.execute("""
                INSERT INTO process_chain 
                (chain_name, start_process_id, end_process_id, chain_length, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (chain_name, start_process_id, end_process_id, chain_length, True, datetime.utcnow(), datetime.utcnow()))
            
            chain_id = cursor.fetchone()['id']
            print(f"✅ 통합 공정 그룹 생성 완료: ID {chain_id}, 이름: {chain_name}")
            
            # 3. 그룹에 공정들 연결
            for i, proc in enumerate(processes, 1):
                cursor.execute("""
                    INSERT INTO process_chain_link 
                    (chain_id, process_id, sequence_order, is_continue_edge, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (chain_id, proc['process_id'], i, True, datetime.utcnow(), datetime.utcnow()))
            
            print(f"✅ {len(processes)}개 공정을 그룹에 연결 완료")
            
            # 4. 통합 그룹의 총 배출량 계산
            total_emission = sum(proc['attrdir_em'] for proc in processes)
            print(f"🔥 통합 그룹 총 배출량: {total_emission}")
            
            conn.commit()
            print("✅ 데이터베이스 변경사항 저장 완료")
            
            return chain_id
            
    except Exception as e:
        print(f"❌ 통합 공정 그룹 생성 실패: {e}")
        conn.rollback()
        raise e

def verify_process_chain(conn):
    """생성된 통합 공정 그룹 확인"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # process_chain 테이블 확인
            cursor.execute("SELECT * FROM process_chain ORDER BY id")
            chains = cursor.fetchall()
            
            print(f"\n📋 생성된 통합 공정 그룹: {len(chains)}개")
            for chain in chains:
                print(f"   그룹 ID: {chain['id']}")
                print(f"   그룹명: {chain['chain_name']}")
                print(f"   시작공정: {chain['start_process_id']}")
                print(f"   종료공정: {chain['end_process_id']}")
                print(f"   공정개수: {chain['chain_length']}")
                print(f"   활성상태: {chain['is_active']}")
                
                # 해당 그룹의 링크 확인
                cursor.execute("""
                    SELECT pcl.*, pae.attrdir_em
                    FROM process_chain_link pcl
                    LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
                    WHERE pcl.chain_id = %s 
                    ORDER BY pcl.sequence_order
                """, (chain['id'],))
                links = cursor.fetchall()
                
                print(f"   연결된 공정들:")
                total_emission = 0
                for link in links:
                    emission = link['attrdir_em'] or 0
                    total_emission += emission
                    print(f"     - 공정 ID: {link['process_id']}, 순서: {link['sequence_order']}, 배출량: {emission}")
                
                print(f"   그룹 총 배출량: {total_emission}")
                print()
                
    except Exception as e:
        print(f"❌ 통합 공정 그룹 확인 실패: {e}")

def main():
    """메인 함수"""
    print("🚀 통합 공정 그룹 생성 시작")
    print("="*80)
    
    # 데이터베이스 연결
    conn = connect_db()
    
    try:
        # 1. 통합 공정 그룹 생성
        chain_id = create_process_chain(conn)
        
        if chain_id:
            # 2. 생성된 그룹 확인
            verify_process_chain(conn)
            
            print("\n" + "="*80)
            print("✅ 통합 공정 그룹 생성 완료!")
            print("이제 프론트엔드에서 배출량 합계가 표시될 것입니다.")
            print("="*80)
        
    except Exception as e:
        print(f"❌ 작업 중 오류 발생: {e}")
    finally:
        conn.close()
        print("🔌 데이터베이스 연결 종료")

if __name__ == "__main__":
    main()
