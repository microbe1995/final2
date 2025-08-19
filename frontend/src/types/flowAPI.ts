import type { Node, Edge } from '@xyflow/react';

// ============================================================================
// 🎯 백엔드 API 응답 타입 정의 (boundary-service 스키마와 매핑)
// ============================================================================

export interface FlowData {
  id: string;
  name: string;
  description?: string;
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
  created_at: string;
  updated_at: string;
}

export interface NodeData {
  id: string;
  flow_id: string;
  node_id: string;
  type: string;
  position: {
    x: number;
    y: number;
  };
  data: Record<string, any>;
  width?: number;
  height?: number;
  style?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface EdgeData {
  id: string;
  flow_id: string;
  edge_id: string;
  source: string;
  target: string;
  source_handle?: string;
  target_handle?: string;
  type?: string;
  data?: Record<string, any>;
  style?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// 🎯 API 요청/응답 스키마
// ============================================================================

export interface CreateFlowRequest {
  name: string;
  description?: string;
  settings?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface FlowStateResponse {
  flow: FlowData;
  nodes: NodeData[];
  edges: EdgeData[];
}

export interface CreateNodeRequest {
  flow_id: string;
  node_id: string;
  type: string;
  position: {
    x: number;
    y: number;
  };
  data: Record<string, any>;
  width?: number;
  height?: number;
  style?: Record<string, any>;
}

export interface CreateEdgeRequest {
  flow_id: string;
  edge_id: string;
  source: string;
  target: string;
  source_handle?: string;
  target_handle?: string;
  type?: string;
  data?: Record<string, any>;
  style?: Record<string, any>;
}

export interface UpdateViewportRequest {
  flow_id: string;
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
}

// ============================================================================
// 🎯 프론트엔드-백엔드 데이터 변환 유틸리티 타입
// ============================================================================

export interface ReactFlowState {
  flowId: string;
  nodes: Node[];
  edges: Edge[];
  viewport: {
    x: number;
    y: number;
    zoom: number;
  };
}
