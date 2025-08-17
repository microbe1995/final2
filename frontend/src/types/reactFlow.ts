import type { Node, Edge, BuiltInNode, BuiltInEdge } from '@xyflow/react';

// ============================================================================
// 🎯 Process Flow 관련 타입 정의
// ============================================================================

// Process Node 데이터 타입
export interface ProcessNodeData {
  label: string;
  description: string;
  processType: 'manufacturing' | 'inspection' | 'packaging' | 'transport' | 'storage';
  parameters: Record<string, any>;
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

// 커스텀 엣지 타입
export type ProcessEdge = Edge<ProcessEdgeData, 'processEdge'>;

// 전체 노드 타입 (내장 노드 + 커스텀 노드)
export type AppNodeType = BuiltInNode | ProcessNode;

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
