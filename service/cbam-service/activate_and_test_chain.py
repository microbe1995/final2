#!/usr/bin/env python3
"""
공정 체인 활성화 및 배출량 전파 테스트 스크립트
"""

import asyncio
import asyncpg
import json
from datetime import datetime

# Railway DB 연결 정보
RAILWAY_DATABASE_URL = "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway"

async def activate_and_test_chain():
    """공정 체인을 활성화하고 배출량 전파를 테스트합니다."""
    
    try:
        # Railway DB 연결
        print("🔗 Railway DB에 연결 중...")
        conn = await asyncpg.connect(RAILWAY_DATABASE_URL)
        print("✅ Railway DB 연결 성공!")
        
        # 1. 기존 공정 체인 활성화
        print("\n🔧 1. 기존 공정 체인 활성화")
        print("=" * 60)
        
        activate_query = """
        UPDATE process_chain 
        SET is_active = true, updated_at = NOW()
        WHERE id = 1;
        """
        
        try:
            await conn.execute(activate_query)
            print("✅ 공정 체인 1번을 활성화했습니다.")
        except Exception as e:
            print(f"❌ 공정 체인 활성화 실패: {e}")
            return False
        
        # 2. 활성화된 공정 체인 정보 확인
        print("\n🔍 2. 활성화된 공정 체인 정보 확인")
        print("=" * 60)
        
        chain_query = """
        SELECT 
            pc.id,
            pc.chain_name,
            pc.start_process_id,
            pc.end_process_id,
            pc.chain_length,
            pc.is_active,
            pcl.sequence_order,
            pcl.process_id,
            pcl.is_continue_edge,
            p.process_name,
            pae.attrdir_em,
            pae.cumulative_emission
        FROM process_chain pc
        JOIN process_chain_link pcl ON pc.id = pcl.chain_id
        JOIN process p ON pcl.process_id = p.id
        LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
        WHERE pc.id = 1
        ORDER BY pcl.sequence_order;
        """
        
        chain_data = await conn.fetch(chain_query)
        
        if not chain_data:
            print("⚠️ 공정 체인 데이터를 찾을 수 없습니다.")
            return False
        
        print(f"📋 공정 체인: {chain_data[0]['chain_name']}")
        print(f"📊 총 공정 수: {len(chain_data)}")
        print(f"🔗 활성 상태: {'예' if chain_data[0]['is_active'] else '아니오'}")
        print()
        
        print("📋 공정 정보:")
        for data in chain_data:
            print(f"  📊 순서 {data['sequence_order']}: 공정 {data['process_id']} ({data['process_name']})")
            print(f"    자체 배출량: {data['attrdir_em'] or 'N/A'}")
            print(f"    누적 배출량: {data['cumulative_emission'] or 'N/A'}")
            print(f"    continue 엣지: {'예' if data['is_continue_edge'] else '아니오'}")
            print()
        
        # 3. 배출량 누적 전달 실행
        print("\n🧮 3. 배출량 누적 전달 실행")
        print("=" * 60)
        
        print("📊 규칙 1번: 공정→공정 배출량 누적 전달")
        print("  source.cumulative_emission이 target으로 전달되어")
        print("  target.cumulative_emission = source.cumulative_emission + target.attrdir_em")
        print()
        
        # 배출량 누적 전달 실행
        propagation_results = []
        previous_cumulative = 0
        
        for i, data in enumerate(chain_data):
            process_id = data['process_id']
            process_name = data['process_name']
            own_emission = float(data['attrdir_em']) if data['attrdir_em'] else 0.0
            is_continue = data['is_continue_edge']
            sequence_order = data['sequence_order']
            
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
            
            propagation_results.append({
                'sequence_order': sequence_order,
                'process_id': process_id,
                'process_name': process_name,
                'own_emission': own_emission,
                'cumulative_emission': cumulative_emission,
                'propagation_type': propagation_type
            })
            
            previous_cumulative = cumulative_emission
            
            print(f"  📊 순서 {sequence_order}: {process_name} (ID: {process_id})")
            print(f"    자체 배출량: {own_emission}")
            print(f"    누적 배출량: {cumulative_emission}")
            print(f"    전파 유형: {propagation_type}")
            print()
        
        # 4. 실제 DB 업데이트
        print("\n🔧 4. 실제 DB 업데이트")
        print("=" * 60)
        
        print("🔧 실제 DB를 업데이트합니다...")
        
        # 각 공정의 누적 배출량을 실제로 업데이트
        for result in propagation_results:
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
                return False
        
        print("✅ 모든 공정의 누적 배출량 업데이트 완료!")
        
        # 5. 업데이트 후 결과 확인
        print("\n🔍 5. 업데이트 후 결과 확인")
        print("=" * 60)
        
        # 업데이트된 데이터 조회
        updated_query = """
        SELECT 
            pcl.sequence_order,
            pcl.process_id,
            p.process_name,
            pae.attrdir_em,
            pae.cumulative_emission,
            pae.updated_at
        FROM process_chain_link pcl
        JOIN process p ON pcl.process_id = p.id
        LEFT JOIN process_attrdir_emission pae ON pcl.process_id = pae.process_id
        WHERE pcl.chain_id = 1
        ORDER BY pcl.sequence_order;
        """
        
        updated_data = await conn.fetch(updated_query)
        
        print("📋 업데이트된 공정 정보:")
        for data in updated_data:
            print(f"  📊 순서 {data['sequence_order']}: 공정 {data['process_id']} ({data['process_name']})")
            print(f"    자체 배출량: {data['attrdir_em'] or 'N/A'}")
            print(f"    누적 배출량: {data['cumulative_emission'] or 'N/A'}")
            print(f"    업데이트 시간: {data['updated_at']}")
            print()
        
        # 6. 결과 요약
        print("\n📊 6. 결과 요약")
        print("=" * 60)
        
        total_own = sum(r['own_emission'] for r in propagation_results)
        total_cumulative = sum(r['cumulative_emission'] for r in propagation_results)
        final_cumulative = propagation_results[-1]['cumulative_emission'] if propagation_results else 0
        
        print(f"📋 공정 체인: {chain_data[0]['chain_name']}")
        print(f"📊 총 공정 수: {len(propagation_results)}")
        print(f"🧮 총 자체 배출량: {total_own}")
        print(f"🔗 최종 누적 배출량: {final_cumulative}")
        print(f"📈 누적 증가율: {((final_cumulative - total_own) / total_own * 100):.2f}%" if total_own > 0 else "N/A")
        
        # 7. 결과를 JSON 파일로 저장
        print("\n💾 7. 결과를 JSON 파일로 저장")
        print("=" * 60)
        
        final_result = {
            'execution_date': datetime.now().isoformat(),
            'chain_id': 1,
            'chain_name': chain_data[0]['chain_name'],
            'total_processes': len(propagation_results),
            'propagation_results': propagation_results,
            'summary': {
                'total_own_emissions': total_own,
                'total_cumulative_emissions': total_cumulative,
                'final_cumulative_emission': final_cumulative,
                'accumulation_ratio': ((final_cumulative - total_own) / total_own * 100) if total_own > 0 else None
            },
            'status': 'SUCCESS'
        }
        
        with open('emission_propagation_result.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
        
        print("✅ 결과가 emission_propagation_result.json 파일로 저장되었습니다.")
        
        await conn.close()
        print("\n🔗 Railway DB 연결 종료")
        
        return True
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 공정 체인 활성화 및 배출량 전파 테스트 시작")
    print("=" * 60)
    print("📍 규칙 1번: 공정→공정 배출량 누적 전달 실행")
    print("=" * 60)
    
    success = asyncio.run(activate_and_test_chain())
    
    if success:
        print("\n🎯 실행 완료! 다음 단계:")
        print("1. emission_propagation_result.json 파일 확인")
        print("2. 실제 배출량 전파 서비스 구현")
        print("3. API 엔드포인트 생성")
    else:
        print("\n❌ 실행 실패! 오류를 확인하고 다시 시도해주세요.")
