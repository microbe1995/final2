#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 노드 연결 기능 테스트 스크립트
React Flow의 핸들 ID 생성과 연결 검증 로직을 시뮬레이션합니다.
"""

import re
import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class NodeType(Enum):
    PRODUCT = "product"
    PROCESS = "process"
    GROUP = "group"

class Position(Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

@dataclass
class Node:
    id: str
    type: NodeType
    node_id: str
    label: str
    description: str

@dataclass
class Handle:
    id: str
    position: Position
    type: str = "source"

@dataclass
class Connection:
    source: str
    target: str
    source_handle: str
    target_handle: str

@dataclass
class Edge:
    id: str
    source: str
    target: str
    source_handle: str
    target_handle: str
    type: str = "custom"

class NodeConnectionTester:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.handles: Dict[str, List[Handle]] = {}
        self.edges: List[Edge] = []
        self.handle_counter = 0
        
    def create_node(self, node_type: NodeType, node_id: str, label: str, description: str) -> Node:
        """노드 생성"""
        node = Node(
            id=f"{node_type.value}-{node_id}-{self._generate_random_suffix()}",
            type=node_type,
            node_id=node_id,
            label=label,
            description=description
        )
        self.nodes[node.id] = node
        self._create_handles_for_node(node)
        return node
    
    def _generate_random_suffix(self) -> str:
        """랜덤 접미사 생성 (React Flow 스타일)"""
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    
    def _create_handles_for_node(self, node: Node):
        """노드에 4방향 핸들 생성 (React Flow 시뮬레이션)"""
        handles = []
        for position in Position:
            # React Flow가 생성하는 실제 핸들 ID 형식 시뮬레이션
            handle_id = f"{self.handle_counter}-{position.value}"
            self.handle_counter += 1
            
            handle = Handle(
                id=handle_id,
                position=position,
                type="source"
            )
            handles.append(handle)
        
        self.handles[node.id] = handles
        print(f"✅ 노드 '{node.label}'에 핸들 생성: {[h.id for h in handles]}")
    
    def validate_connection(self, connection: Connection) -> Tuple[bool, str]:
        """연결 검증 로직 (실제 ProcessManager와 동일)"""
        print(f"🔍 연결 검증 시작: {connection.source} → {connection.target}")
        
        # 1. 같은 노드 간 연결 방지
        if connection.source == connection.target:
            print(f"❌ 같은 노드 간 연결 시도: {connection.source}")
            return False, "same_node"
        
        # 2. 핸들 ID 존재 여부 확인
        if not connection.source_handle or not connection.target_handle:
            print(f"❌ 핸들 ID 누락: source={connection.source_handle}, target={connection.target_handle}")
            return False, "missing_handles"
        
        # 3. 핸들 ID 형식 확인 (React Flow의 실제 형식)
        handle_pattern = r'^\d+-(left|right|top|bottom)$'
        if not re.match(handle_pattern, connection.source_handle) or not re.match(handle_pattern, connection.target_handle):
            print(f"❌ 핸들 ID 형식 불일치: source={connection.source_handle}, target={connection.target_handle}")
            return False, "invalid_handle_format"
        
        # 4. 이미 존재하는 연결 확인
        existing_edge = self._find_existing_edge(connection.source, connection.target)
        if existing_edge:
            print(f"❌ 이미 존재하는 연결: {existing_edge.id}")
            return False, "duplicate_edge"
        
        print("✅ 연결 검증 통과")
        return True, "valid"
    
    def _find_existing_edge(self, source: str, target: str) -> Optional[Edge]:
        """기존 연결 찾기"""
        for edge in self.edges:
            if (edge.source == source and edge.target == target) or \
               (edge.source == target and edge.target == source):
                return edge
        return None
    
    def create_connection(self, source_node_id: str, target_node_id: str, 
                         source_position: Position, target_position: Position) -> bool:
        """연결 생성"""
        # 핸들 ID 찾기
        source_handle = self._find_handle_by_position(source_node_id, source_position)
        target_handle = self._find_handle_by_position(target_node_id, target_position)
        
        if not source_handle or not target_handle:
            print(f"❌ 핸들을 찾을 수 없음: source={source_position.value}, target={target_position.value}")
            return False
        
        connection = Connection(
            source=source_node_id,
            target=target_node_id,
            source_handle=source_handle.id,
            target_handle=target_handle.id
        )
        
        # 연결 검증
        is_valid, reason = self.validate_connection(connection)
        if not is_valid:
            print(f"❌ 연결 실패: {reason}")
            return False
        
        # Edge 생성
        edge = Edge(
            id=f"e-{int(time.time() * 1000)}",
            source=connection.source,
            target=connection.target,
            source_handle=connection.source_handle,
            target_handle=connection.target_handle
        )
        
        self.edges.append(edge)
        print(f"✅ 연결 성공: {connection.source} → {connection.target}")
        return True
    
    def _find_handle_by_position(self, node_id: str, position: Position) -> Optional[Handle]:
        """위치별 핸들 찾기"""
        if node_id not in self.handles:
            return None
        
        for handle in self.handles[node_id]:
            if handle.position == position:
                return handle
        return None
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "="*60)
        print("📊 테스트 결과 요약")
        print("="*60)
        
        print(f"📦 생성된 노드: {len(self.nodes)}개")
        for node in self.nodes.values():
            print(f"  - {node.label} ({node.id})")
        
        print(f"🔗 생성된 연결: {len(self.edges)}개")
        for edge in self.edges:
            source_label = self.nodes[edge.source].label
            target_label = self.nodes[edge.target].label
            print(f"  - {source_label} → {target_label}")
        
        print(f"🎯 총 핸들: {sum(len(handles) for handles in self.handles.values())}개")
        print("="*60)

def run_connection_tests():
    """연결 테스트 실행"""
    print("🚀 노드 연결 테스트 시작")
    print("="*60)
    
    tester = NodeConnectionTester()
    
    # 테스트 노드 생성
    print("\n📦 테스트 노드 생성")
    print("-"*40)
    
    product_node = tester.create_node(
        NodeType.PRODUCT, "123", "테스트 제품", "연결 테스트용 제품"
    )
    
    process_node = tester.create_node(
        NodeType.PROCESS, "456", "테스트 공정", "연결 테스트용 공정"
    )
    
    group_node = tester.create_node(
        NodeType.GROUP, "789", "테스트 그룹", "연결 테스트용 그룹"
    )
    
    # 테스트 케이스들
    print("\n🔗 연결 테스트 실행")
    print("-"*40)
    
    test_cases = [
        {
            "name": "제품 → 공정 연결 (정상)",
            "source": product_node.id,
            "target": process_node.id,
            "source_pos": Position.RIGHT,
            "target_pos": Position.LEFT,
            "expected": True
        },
        {
            "name": "공정 → 그룹 연결 (정상)",
            "source": process_node.id,
            "target": group_node.id,
            "source_pos": Position.TOP,
            "target_pos": Position.BOTTOM,
            "expected": True
        },
        {
            "name": "같은 노드 연결 (실패 예상)",
            "source": product_node.id,
            "target": product_node.id,
            "source_pos": Position.LEFT,
            "target_pos": Position.RIGHT,
            "expected": False
        },
        {
            "name": "중복 연결 시도 (실패 예상)",
            "source": product_node.id,
            "target": process_node.id,
            "source_pos": Position.BOTTOM,
            "target_pos": Position.TOP,
            "expected": False  # 이미 연결되어 있으므로 실패
        },
        {
            "name": "그룹 → 제품 연결 (정상)",
            "source": group_node.id,
            "target": product_node.id,
            "source_pos": Position.LEFT,
            "target_pos": Position.BOTTOM,
            "expected": True
        }
    ]
    
    # 테스트 실행
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 테스트 {i}: {test_case['name']}")
        print(f"   소스: {test_case['source']} ({test_case['source_pos'].value})")
        print(f"   타겟: {test_case['target']} ({test_case['target_pos'].value})")
        
        result = tester.create_connection(
            test_case['source'],
            test_case['target'],
            test_case['source_pos'],
            test_case['target_pos']
        )
        
        if result == test_case['expected']:
            print(f"   ✅ 예상 결과와 일치: {result}")
            passed_tests += 1
        else:
            print(f"   ❌ 예상 결과와 불일치: 예상={test_case['expected']}, 실제={result}")
        
        time.sleep(0.5)  # 테스트 간 간격
    
    # 결과 요약
    print("\n" + "="*60)
    print("🎯 최종 테스트 결과")
    print("="*60)
    print(f"통과: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    
    tester.print_summary()

def run_handle_id_tests():
    """핸들 ID 생성 테스트"""
    print("\n🔧 핸들 ID 생성 테스트")
    print("-"*40)
    
    tester = NodeConnectionTester()
    
    # 노드 생성
    node = tester.create_node(NodeType.PRODUCT, "999", "핸들 테스트 노드", "핸들 ID 테스트용")
    
    # 핸들 ID 패턴 테스트
    handle_pattern = r'^\d+-(left|right|top|bottom)$'
    
    print("\n핸들 ID 형식 검증:")
    for handle in tester.handles[node.id]:
        is_valid = bool(re.match(handle_pattern, handle.id))
        print(f"  {handle.id}: {'✅' if is_valid else '❌'} ({handle.position.value})")
    
    # 잘못된 핸들 ID 테스트
    invalid_handles = [
        "invalid-handle",
        "abc-left",
        "123-invalid",
        "handle-123",
        ""
    ]
    
    print("\n잘못된 핸들 ID 테스트:")
    for handle_id in invalid_handles:
        is_valid = bool(re.match(handle_pattern, handle_id))
        print(f"  {handle_id}: {'✅' if is_valid else '❌'}")

if __name__ == "__main__":
    print("🔧 React Flow 노드 연결 테스트 스크립트")
    print("="*60)
    
    # 핸들 ID 테스트
    run_handle_id_tests()
    
    # 연결 테스트
    run_connection_tests()
    
    print("\n✅ 테스트 완료!")
