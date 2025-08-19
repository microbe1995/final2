import type { Node, Edge, BuiltInNode, BuiltInEdge } from '@xyflow/react';

// ============================================================================
// 🎯 Process Flow 관련 타입 정의
// ============================================================================

// Process Node 데이터 타입
export interface ProcessNodeData {
  label: string;
  description?: string;
  color?: string;
  icon?: string;
  processType?: 'start' | 'process' | 'end' | 'manufacturing' | 'inspection' | 'packaging' | 'transport' | 'storage';
  parameters?: Record<string, any>;
  metadata?: Record<string, any>;
  // Sub Flow 지원
  parentId?: string;
  extent?: 'parent' | 'free';
  [key: string]: unknown; // 인덱스 시그니처 추가
}

// Process Edge 데이터 타입
export interface ProcessEdgeData {
  label: string;
  processType: 'standard' | 'conditional' | 'parallel' | 'sequential';
  conditions?: Record<string, any>;
  [key: string]: unknown; // 인덱스 시그니처 추가
}

// 커스텀 노드 타입
export type ProcessNode = Node<ProcessNodeData, 'processNode'>;

// Group Node 데이터 타입 (Sub Flow 지원)
export interface GroupNodeData {
  label: string;
  description?: string;
  groupType: 'process' | 'subprocess' | 'workflow';
  childCount: number;
  isExpanded: boolean;
  style?: React.CSSProperties;
  // Sub Flow 관련
  children?: string[]; // 자식 노드 ID 목록
  parentExtent?: 'parent' | 'free';
  [key: string]: unknown; // 인덱스 시그니처 추가
}

// Group Node 타입
export type GroupNode = Node<GroupNodeData, 'groupNode'>;

// 커스텀 엣지 타입
export type ProcessEdge = Edge<ProcessEdgeData, 'processEdge'>;

// 확장된 노드 데이터 타입 (모든 노드에서 사용 가능)
export interface ExtendedNodeData {
  label: string;
  description?: string;
  color?: string;
  icon?: string;
  processType?: 'start' | 'process' | 'end' | 'manufacturing' | 'inspection' | 'packaging' | 'transport' | 'storage';
  parameters?: Record<string, any>;
  metadata?: Record<string, any>;
  [key: string]: unknown;
}

// 전체 노드 타입 (확장된 데이터 타입 사용)
export type AppNodeType = Node<ExtendedNodeData>;

// 전체 엣지 타입 (내장 엣지 + 커스텀 엣지)
export type AppEdgeType = BuiltInEdge | ProcessEdge;

// ============================================================================
// 🎯 Canvas 데이터 타입
// ============================================================================

export interface CanvasData {
  id?: string;
  name: string;
  description: string;
  nodes: any[];  // AppNodeType[] → any[]로 변경하여 타입 호환성 문제 해결
  edges: any[];  // AppEdgeType[] → any[]로 변경하여 타입 호환성 문제 해결
  metadata?: {
    createdAt: string;
    updatedAt: string;
    nodeCount: number;
    edgeCount: number;
  };
}

// ============================================================================
// 🎯 Flow 데이터 타입
// ============================================================================

export interface FlowData {
  nodes: ProcessNode[];
  edges: ProcessEdge[];
  metadata?: any;
}

// ============================================================================
// 🎯 타입 가드 함수들
// ============================================================================

export function isProcessNode(node: AppNodeType): node is ProcessNode {
  return node.type === 'processNode';
}

export function isProcessEdge(edge: AppEdgeType): edge is ProcessEdge {
  return edge.type === 'processEdge';
}

export function isManufacturingNode(node: AppNodeType): node is ProcessNode {
  return isProcessNode(node) && node.data.processType === 'manufacturing';
}

export function isInspectionNode(node: AppNodeType): node is ProcessNode {
  return isProcessNode(node) && node.data.processType === 'inspection';
}

export function isPackagingNode(node: AppNodeType): node is ProcessNode {
  return isProcessNode(node) && node.data.processType === 'packaging';
}
