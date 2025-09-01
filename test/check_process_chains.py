#!/usr/bin/env python3
"""
공정 체인 테이블 상태 확인 스크립트
"""

import asyncio
import asyncpg
import json
from datetime import datetime

# Railway DB 연결 정보
RAILWAY_DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def check_process_chains():
    """공정 체인 테이블의 상태를 확인합니다."""
    
    try:
        # Railway DB 연결
        print("🔗 Railway DB에 연결 중...")
        conn = await asyncpg.connect(RAILWAY_DATABASE_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. process_chain 테이블 전체 확인
        print("\n🔍 1. process_chain 테이블 전체 확인")
        print("=" * 60)
        
        chain_query = """
        SELECT 
            id,
            chain_name,
            start_process_id,
            end_process_id,
            chain_length,
            is_active,
            created_at,
            updated_at
        FROM process_chain
        ORDER BY id;
        """
        
        chains = await conn.fetch(chain_query)
        
        if not chains:
            print("⚠️ process_chain 테이블에 데이터가 없습니다.")
        else:
            print(f"📊 총 공정 체인 수: {len(chains)}")
            
            for chain in chains:
                print(f"\n📋 체인 ID: {chain['id']}")
                print(f"  이름: {chain['chain_name']}")
                print(f"  시작 공정: {chain['start_process_id']}")
                print(f"  종료 공정: {chain['end_process_id']}")
                print(f"  공정 수: {chain['chain_length']}")
                print(f"  활성 상태: {'예' if chain['is_active'] else '아니오'}")
                print(f"  생성일: {chain['created_at']}")
                print(f"  수정일: {chain['updated_at']}")
        
        # 2. process_chain_link 테이블 확인
        print("\n🔍 2. process_chain_link 테이블 확인")
        print("=" * 60)
        
        link_query = """
        SELECT 
            id,
            chain_id,
            process_id,
            sequence_order,
            is_continue_edge,
            created_at,
            updated_at
        FROM process_chain_link
        ORDER BY chain_id, sequence_order;
        """
        
        links = await conn.fetch(link_query)
        
        if not links:
            print("⚠️ process_chain_link 테이블에 데이터가 없습니다.")
        else:
            print(f"📊 총 링크 수: {len(links)}")
            
            # 체인별로 그룹화
            chain_links = {}
            for link in links:
                chain_id = link['chain_id']
                if chain_id not in chain_links:
                    chain_links[chain_id] = []
                chain_links[chain_id].append(link)
            
            for chain_id, chain_link_list in chain_links.items():
                print(f"\n🔗 체인 {chain_id}의 링크들:")
                for link in chain_link_list:
                    print(f"  📊 순서 {link['sequence_order']}: 공정 {link['process_id']} (continue: {'예' if link['is_continue_edge'] else '아니오'})")
        
        # 3. 공정 정보 확인
        print("\n🔍 3. 공정 정보 확인")
        print("=" * 60)
        
        process_query = """
        SELECT 
            id,
            process_name,
            start_period,
            end_period,
            created_at,
            updated_at
        FROM process
        ORDER BY id;
        """
        
        processes = await conn.fetch(process_query)
        
        if not processes:
            print("⚠️ process 테이블에 데이터가 없습니다.")
        else:
            print(f"📊 총 공정 수: {len(processes)}")
            
            for proc in processes:
                print(f"  📋 공정 {proc['id']}: {proc['process_name']}")
        
        # 4. 배출량 정보 확인
        print("\n🔍 4. 배출량 정보 확인")
        print("=" * 60)
        
        emission_query = """
        SELECT 
            id,
            process_id,
            total_matdir_emission,
            total_fueldir_emission,
            attrdir_em,
            cumulative_emission,
            calculation_date
        FROM process_attrdir_emission
        ORDER BY process_id;
        """
        
        emissions = await conn.fetch(emission_query)
        
        if not emissions:
            print("⚠️ process_attrdir_emission 테이블에 데이터가 없습니다.")
        else:
            print(f"📊 총 배출량 레코드 수: {len(emissions)}")
            
            for emission in emissions:
                print(f"  📊 공정 {emission['process_id']}:")
                print(f"    원료직접: {emission['total_matdir_emission']}")
                print(f"    연료직접: {emission['total_fueldir_emission']}")
                print(f"    직접귀속: {emission['attrdir_em']}")
                print(f"    누적배출량: {emission['cumulative_emission']}")
                print()
        
        # 5. 간단한 공정 체인 생성 테스트
        print("\n🔧 5. 간단한 공정 체인 생성 테스트")
        print("=" * 60)
        
        # 기존 공정 체인이 없으면 간단한 것을 생성
        if not chains:
            print("📝 간단한 공정 체인을 생성합니다...")
            
            try:
                # 1. 공정 체인 생성
                create_chain_query = """
                INSERT INTO process_chain (chain_name, start_process_id, end_process_id, chain_length, is_active)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id;
                """
                
                # 첫 번째와 두 번째 공정을 사용
                if len(processes) >= 2:
                    start_process = processes[0]['id']
                    end_process = processes[1]['id']
                    
                    result = await conn.execute(create_chain_query, 
                                             "테스트 공정 체인", 
                                             start_process, 
                                             end_process, 
                                             2, 
                                             True)
                    
                    print(f"✅ 공정 체인 생성 완료: {result}")
                    
                    # 2. 공정 체인 링크 생성
                    create_link_query = """
                    INSERT INTO process_chain_link (chain_id, process_id, sequence_order, is_continue_edge)
                    VALUES ($1, $2, $3, $4);
                    """
                    
                    # 첫 번째 공정
                    await conn.execute(create_link_query, 1, start_process, 1, True)
                    print(f"✅ 첫 번째 공정 링크 생성: 공정 {start_process}")
                    
                    # 두 번째 공정
                    await conn.execute(create_link_query, 1, end_process, 2, True)
                    print(f"✅ 두 번째 공정 링크 생성: 공정 {end_process}")
                    
                    await conn.commit()
                    print("✅ 테스트 공정 체인 생성 완료!")
                    
                else:
                    print("⚠️ 공정이 2개 미만이어서 체인을 생성할 수 없습니다.")
                    
            except Exception as e:
                print(f"❌ 공정 체인 생성 실패: {e}")
                await conn.rollback()
        else:
            print("ℹ️ 기존 공정 체인이 존재합니다.")
        
        await conn.close()
        print("\n🔗 Railway DB 연결 종료")
        
        return True
        
    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 공정 체인 상태 확인 시작")
    print("=" * 60)
    
    success = asyncio.run(check_process_chains())
    
    if success:
        print("\n🎯 확인 완료!")
    else:
        print("\n❌ 확인 실패!")
