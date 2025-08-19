'use client';

import { useCallback } from 'react';
import { useAPI } from './useAPI';
import type { Node, Edge } from '@xyflow/react';
import type {
  FlowData,
  FlowStateResponse,
  CreateFlowRequest,
  CreateNodeRequest,
  CreateEdgeRequest,
  UpdateViewportRequest,
  NodeData,
  EdgeData,
} from '@/types/flowAPI';

// ============================================================================
// 🎯 React Flow 백엔드 연동 훅
// ============================================================================

export const useReactFlowAPI = () => {
  const api = useAPI('/api/v1/boundary');

  // ============================================================================
  // 🎯 플로우 관리 API
  // ============================================================================

  const createFlow = useCallback(async (data: CreateFlowRequest): Promise<FlowData | null> => {
    return api.post('/flow', data, {
      successMessage: '플로우가 생성되었습니다.',
      errorMessage: '플로우 생성에 실패했습니다.'
    });
  }, [api]);

  const getFlowState = useCallback(async (flowId: string): Promise<FlowStateResponse | null> => {
    return api.get(`/flow/${flowId}/state`, {
      errorMessage: '플로우 상태 조회에 실패했습니다.'
    });
  }, [api]);

  const updateFlow = useCallback(async (flowId: string, data: Partial<FlowData>): Promise<FlowData | null> => {
    return api.put(`/flow/${flowId}`, data, {
      successMessage: '플로우가 업데이트되었습니다.',
      errorMessage: '플로우 업데이트에 실패했습니다.'
    });
  }, [api]);

  const deleteFlow = useCallback(async (flowId: string): Promise<boolean> => {
    const result = await api.delete(`/flow/${flowId}`, {
      successMessage: '플로우가 삭제되었습니다.',
      errorMessage: '플로우 삭제에 실패했습니다.'
    });
    return !!result;
  }, [api]);

  // ============================================================================
  // 🎯 노드 관리 API
  // ============================================================================

  const createNode = useCallback(async (data: CreateNodeRequest): Promise<NodeData | null> => {
    return api.post('/node', data, {
      errorMessage: '노드 생성에 실패했습니다.'
    });
  }, [api]);

  const updateNode = useCallback(async (nodeId: string, data: Partial<CreateNodeRequest>): Promise<NodeData | null> => {
    return api.put(`/node/${nodeId}`, data, {
      errorMessage: '노드 업데이트에 실패했습니다.'
    });
  }, [api]);

  const deleteNode = useCallback(async (nodeId: string): Promise<boolean> => {
    const result = await api.delete(`/node/${nodeId}`, {
      errorMessage: '노드 삭제에 실패했습니다.'
    });
    return !!result;
  }, [api]);

  // ============================================================================
  // 🎯 엣지 관리 API
  // ============================================================================

  const createEdge = useCallback(async (data: CreateEdgeRequest): Promise<EdgeData | null> => {
    return api.post('/edge', data, {
      errorMessage: '엣지 생성에 실패했습니다.'
    });
  }, [api]);

  const updateEdge = useCallback(async (edgeId: string, data: Partial<CreateEdgeRequest>): Promise<EdgeData | null> => {
    return api.put(`/edge/${edgeId}`, data, {
      errorMessage: '엣지 업데이트에 실패했습니다.'
    });
  }, [api]);

  const deleteEdge = useCallback(async (edgeId: string): Promise<boolean> => {
    const result = await api.delete(`/edge/${edgeId}`, {
      errorMessage: '엣지 삭제에 실패했습니다.'
    });
    return !!result;
  }, [api]);

  // ============================================================================
  // 🎯 뷰포트 관리 API
  // ============================================================================

  const updateViewport = useCallback(async (data: UpdateViewportRequest): Promise<boolean> => {
    const result = await api.post('/viewport', data, {
      errorMessage: '뷰포트 업데이트에 실패했습니다.'
    });
    return !!result;
  }, [api]);

  // ============================================================================
  // 🎯 배치 작업 API (성능 최적화)
  // ============================================================================

  const saveFlowState = useCallback(async (
    flowId: string,
    nodes: Node[],
    edges: Edge[],
    viewport: { x: number; y: number; zoom: number }
  ): Promise<boolean> => {
    try {
      // 뷰포트 업데이트
      await updateViewport({ flow_id: flowId, viewport });

      // 기존 노드/엣지와 비교하여 변경사항만 처리 (실제로는 더 복잡한 로직 필요)
      // 여기서는 간단히 전체 상태를 저장
      const nodePromises = nodes.map(node => 
        createNode({
          flow_id: flowId,
          node_id: node.id,
          type: node.type || 'default',
          position: node.position,
          data: node.data,
          width: node.width,
          height: node.height,
          style: node.style,
        })
      );

      const edgePromises = edges.map(edge =>
        createEdge({
          flow_id: flowId,
          edge_id: edge.id,
          source: edge.source,
          target: edge.target,
          source_handle: edge.sourceHandle || undefined,
          target_handle: edge.targetHandle || undefined,
          type: edge.type,
          data: edge.data,
          style: edge.style,
        })
      );

      await Promise.all([...nodePromises, ...edgePromises]);
      return true;
    } catch (error) {
      console.error('플로우 상태 저장 실패:', error);
      return false;
    }
  }, [updateViewport, createNode, createEdge]);

  // ============================================================================
  // 🎯 데이터 변환 유틸리티
  // ============================================================================

  const convertBackendToFrontend = useCallback((backendState: FlowStateResponse) => {
    const nodes: Node[] = backendState.nodes.map(nodeData => ({
      id: nodeData.node_id,
      type: nodeData.type,
      position: nodeData.position,
      data: nodeData.data,
      width: nodeData.width,
      height: nodeData.height,
      style: nodeData.style,
    }));

    const edges: Edge[] = backendState.edges.map(edgeData => ({
      id: edgeData.edge_id,
      source: edgeData.source,
      target: edgeData.target,
      sourceHandle: edgeData.source_handle,
      targetHandle: edgeData.target_handle,
      type: edgeData.type,
      data: edgeData.data,
      style: edgeData.style,
    }));

    return {
      flowId: backendState.flow.id,
      flow: backendState.flow,
      nodes,
      edges,
      viewport: backendState.flow.viewport,
    };
  }, []);

  return {
    // 플로우 관리
    createFlow,
    getFlowState,
    updateFlow,
    deleteFlow,
    
    // 노드 관리
    createNode,
    updateNode,
    deleteNode,
    
    // 엣지 관리
    createEdge,
    updateEdge,
    deleteEdge,
    
    // 뷰포트 관리
    updateViewport,
    
    // 배치 작업
    saveFlowState,
    
    // 유틸리티
    convertBackendToFrontend,
  };
};
