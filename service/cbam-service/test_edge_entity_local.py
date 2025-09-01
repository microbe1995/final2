#!/usr/bin/env python3
"""
로컬에서 Edge 엔티티를 테스트하는 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_edge_entity():
    """Edge 엔티티를 로컬에서 테스트합니다."""
    
    print("🚀 Edge 엔티티 로컬 테스트 시작")
    print("=" * 50)
    
    try:
        # 1. Edge 엔티티 import 테스트
        print("\n🔍 1. Edge 엔티티 import 테스트")
        try:
            from app.domain.edge.edge_entity import Edge
            print("✅ Edge 엔티티 import 성공")
        except Exception as e:
            print(f"❌ Edge 엔티티 import 실패: {e}")
            return
        
        # 2. Edge 엔티티 인스턴스 생성 테스트
        print("\n🔍 2. Edge 엔티티 인스턴스 생성 테스트")
        try:
            edge = Edge(
                source_node_type="process",
                source_id=156,
                target_node_type="process",
                target_id=157,
                edge_kind="continue"
            )
            print("✅ Edge 엔티티 인스턴스 생성 성공")
            print(f"📝 생성된 Edge: {edge}")
            print(f"🆔 Edge ID: {edge.id}")
            print(f"🔗 Source: {edge.source_node_type}:{edge.source_id}")
            print(f"🎯 Target: {edge.target_node_type}:{edge.target_id}")
            print(f"📌 Kind: {edge.edge_kind}")
        except Exception as e:
            print(f"❌ Edge 엔티티 인스턴스 생성 실패: {e}")
            import traceback
            print(f"📋 스택 트레이스: {traceback.format_exc()}")
            return
        
        # 3. Edge 엔티티 to_dict 테스트
        print("\n🔍 3. Edge 엔티티 to_dict 테스트")
        try:
            edge_dict = edge.to_dict()
            print("✅ Edge 엔티티 to_dict 성공")
            print(f"📝 딕셔너리: {edge_dict}")
        except Exception as e:
            print(f"❌ Edge 엔티티 to_dict 실패: {e}")
        
        # 4. Edge 엔티티 from_dict 테스트
        print("\n🔍 4. Edge 엔티티 from_dict 테스트")
        try:
            test_data = {
                "source_node_type": "process",
                "source_id": 158,
                "target_node_type": "process",
                "target_id": 159,
                "edge_kind": "produce"
            }
            new_edge = Edge.from_dict(test_data)
            print("✅ Edge 엔티티 from_dict 성공")
            print(f"📝 새로 생성된 Edge: {new_edge}")
        except Exception as e:
            print(f"❌ Edge 엔티티 from_dict 실패: {e}")
        
        # 5. Base 클래스 확인
        print("\n🔍 5. Base 클래스 확인")
        try:
            print(f"📋 Edge 클래스의 Base: {Edge.__bases__}")
            print(f"📋 Edge 클래스의 __tablename__: {Edge.__tablename__}")
            print(f"📋 Edge 클래스의 __table__: {Edge.__table__}")
        except Exception as e:
            print(f"❌ Base 클래스 확인 실패: {e}")
        
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        import traceback
        print(f"📋 스택 트레이스: {traceback.format_exc()}")
    
    print("\n🎯 Edge 엔티티 로컬 테스트 완료!")

if __name__ == "__main__":
    test_edge_entity()
