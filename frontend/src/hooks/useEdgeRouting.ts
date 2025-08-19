'use client';

import { useCallback, useState } from 'react';
import type { Edge, Connection } from '@xyflow/react';

// ============================================================================
// 🎯 Edge Routing 타입 정의
// ============================================================================

export type EdgeRoutingType = 'default' | 'smart' | 'orthogonal' | 'bezier' | 'straight' | 'step';

export interface EdgeRoutingOptions {
  type: EdgeRoutingType;
  smartEdge?: boolean;
  orthogonal?: boolean;
  bezierCurve?: boolean;
  stepSize?: number;
  smoothness?: number;
  avoidNodes?: boolean;
  gridSnap?: boolean;
  gridSize?: number;
}

export interface EdgeRoutingResult {
  edges: Edge[];
  routingTime: number;
  complexity: 'low' | 'medium' | 'high';
}

// ============================================================================
// 🎯 Edge Routing 훅
// ============================================================================

export const useEdgeRouting = () => {
  const [isRouting, setIsRouting] = useState(false);
  const [currentRoutingType, setCurrentRoutingType] = useState<EdgeRoutingType>('default');

  // ============================================================================
  // 🎯 Smart Edge Routing (노드 충돌 방지)
  // ============================================================================
  
  const applySmartEdgeRouting = useCallback(async (
    edges: Edge[],
    nodes: any[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    setIsRouting(true);
    setCurrentRoutingType('smart');
    
    try {
      const startTime = performance.now();
      
      const defaultOptions: EdgeRoutingOptions = {
        type: 'smart',
        smartEdge: true,
        avoidNodes: true,
        gridSnap: true,
        gridSize: 20,
        ...options
      };

      // Smart Edge 라우팅 적용
      const routedEdges = edges.map(edge => {
        // 노드 충돌을 피하는 경로 계산
        const sourceNode = nodes.find(n => n.id === edge.source);
        const targetNode = nodes.find(n => n.id === edge.target);
        
        if (sourceNode && targetNode) {
          // 간단한 충돌 방지 로직 (실제로는 더 복잡한 알고리즘 필요)
          const midPoint = {
            x: (sourceNode.position.x + targetNode.position.x) / 2,
            y: (sourceNode.position.y + targetNode.position.y) / 2
          };
          
          // 노드 간 거리에 따라 경로 조정
          const distance = Math.sqrt(
            Math.pow(targetNode.position.x - sourceNode.position.x, 2) +
            Math.pow(targetNode.position.y - sourceNode.position.y, 2)
          );
          
          if (distance < 100) {
            // 가까운 노드들은 곡선으로 연결
            return {
              ...edge,
              type: 'smartEdge',
              data: {
                ...edge.data,
                routingType: 'smart',
                avoidNodes: true
              }
            };
          }
        }
        
        return edge;
      });

      const routingTime = performance.now() - startTime;
      
      return {
        edges: routedEdges,
        routingTime,
        complexity: edges.length > 20 ? 'high' : edges.length > 10 ? 'medium' : 'low'
      };
    } finally {
      setIsRouting(false);
    }
  }, []);

  // ============================================================================
  // 🎯 Orthogonal Edge Routing (직교 다이어그램)
  // ============================================================================
  
  const applyOrthogonalRouting = useCallback(async (
    edges: Edge[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    setIsRouting(true);
    setCurrentRoutingType('orthogonal');
    
    try {
      const startTime = performance.now();
      
      const defaultOptions: EdgeRoutingOptions = {
        type: 'orthogonal',
        orthogonal: true,
        stepSize: 20,
        gridSnap: true,
        gridSize: 20,
        ...options
      };

      // Orthogonal 라우팅 적용
      const routedEdges = edges.map(edge => ({
        ...edge,
        type: 'orthogonalEdge',
        data: {
          ...edge.data,
          routingType: 'orthogonal',
          stepSize: defaultOptions.stepSize,
          gridSnap: defaultOptions.gridSnap
        }
      }));

      const routingTime = performance.now() - startTime;
      
      return {
        edges: routedEdges,
        routingTime,
        complexity: edges.length > 15 ? 'high' : edges.length > 8 ? 'medium' : 'low'
      };
    } finally {
      setIsRouting(false);
    }
  }, []);

  // ============================================================================
  // 🎯 Bezier Curve Routing (부드러운 곡선)
  // ============================================================================
  
  const applyBezierRouting = useCallback(async (
    edges: Edge[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    setIsRouting(true);
    setCurrentRoutingType('bezier');
    
    try {
      const startTime = performance.now();
      
      const defaultOptions: EdgeRoutingOptions = {
        type: 'bezier',
        bezierCurve: true,
        smoothness: 0.5,
        ...options
      };

      // Bezier 곡선 라우팅 적용
      const routedEdges = edges.map(edge => ({
        ...edge,
        type: 'bezierEdge',
        data: {
          ...edge.data,
          routingType: 'bezier',
          smoothness: defaultOptions.smoothness
        }
      }));

      const routingTime = performance.now() - startTime;
      
      return {
        edges: routedEdges,
        routingTime,
        complexity: 'low' // Bezier는 계산이 간단
      };
    } finally {
      setIsRouting(false);
    }
  }, []);

  // ============================================================================
  // 🎯 Step Edge Routing (계단식 경로)
  // ============================================================================
  
  const applyStepRouting = useCallback(async (
    edges: Edge[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    setIsRouting(true);
    setCurrentRoutingType('step');
    
    try {
      const startTime = performance.now();
      
      const defaultOptions: EdgeRoutingOptions = {
        type: 'step',
        stepSize: 30,
        gridSnap: true,
        gridSize: 30,
        ...options
      };

      // Step 라우팅 적용
      const routedEdges = edges.map(edge => ({
        ...edge,
        type: 'stepEdge',
        data: {
          ...edge.data,
          routingType: 'step',
          stepSize: defaultOptions.stepSize,
          gridSnap: defaultOptions.gridSnap
        }
      }));

      const routingTime = performance.now() - startTime;
      
      return {
        edges: routedEdges,
        routingTime,
        complexity: 'low' // Step은 계산이 간단
      };
    } finally {
      setIsRouting(false);
    }
  }, []);

  // ============================================================================
  // 🎯 자동 라우팅 선택
  // ============================================================================
  
  const applyAutoRouting = useCallback(async (
    edges: Edge[],
    nodes: any[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    // 엣지 수와 노드 배치에 따라 적절한 라우팅 선택
    if (edges.length <= 5) {
      return applyBezierRouting(edges, options);
    } else if (edges.length <= 15) {
      return applySmartEdgeRouting(edges, nodes, options);
    } else {
      return applyOrthogonalRouting(edges, options);
    }
  }, [applyBezierRouting, applySmartEdgeRouting, applyOrthogonalRouting]);

  // ============================================================================
  // 🎯 라우팅 최적화
  // ============================================================================
  
  const optimizeRouting = useCallback(async (
    edges: Edge[],
    nodes: any[],
    options: Partial<EdgeRoutingOptions> = {}
  ): Promise<EdgeRoutingResult> => {
    setIsRouting(true);
    
    try {
      const startTime = performance.now();
      
      // 1단계: Smart Edge로 기본 라우팅
      const smartResult = await applySmartEdgeRouting(edges, nodes, options);
      
      // 2단계: 필요시 Orthogonal로 정리
      if (smartResult.complexity === 'high') {
        const orthogonalResult = await applyOrthogonalRouting(smartResult.edges, options);
        return {
          ...orthogonalResult,
          routingTime: performance.now() - startTime
        };
      }
      
      return smartResult;
    } finally {
      setIsRouting(false);
    }
  }, [applySmartEdgeRouting, applyOrthogonalRouting]);

  // ============================================================================
  // 🎯 라우팅 리셋
  // ============================================================================
  
  const resetRouting = useCallback((edges: Edge[]): EdgeRoutingResult => {
    setCurrentRoutingType('default');
    
    const resetEdges = edges.map(edge => ({
      ...edge,
      type: 'default',
      data: {
        ...edge.data,
        routingType: 'default'
      }
    }));

    return {
      edges: resetEdges,
      routingTime: 0,
      complexity: 'low'
    };
  }, []);

  return {
    // 상태
    isRouting,
    currentRoutingType,
    
    // 라우팅 함수들
    applySmartEdgeRouting,
    applyOrthogonalRouting,
    applyBezierRouting,
    applyStepRouting,
    applyAutoRouting,
    optimizeRouting,
    resetRouting,
    
    // 유틸리티
    getRoutingOptions: (type: EdgeRoutingType): EdgeRoutingOptions => {
      const baseOptions: EdgeRoutingOptions = {
        type,
        smartEdge: false,
        orthogonal: false,
        bezierCurve: false,
        stepSize: 20,
        smoothness: 0.5,
        avoidNodes: false,
        gridSnap: false,
        gridSize: 20
      };

      switch (type) {
        case 'smart':
          return { ...baseOptions, smartEdge: true, avoidNodes: true, gridSnap: true };
        case 'orthogonal':
          return { ...baseOptions, orthogonal: true, gridSnap: true };
        case 'bezier':
          return { ...baseOptions, bezierCurve: true };
        case 'step':
          return { ...baseOptions, stepSize: 30, gridSnap: true, gridSize: 30 };
        default:
          return baseOptions;
      }
    }
  };
};
