import type { Node, Edge } from '@xyflow/react';

// ============================================================================
// 🎯 간소화된 React Flow 타입 정의
// ============================================================================

export interface FlowNode extends Node {
  data: {
    label: string;
    [key: string]: any; // 향후 속성 확장을 위한 여분 공간
  };
}

export interface FlowEdge extends Edge {
  data?: {
    label?: string;
    [key: string]: any; // 향후 속성 확장을 위한 여분 공간
  };
}

// ============================================================================
// 🎯 플로우 상태 관리 타입
// ============================================================================

export interface FlowState {
  nodes: FlowNode[];
  edges: FlowEdge[];
}

export interface FlowChangeHandler {
  (nodes: FlowNode[], edges: FlowEdge[]): void;
}