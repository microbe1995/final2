'use client';

import { useCallback } from 'react';
import { Node, Edge } from '@xyflow/react';

export const useNodeManagement = (
  nodes: Node<any>[],
  edges: Edge<any>[],
  onFlowChange: (nodes: Node[], edges: Edge[]) => void
) => {
  const addProcessNode = useCallback(() => {
    const newNode: Node<any> = {
      id: `node-${Date.now()}`,
      type: 'processNode',
      position: { x: 250, y: 250 },
      data: {
        label: '새 공정 단계',
        processType: 'manufacturing',
        description: '공정 단계 설명을 입력하세요',
        parameters: {},
      },
    };
    
    const newNodes = [...nodes, newNode];
    onFlowChange(newNodes, edges);
    console.log('✅ 공정 단계 추가됨:', newNode);
  }, [nodes, edges, onFlowChange]);

  const addProcessEdge = useCallback(() => {
    // 최소 2개의 노드가 있어야 엣지 추가 가능
    if (nodes.length < 2) {
      alert('엣지를 추가하려면 최소 2개의 노드가 필요합니다.');
      return;
    }

    const newEdge: Edge<any> = {
      id: `edge-${Date.now()}`,
      source: nodes[0].id, // 첫 번째 노드
      target: nodes[1].id, // 두 번째 노드
      type: 'processEdge',
      data: {
        label: '공정 흐름',
        processType: 'standard',
      },
    };
    
    const newEdges = [...edges, newEdge];
    onFlowChange(nodes, newEdges);
    console.log('✅ 공정 연결 추가됨:', newEdge);
  }, [nodes, edges, onFlowChange]);

  const deleteSelectedElements = useCallback(() => {
    const selectedNodes = nodes.filter((node) => node.selected);
    const selectedEdges = edges.filter((edge) => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      const newNodes = nodes.filter((node) => !node.selected);
      const newEdges = edges.filter((edge) => !edge.selected);
      onFlowChange(newNodes, newEdges);
      console.log('✅ 선택된 요소 삭제됨');
    } else {
      alert('삭제할 요소를 선택해주세요.');
    }
  }, [nodes, edges, onFlowChange]);

  return {
    addProcessNode,
    addProcessEdge,
    deleteSelectedElements,
  };
};
