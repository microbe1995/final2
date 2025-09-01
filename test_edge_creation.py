#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 Edge 생성 테스트 스크립트
CBAM 배출량 전파 시스템의 Edge 도메인 테스트
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'service', 'cbam-service'))

async def test_edge_creation():
    """Edge 생성 기능 테스트"""
    print("🔗 Edge 생성 테스트 시작")
    print("=" * 50)
    
    try:
        # Edge 서비스 import
        from app.domain.edge.edge_service import EdgeService
        from app.domain.edge.edge_schema import EdgeCreateRequest
        
        print("✅ Edge 서비스 import 성공")
        
        # Edge 서비스 인스턴스 생성
        edge_service = EdgeService()
        print("✅ Edge 서비스 인스턴스 생성 완료")
        
        # 데이터베이스 초기화
        await edge_service.initialize()
        print("✅ 데이터베이스 초기화 완료")
        
        # 테스트 데이터 준비
        test_edges = [
            {
                "source_node_type": "process",
                "source_id": 165,
                "target_node_type": "process", 
                "target_id": 166,
                "edge_kind": "continue"
            },
            {
                "source_node_type": "process",
                "source_id": 166,
                "target_node_type": "product",
                "target_id": 1,
                "edge_kind": "produce"
            },
            {
                "source_node_type": "product",
                "source_id": 1,
                "target_node_type": "process",
                "target_id": 167,
                "edge_kind": "consume"
            }
        ]
        
        print(f"📋 테스트할 엣지 수: {len(test_edges)}개")
        
        # 각 엣지 생성 테스트
        created_edges = []
        for i, edge_data in enumerate(test_edges, 1):
            print(f"\n🔗 엣지 {i} 생성 테스트:")
            print(f"  소스: {edge_data['source_node_type']}({edge_data['source_id']})")
            print(f"  타겟: {edge_data['target_node_type']}({edge_data['target_id']})")
            print(f"  종류: {edge_data['edge_kind']}")
            
            try:
                # EdgeCreateRequest 객체 생성
                edge_request = EdgeCreateRequest(**edge_data)
                
                # 엣지 생성
                result = await edge_service.create_edge(edge_request)
                
                if result:
                    print(f"  ✅ 엣지 생성 성공: ID {result['id']}")
                    created_edges.append(result)
                else:
                    print(f"  ❌ 엣지 생성 실패: 결과가 None")
                    
            except Exception as e:
                print(f"  ❌ 엣지 생성 실패: {str(e)}")
                import traceback
                print(f"  스택 트레이스: {traceback.format_exc()}")
        
        # 생성된 엣지 목록 조회
        print(f"\n📋 생성된 엣지 목록 조회:")
        try:
            all_edges = await edge_service.get_edges()
            print(f"  총 엣지 수: {len(all_edges)}개")
            
            for edge in all_edges:
                print(f"  - ID {edge['id']}: {edge['source_node_type']}({edge['source_id']}) -> {edge['target_node_type']}({edge['target_id']}) [{edge['edge_kind']}]")
                
        except Exception as e:
            print(f"  ❌ 엣지 목록 조회 실패: {str(e)}")
        
        # 특정 엣지 조회 테스트
        if created_edges:
            print(f"\n🔍 특정 엣지 조회 테스트:")
            test_edge_id = created_edges[0]['id']
            try:
                edge = await edge_service.get_edge(test_edge_id)
                if edge:
                    print(f"  ✅ 엣지 {test_edge_id} 조회 성공:")
                    print(f"    소스: {edge['source_node_type']}({edge['source_id']})")
                    print(f"    타겟: {edge['target_node_type']}({edge['target_id']})")
                    print(f"    종류: {edge['edge_kind']}")
                    print(f"    생성일: {edge['created_at']}")
                else:
                    print(f"  ❌ 엣지 {test_edge_id} 조회 실패: 엣지를 찾을 수 없음")
            except Exception as e:
                print(f"  ❌ 엣지 {test_edge_id} 조회 실패: {str(e)}")
        
        # 배출량 전파 테스트
        print(f"\n🌱 배출량 전파 테스트:")
        try:
            # 공정 165의 배출량 데이터 조회
            emission_data = await edge_service.get_process_emission_data(165)
            if emission_data:
                print(f"  ✅ 공정 165 배출량 데이터 조회 성공:")
                print(f"    자체 배출량: {emission_data['attrdir_em']}")
                print(f"    누적 배출량: {emission_data['cumulative_emission']}")
            else:
                print(f"  ⚠️ 공정 165 배출량 데이터 없음")
            
            # 공정 165에서 나가는 continue 엣지 조회
            continue_edges = await edge_service.get_continue_edges(165)
            print(f"  공정 165의 continue 엣지 수: {len(continue_edges)}개")
            
        except Exception as e:
            print(f"  ❌ 배출량 전파 테스트 실패: {str(e)}")
        
        print(f"\n🎯 테스트 완료!")
        print(f"  성공적으로 생성된 엣지: {len(created_edges)}개")
        
    except ImportError as e:
        print(f"❌ Import 오류: {str(e)}")
        print("프로젝트 구조를 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")

async def test_edge_crud_operations():
    """Edge CRUD 작업 테스트"""
    print("\n🔧 Edge CRUD 작업 테스트")
    print("=" * 50)
    
    try:
        from app.domain.edge.edge_service import EdgeService
        from app.domain.edge.edge_schema import EdgeCreateRequest, EdgeUpdateRequest
        
        edge_service = EdgeService()
        await edge_service.initialize()
        
        # 1. CREATE 테스트
        print("1️⃣ CREATE 테스트")
        create_data = {
            "source_node_type": "process",
            "source_id": 999,
            "target_node_type": "process",
            "target_id": 1000,
            "edge_kind": "continue"
        }
        
        edge_request = EdgeCreateRequest(**create_data)
        created_edge = await edge_service.create_edge(edge_request)
        
        if created_edge:
            print(f"  ✅ 엣지 생성 성공: ID {created_edge['id']}")
            edge_id = created_edge['id']
            
            # 2. READ 테스트
            print("2️⃣ READ 테스트")
            read_edge = await edge_service.get_edge(edge_id)
            if read_edge:
                print(f"  ✅ 엣지 조회 성공: ID {read_edge['id']}")
            else:
                print(f"  ❌ 엣지 조회 실패")
            
            # 3. UPDATE 테스트
            print("3️⃣ UPDATE 테스트")
            update_data = EdgeUpdateRequest(
                source_id=888,
                target_id=999,
                edge_kind="produce"
            )
            
            updated_edge = await edge_service.update_edge(edge_id, update_data)
            if updated_edge:
                print(f"  ✅ 엣지 수정 성공: ID {updated_edge['id']}")
                print(f"    수정된 소스 ID: {updated_edge['source_id']}")
                print(f"    수정된 타겟 ID: {updated_edge['target_id']}")
                print(f"    수정된 종류: {updated_edge['edge_kind']}")
            else:
                print(f"  ❌ 엣지 수정 실패")
            
            # 4. DELETE 테스트
            print("4️⃣ DELETE 테스트")
            delete_success = await edge_service.delete_edge(edge_id)
            if delete_success:
                print(f"  ✅ 엣지 삭제 성공: ID {edge_id}")
                
                # 삭제 확인
                deleted_edge = await edge_service.get_edge(edge_id)
                if not deleted_edge:
                    print(f"  ✅ 삭제 확인 완료: 엣지 {edge_id}가 존재하지 않음")
                else:
                    print(f"  ❌ 삭제 확인 실패: 엣지 {edge_id}가 여전히 존재함")
            else:
                print(f"  ❌ 엣지 삭제 실패: ID {edge_id}")
        
        else:
            print(f"  ❌ 엣지 생성 실패")
        
    except Exception as e:
        print(f"❌ CRUD 테스트 실패: {str(e)}")
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")

async def main():
    """메인 테스트 함수"""
    print("🚀 CBAM Edge 도메인 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 기본 Edge 생성 테스트
    await test_edge_creation()
    
    # CRUD 작업 테스트
    await test_edge_crud_operations()
    
    print("\n🎉 모든 테스트 완료!")
    print(f"📅 테스트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # asyncio 이벤트 루프 실행
    asyncio.run(main())
