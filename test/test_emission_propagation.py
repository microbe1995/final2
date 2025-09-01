#!/usr/bin/env python3
"""
배출량 전파 서비스 테스트 스크립트
규칙 1번: 공정→공정 배출량 누적 전달을 테스트합니다.
"""

import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Any

# Railway DB 연결 정보
RAILWAY_DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def test_emission_propagation():
    """배출량 전파 서비스를 테스트합니다."""
    
    try:
        # Railway DB 연결
        print("🔗 Railway DB에 연결 중...")
        conn = await asyncpg.connect(RAILWAY_DATABASE_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 현재 공정 체인 정보 확인
        print("\n🔍 1. 현재 공정 체인 정보 확인")
        print("=" * 60)
        
        chain_query = """
        SELECT 
            pc.id as chain_id,
            pc.chain_name,
            pc.start_process_id,
            pc.end_process_id,
            pc.chain_length,
            pc.is_active
        FROM process_chain pc
        WHERE pc.is_active = true
        ORDER BY pc.id;
        """
        
        chains = await conn.fetch(chain_query)
        
        if not chains:
            print("⚠️ 활성화된 공정 체인이 없습니다.")
            return
        
        print(f"📊 활성화된 공정 체인 수: {len(chains)}")
        
        for chain in chains:
            print(f"\n📋 체인 ID: {chain['chain_id']}")
            print(f"  이름: {chain['chain_name']}")
            print(f"  시작 공정: {chain['start_process_id']}")
            print(f"  종료 공정: {chain['end_process_id']}")
            print(f"  공정 수: {chain['chain_length']}")
        
        # 2. 첫 번째 공정 체인 선택하여 상세 분석
        if chains:
            selected_chain = chains[0]
            chain_id = selected_chain['chain_id']
            
            print(f"\n🎯 선택된 공정 체인: {selected_chain['chain_name']} (ID: {chain_id})")
            
            # 3. 공정 체인의 상세 공정 정보 조회
            print("\n🔍 3. 공정 체인 상세 공정 정보")
            print("=" * 60)
            
            process_query = """
            SELECT 
                pcl.sequence_order,
                pcl.process_id,
                pcl.is_continue_edge,
                p.process_name,
                pae.attrdir_em,
                pae.cumulative_emission,
                pae.calculation_date
            FROM process_chain_link pcl
            JOIN process p ON pcl.process_id = p.id
            LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
            WHERE pcl.chain_id = $1
            ORDER BY pcl.sequence_order;
            """
            
            processes = await conn.fetch(process_query, chain_id)
            
            print(f"📋 공정 체인 {chain_id}의 공정 정보:")
            for proc in processes:
                print(f"  📊 순서 {proc['sequence_order']}: 공정 {proc['process_id']} ({proc['process_name']})")
                print(f"    자체 배출량: {proc['attrdir_em'] or 'N/A'}")
                print(f"    누적 배출량: {proc['cumulative_emission'] or 'N/A'}")
                print(f"    continue 엣지: {'예' if proc['is_continue_edge'] else '아니오'}")
                print()
            
            # 4. 배출량 누적 전달 시뮬레이션
            print("\n🧮 4. 배출량 누적 전달 시뮬레이션")
            print("=" * 60)
            
            print("📊 규칙 1번: 공정→공정 배출량 누적 전달")
            print("  source.cumulative_emission이 target으로 전달되어")
            print("  target.cumulative_emission = source.cumulative_emission + target.attrdir_em")
            print()
            
            # 시뮬레이션 실행
            simulation_results = []
            previous_cumulative = 0
            
            for i, proc in enumerate(processes):
                process_id = proc['process_id']
                process_name = proc['process_name']
                own_emission = float(proc['attrdir_em']) if proc['attrdir_em'] else 0.0
                is_continue = proc['is_continue_edge']
                
                if i == 0:
                    # 첫 번째 공정: 누적 배출량 = 자체 배출량
                    cumulative_emission = own_emission
                    propagation_type = "첫 번째 공정 (누적 = 자체)"
                elif is_continue and previous_cumulative > 0:
                    # continue 엣지가 있는 경우: 이전 공정에서 누적 전달
                    cumulative_emission = previous_cumulative + own_emission
                    propagation_type = f"continue 엣지 (이전 누적 {previous_cumulative} + 자체 {own_emission})"
                else:
                    # continue 엣지가 없는 경우: 자체 배출량만
                    cumulative_emission = own_emission
                    propagation_type = "continue 엣지 없음 (누적 = 자체)"
                
                simulation_results.append({
                    'sequence_order': proc['sequence_order'],
                    'process_id': process_id,
                    'process_name': process_name,
                    'own_emission': own_emission,
                    'cumulative_emission': cumulative_emission,
                    'propagation_type': propagation_type
                })
                
                previous_cumulative = cumulative_emission
                
                print(f"  📊 순서 {proc['sequence_order']}: {process_name} (ID: {process_id})")
                print(f"    자체 배출량: {own_emission}")
                print(f"    누적 배출량: {cumulative_emission}")
                print(f"    전파 유형: {propagation_type}")
                print()
            
            # 5. 시뮬레이션 결과 요약
            print("\n📊 5. 시뮬레이션 결과 요약")
            print("=" * 60)
            
            total_own = sum(r['own_emission'] for r in simulation_results)
            total_cumulative = sum(r['cumulative_emission'] for r in simulation_results)
            final_cumulative = simulation_results[-1]['cumulative_emission'] if simulation_results else 0
            
            print(f"📋 공정 체인: {selected_chain['chain_name']}")
            print(f"📊 총 공정 수: {len(simulation_results)}")
            print(f"🧮 총 자체 배출량: {total_own}")
            print(f"🔗 최종 누적 배출량: {final_cumulative}")
            print(f"📈 누적 증가율: {((final_cumulative - total_own) / total_own * 100):.2f}%" if total_own > 0 else "N/A")
            
            # 6. 실제 DB 업데이트 (선택사항)
            print("\n🔧 6. 실제 DB 업데이트 (선택사항)")
            print("=" * 60)
            
            print("⚠️ 실제 DB를 업데이트하시겠습니까? (y/N)")
            user_input = input().strip().lower()
            
            if user_input == 'y':
                print("🔧 실제 DB 업데이트를 진행합니다...")
                
                # 각 공정의 누적 배출량을 실제로 업데이트
                for result in simulation_results:
                    update_query = """
                    UPDATE process_attrdir_emission 
                    SET cumulative_emission = $1, updated_at = NOW()
                    WHERE process_id = $2;
                    """
                    
                    try:
                        await conn.execute(update_query, result['cumulative_emission'], result['process_id'])
                        print(f"✅ 공정 {result['process_id']} 누적 배출량 업데이트: {result['cumulative_emission']}")
                    except Exception as e:
                        print(f"❌ 공정 {result['process_id']} 업데이트 실패: {e}")
                
                await conn.commit()
                print("✅ 모든 공정의 누적 배출량 업데이트 완료!")
                
            else:
                print("ℹ️ 실제 DB 업데이트를 건너뜁니다.")
            
            # 7. 결과를 JSON 파일로 저장
            print("\n💾 7. 시뮬레이션 결과를 JSON 파일로 저장")
            print("=" * 60)
            
            simulation_summary = {
                'simulation_date': datetime.now().isoformat(),
                'chain_id': chain_id,
                'chain_name': selected_chain['chain_name'],
                'total_processes': len(simulation_results),
                'simulation_results': simulation_results,
                'summary': {
                    'total_own_emissions': total_own,
                    'total_cumulative_emissions': total_cumulative,
                    'final_cumulative_emission': final_cumulative,
                    'accumulation_ratio': ((final_cumulative - total_own) / total_own * 100) if total_own > 0 else None
                }
            }
            
            with open('emission_propagation_simulation.json', 'w', encoding='utf-8') as f:
                json.dump(simulation_summary, f, indent=2, ensure_ascii=False, default=str)
            
            print("✅ 시뮬레이션 결과가 emission_propagation_simulation.json 파일로 저장되었습니다.")
        
        await conn.close()
        print("\n🔗 Railway DB 연결 종료")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 배출량 전파 서비스 테스트 시작")
    print("=" * 60)
    print("📍 규칙 1번: 공정→공정 배출량 누적 전달 테스트")
    print("=" * 60)
    
    success = asyncio.run(test_emission_propagation())
    
    if success:
        print("\n🎯 테스트 완료! 다음 단계:")
        print("1. emission_propagation_simulation.json 파일 확인")
        print("2. 실제 배출량 전파 서비스 구현")
        print("3. API 엔드포인트 생성")
    else:
        print("\n❌ 테스트 실패! 오류를 확인하고 다시 시도해주세요.")
