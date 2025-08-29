#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge API 테스트 스크립트
백엔드 Edge 생성 및 자동 통합 그룹 생성 기능을 테스트합니다.
"""

import requests
import json
import time
from typing import Dict, Any

# API 기본 설정
BASE_URL = "http://localhost:8001"  # CBAM 서비스 포트
API_BASE = f"{BASE_URL}/api/v1"

def test_edge_creation():
    """Edge 생성 및 자동 통합 그룹 생성 테스트"""
    
    print("🚀 Edge API 테스트 시작")
    print("="*80)
    
    # 1. 기존 공정들 확인
    print("📋 기존 공정들 확인 중...")
    try:
        response = requests.get(f"{API_BASE}/process")
        if response.status_code == 200:
            processes = response.json()
            print(f"✅ 공정 목록 조회 성공: {len(processes)}개")
            for proc in processes[:3]:  # 처음 3개만 표시
                print(f"   - 공정 ID: {proc['id']}, 이름: {proc['process_name']}")
        else:
            print(f"❌ 공정 목록 조회 실패: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 공정 목록 조회 중 오류: {e}")
        return
    
    # 2. Edge 생성 테스트
    print("\n🔗 Edge 생성 테스트...")
    
    # 테스트용 Edge 데이터 (공정 156과 157을 연결)
    edge_data = {
        "source_id": 156,
        "target_id": 157,
        "edge_kind": "continue"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/edge",
            json=edge_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            edge = response.json()
            print(f"✅ Edge 생성 성공: ID {edge['id']}")
            print(f"   소스 공정: {edge['source_id']}")
            print(f"   타겟 공정: {edge['target_id']}")
            print(f"   연결 종류: {edge['edge_kind']}")
        else:
            print(f"❌ Edge 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Edge 생성 중 오류: {e}")
        return
    
    # 3. 잠시 대기 (백엔드 처리 시간)
    print("\n⏳ 백엔드 처리 대기 중... (3초)")
    time.sleep(3)
    
    # 4. 생성된 통합 그룹 확인
    print("\n📋 생성된 통합 그룹 확인 중...")
    try:
        response = requests.get(f"{API_BASE}/sourcestream/chain")
        if response.status_code == 200:
            chains = response.json()
            print(f"✅ 통합 그룹 목록 조회 성공: {len(chains)}개")
            
            for chain in chains:
                print(f"\n   그룹 ID: {chain['id']}")
                print(f"   그룹명: {chain['chain_name']}")
                print(f"   시작공정: {chain['start_process_id']}")
                print(f"   종료공정: {chain['end_process_id']}")
                print(f"   공정개수: {chain['chain_length']}")
                print(f"   활성상태: {chain['is_active']}")
                
                # 그룹 내 공정들의 배출량 확인
                if 'processes' in chain:
                    print(f"   연결된 공정들:")
                    total_emission = 0
                    for proc in chain['processes']:
                        emission = proc.get('attrdir_em', 0)
                        total_emission += emission
                        print(f"     - 공정 ID: {proc['process_id']}, 배출량: {emission}")
                    
                    print(f"   그룹 총 배출량: {total_emission}")
        else:
            print(f"❌ 통합 그룹 목록 조회 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 통합 그룹 확인 중 오류: {e}")
    
    # 5. Edge 목록 확인
    print("\n🔗 생성된 Edge 목록 확인...")
    try:
        response = requests.get(f"{API_BASE}/edge")
        if response.status_code == 200:
            edges = response.json()
            print(f"✅ Edge 목록 조회 성공: {len(edges)}개")
            
            for edge in edges:
                print(f"   - Edge ID: {edge['id']}: {edge['source_id']} -> {edge['target_id']} ({edge['edge_kind']})")
        else:
            print(f"❌ Edge 목록 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Edge 목록 확인 중 오류: {e}")
    
    print("\n" + "="*80)
    print("✅ Edge API 테스트 완료!")
    print("="*80)

def test_process_chain_creation():
    """통합 공정 그룹 생성 테스트"""
    
    print("\n🔄 통합 공정 그룹 생성 테스트")
    print("="*80)
    
    # 추가 Edge 생성 (공정 156 -> 158, 157 -> 158)
    additional_edges = [
        {"source_id": 156, "target_id": 158, "edge_kind": "continue"},
        {"source_id": 157, "target_id": 158, "edge_kind": "continue"}
    ]
    
    for i, edge_data in enumerate(additional_edges, 1):
        print(f"\n🔗 추가 Edge {i} 생성: {edge_data['source_id']} -> {edge_data['target_id']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/edge",
                json=edge_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                edge = response.json()
                print(f"✅ Edge 생성 성공: ID {edge['id']}")
            else:
                print(f"❌ Edge 생성 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Edge 생성 중 오류: {e}")
    
    # 잠시 대기
    print("\n⏳ 백엔드 처리 대기 중... (5초)")
    time.sleep(5)
    
    # 최종 통합 공정 그룹 상태 확인
    print("\n📊 최종 통합 공정 그룹 상태 확인...")
    try:
        response = requests.get(f"{API_BASE}/sourcestream/chain")
        if response.status_code == 200:
            chains = response.json()
            print(f"✅ 최종 통합 공정 그룹: {len(chains)}개")
            
            for chain in chains:
                print(f"\n   그룹 ID: {chain['id']}")
                print(f"   그룹명: {chain['chain_name']}")
                print(f"   공정개수: {chain['chain_length']}")
                
                if 'processes' in chain:
                    process_ids = [proc['process_id'] for proc in chain['processes']]
                    print(f"   포함된 공정: {process_ids}")
        else:
            print(f"❌ 통합 그룹 확인 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 최종 상태 확인 중 오류: {e}")

if __name__ == "__main__":
    # 1. 기본 Edge 생성 테스트
    test_edge_creation()
    
    # 2. 복잡한 통합 그룹 테스트 (선택사항)
    # test_process_chain_creation()
    
    print("\n🎯 테스트 완료!")
    print("프론트엔드에서 노드를 연결해보세요!")
