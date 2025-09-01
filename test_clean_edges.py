#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
순환 참조가 없는 깨끗한 엣지들로 배출량 전파 테스트
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'service', 'cbam-service'))

async def test_clean_emission_propagation():
    """순환 참조가 없는 깨끗한 엣지들로 배출량 전파 테스트"""
    print("🌱 깨끗한 배출량 전파 테스트 시작")
    print("=" * 50)
    
    try:
        from app.domain.edge.edge_service import EdgeService
        from app.domain.edge.edge_schema import EdgeCreateRequest
        
        edge_service = EdgeService()
        await edge_service.initialize()
        
        # 기존 엣지들 중에서 순환 참조가 없는 것들만 필터링
        all_edges = await edge_service.get_edges()
        
        # 테스트용 깨끗한 엣지들만 선택 (기존 테스트에서 생성된 것들)
        clean_edges = [
            edge for edge in all_edges 
            if edge['source_id'] in [165, 166, 167, 999, 1000] and 
               edge['target_id'] in [165, 166, 167, 1, 999, 1000]
        ]
        
        print(f"📋 깨끗한 엣지 수: {len(clean_edges)}개")
        for edge in clean_edges:
            print(f"  - {edge['source_node_type']}({edge['source_id']}) -> {edge['target_node_type']}({edge['target_id']}) [{edge['edge_kind']}]")
        
        # 순환 참조 검사
        has_cycle = await edge_service._detect_cycles(clean_edges)
        if has_cycle:
            print("❌ 깨끗한 엣지들에도 순환 참조가 발견되었습니다.")
            return
        else:
            print("✅ 깨끗한 엣지들에는 순환 참조가 없습니다.")
        
        # 1. 공정→공정 배출량 전파 테스트
        print("\n1️⃣ 공정→공정 배출량 전파 테스트")
        success = await edge_service.propagate_emissions_continue(165, 166)
        if success:
            print(f"  ✅ 공정 165 → 공정 166 배출량 전파 성공")
            
            # 업데이트된 배출량 확인
            updated_emission = await edge_service.get_process_emission_data(166)
            if updated_emission:
                print(f"    공정 166 누적 배출량: {updated_emission['cumulative_emission']}")
        else:
            print(f"  ❌ 공정 165 → 공정 166 배출량 전파 실패")
        
        # 2. 공정→제품 배출량 전파 테스트
        print("\n2️⃣ 공정→제품 배출량 전파 테스트")
        success = await edge_service.propagate_emissions_produce(166, 1)
        if success:
            print(f"  ✅ 공정 166 → 제품 1 배출량 전파 성공")
            
            # 제품 배출량 확인
            product_data = await edge_service.edge_repository.get_product_data(1)
            if product_data:
                print(f"    제품 1 배출량: {product_data['attr_em']}")
        else:
            print(f"  ❌ 공정 166 → 제품 1 배출량 전파 실패")
        
        # 3. 제품→공정 배출량 전파 테스트
        print("\n3️⃣ 제품→공정 배출량 전파 테스트")
        success = await edge_service.propagate_emissions_consume(1, 167)
        if success:
            print(f"  ✅ 제품 1 → 공정 167 배출량 전파 성공")
            
            # 업데이트된 공정 배출량 확인
            updated_emission = await edge_service.get_process_emission_data(167)
            if updated_emission:
                print(f"    공정 167 누적 배출량: {updated_emission['cumulative_emission']}")
        else:
            print(f"  ❌ 제품 1 → 공정 167 배출량 전파 실패")
        
        # 4. 전체 그래프 배출량 전파 테스트 (깨끗한 엣지들만)
        print("\n4️⃣ 전체 그래프 배출량 전파 테스트 (깨끗한 엣지들만)")
        
        # 임시로 깨끗한 엣지들만 사용하여 테스트
        original_get_edges = edge_service.get_edges
        edge_service.get_edges = lambda: asyncio.create_task(asyncio.coroutine(lambda: clean_edges)())
        
        try:
            propagation_result = await edge_service.propagate_emissions_full_graph()
            
            if propagation_result['success']:
                print(f"  ✅ 전체 그래프 배출량 전파 성공")
                print(f"    총 엣지: {propagation_result['total_edges']}개")
                print(f"    성공률: {propagation_result['success_rate']:.1f}%")
                
                results = propagation_result['propagation_results']
                print(f"    Continue 엣지: {results['continue_edges']}개")
                print(f"    Produce 엣지: {results['produce_edges']}개")
                print(f"    Consume 엣지: {results['consume_edges']}개")
                print(f"    성공: {results['success_count']}개, 실패: {results['error_count']}개")
            else:
                print(f"  ❌ 전체 그래프 배출량 전파 실패: {propagation_result.get('error', 'Unknown error')}")
        finally:
            # 원래 메서드 복원
            edge_service.get_edges = original_get_edges
        
    except Exception as e:
        print(f"❌ 깨끗한 배출량 전파 테스트 실패: {str(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")

async def main():
    """메인 테스트 함수"""
    print("🚀 깨끗한 배출량 전파 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    await test_clean_emission_propagation()
    
    print("\n🎉 깨끗한 배출량 전파 테스트 완료!")
    print(f"📅 테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
