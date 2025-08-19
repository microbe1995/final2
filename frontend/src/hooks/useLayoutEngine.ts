'use client';

import { useCallback, useState } from 'react';
import type { Node, Edge } from '@xyflow/react';
import ELK from 'elkjs';

// ============================================================================
// 🎯 ELK Layout Engine 타입 정의
// ============================================================================

export type LayoutAlgorithm = 'elk' | 'manual';

export interface LayoutOptions {
  algorithm: LayoutAlgorithm;
  direction?: 'DOWN' | 'UP' | 'RIGHT' | 'LEFT';
  spacing?: number;
  padding?: number;
  nodeSep?: number;
  rankSep?: number;
  animate?: boolean;
  layout?: 'layered' | 'force' | 'tree' | 'radial' | 'compound';
}

export interface LayoutResult {
  nodes: Node[];
  edges: Edge[];
  duration: number;
}

// ============================================================================
// 🎯 ELK Layout Engine 훅
// ============================================================================

export const useLayoutEngine = () => {
  const [isLayouting, setIsLayouting] = useState(false);
  const [currentAlgorithm, setCurrentAlgorithm] = useState<LayoutAlgorithm>('manual');

  // ============================================================================
  // 🎯 ELK Layout (고급 레이아웃)
  // ============================================================================
  
  const applyELKLayout = useCallback(async (
    nodes: Node[],
    edges: Edge[],
    options: Partial<LayoutOptions> = {}
  ): Promise<LayoutResult> => {
    setIsLayouting(true);
    setCurrentAlgorithm('elk');
    
    try {
      const startTime = performance.now();
      
      // ELK 기본 설정
      const defaultOptions: LayoutOptions = {
        algorithm: 'elk',
        direction: 'DOWN',
        spacing: 60,
        padding: 30,
        nodeSep: 60,
        rankSep: 120,
        animate: true,
        layout: 'layered',
        ...options
      };

      // ELK 인스턴스 생성
      const elk = new ELK();
      
      // ELK 그래프 데이터 구조 생성
      const elkGraph = {
        id: 'root',
        layoutOptions: {
          'elk.algorithm': defaultOptions.layout || 'layered',
          'elk.direction': defaultOptions.direction || 'DOWN',
          'elk.spacing.nodeNode': String(defaultOptions.nodeSep || 60),
          'elk.layered.spacing.nodeNodeBetweenLayers': String(defaultOptions.rankSep || 120),
          'elk.padding': `[${defaultOptions.padding || 30}, ${defaultOptions.padding || 30}, ${defaultOptions.padding || 30}, ${defaultOptions.padding || 30}]`,
        },
        children: nodes.map(node => ({
          id: node.id,
          width: (node.style?.width as number) || 150,
          height: (node.style?.height as number) || 50,
          x: node.position.x,
          y: node.position.y,
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          sources: [edge.source],
          targets: [edge.target],
        })),
      };

      // ELK 레이아웃 계산 실행
      const result = await elk.layout(elkGraph);
      
      // 계산된 위치로 노드 업데이트
      const layoutedNodes = nodes.map(node => {
        const elkNode = result.children?.find(n => n.id === node.id);
        return {
          ...node,
          position: {
            x: elkNode?.x || node.position.x,
            y: elkNode?.y || node.position.y,
          },
        };
      });

      const duration = performance.now() - startTime;
      
      return {
        nodes: layoutedNodes,
        edges,
        duration
      };
    } finally {
      setIsLayouting(false);
    }
  }, []);

  // ============================================================================
  // 🎯 자동 레이아웃 (ELK 기반)
  // ============================================================================
  
  const applyAutoLayout = useCallback(async (
    nodes: Node[],
    edges: Edge[],
    options: Partial<LayoutOptions> = {}
  ): Promise<LayoutResult> => {
    // 노드 수에 따라 적절한 ELK 레이아웃 선택
    let layoutType: 'layered' | 'force' | 'tree' = 'layered';
    
    if (nodes.length <= 5) {
      layoutType = 'tree';
    } else if (nodes.length <= 20) {
      layoutType = 'layered';
    } else {
      layoutType = 'force';
    }
    
    return applyELKLayout(nodes, edges, { ...options, layout: layoutType });
  }, [applyELKLayout]);

  // ============================================================================
  // 🎯 레이아웃 리셋
  // ============================================================================
  
  const resetLayout = useCallback((nodes: Node[], edges: Edge[]): LayoutResult => {
    setCurrentAlgorithm('manual');
    
    const resetNodes = nodes.map(node => ({
      ...node,
      position: { x: 0, y: 0 }
    }));

    return {
      nodes: resetNodes,
      edges,
      duration: 0
    };
  }, []);

  return {
    // 상태
    isLayouting,
    currentAlgorithm,
    
    // 레이아웃 함수들
    applyELKLayout,
    applyAutoLayout,
    resetLayout,
    
    // 유틸리티
    getLayoutOptions: (algorithm: LayoutAlgorithm): LayoutOptions => {
      const baseOptions: LayoutOptions = {
        algorithm,
        direction: 'DOWN',
        spacing: 60,
        padding: 30,
        nodeSep: 60,
        rankSep: 120,
        animate: true,
        layout: 'layered'
      };

      return baseOptions;
    }
  };
};
