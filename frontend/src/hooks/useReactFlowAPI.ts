'use client';

import { useCallback } from 'react';
import type { Node, Edge } from '@xyflow/react';

// ============================================================================
// 🎯 React Flow 백엔드 연동 훅 (Mock 버전)
// ============================================================================

export const useReactFlowAPI = () => {
  // ============================================================================
  // 🎯 플로우 관리 API (Mock 구현)
  // ============================================================================

  const createFlow = useCallback(async (data: any): Promise<any | null> => {
    return {
      id: `flow-${Date.now()}`,
      name: data.name,
      description: data.description,
      viewport: { x: 0, y: 0, zoom: 1 },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }, []);

  const getFlowState = useCallback(
    async (flowId: string): Promise<any | null> => {
      return {
        flow: {
          id: flowId,
          name: '기존 플로우',
          description: '로드된 플로우',
          viewport: { x: 0, y: 0, zoom: 1 },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        nodes: [],
        edges: [],
      };
    },
    []
  );

  const updateFlow = useCallback(
    async (flowId: string, data: any): Promise<any | null> => {
      return {
        id: flowId,
        ...data,
        updated_at: new Date().toISOString(),
      };
    },
    []
  );

  const deleteFlow = useCallback(async (flowId: string): Promise<boolean> => {
    return true;
  }, []);

  // ============================================================================
  // 🎯 노드 관리 API (Mock 구현)
  // ============================================================================

  const createNode = useCallback(async (data: any): Promise<any | null> => {
    return {
      id: data.node_id,
      flow_id: data.flow_id,
      node_id: data.node_id,
      type: data.type,
      position: data.position,
      data: data.data,
      width: data.width,
      height: data.height,
      style: data.style,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }, []);

  const updateNode = useCallback(
    async (nodeId: string, data: any): Promise<any | null> => {
      return {
        id: nodeId,
        ...data,
        updated_at: new Date().toISOString(),
      };
    },
    []
  );

  const deleteNode = useCallback(async (nodeId: string): Promise<boolean> => {
    return true;
  }, []);

  // ============================================================================
  // 🎯 엣지 관리 API (Mock 구현)
  // ============================================================================

  const createEdge = useCallback(async (data: any): Promise<any | null> => {
    return {
      id: data.edge_id,
      flow_id: data.flow_id,
      edge_id: data.edge_id,
      source: data.source,
      target: data.target,
      source_handle: data.source_handle,
      target_handle: data.target_handle,
      type: data.type,
      data: data.data,
      style: data.style,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }, []);

  const updateEdge = useCallback(
    async (edgeId: string, data: any): Promise<any | null> => {
      return {
        id: edgeId,
        ...data,
        updated_at: new Date().toISOString(),
      };
    },
    []
  );

  const deleteEdge = useCallback(async (edgeId: string): Promise<boolean> => {
    return true;
  }, []);

  // ============================================================================
  // 🎯 뷰포트 관리 API (Mock 구현)
  // ============================================================================

  const updateViewport = useCallback(async (data: any): Promise<boolean> => {
    return true;
  }, []);

  // ============================================================================
  // 🎯 배치 작업 API (Mock 구현)
  // ============================================================================

  const saveFlowState = useCallback(
    async (
      flowId: string,
      nodes: Node[],
      edges: Edge[],
      viewport: { x: number; y: number; zoom: number }
    ): Promise<boolean> => {
      try {
        // 플로우가 없으면 생성
        if (!flowId) {
          const flowData = await createFlow({
            name: '새 플로우',
            description: '새로 생성된 플로우',
          });
          if (!flowData) return false;
          flowId = flowData.id;
        }

        // 노드들 저장
        for (const node of nodes) {
          await createNode({
            flow_id: flowId,
            node_id: node.id,
            type: node.type,
            position: node.position,
            data: node.data,
            width: node.width,
            height: node.height,
            style: node.style,
          });
        }

        // 엣지들 저장
        for (const edge of edges) {
          await createEdge({
            flow_id: flowId,
            edge_id: edge.id,
            source: edge.source,
            target: edge.target,
            source_handle: edge.sourceHandle,
            target_handle: edge.targetHandle,
            type: edge.type,
            data: edge.data,
            style: edge.style,
          });
        }

        // 뷰포트 저장
        await updateViewport({
          flow_id: flowId,
          x: viewport.x,
          y: viewport.y,
          zoom: viewport.zoom,
        });

        return true;
      } catch (error) {
        return false;
      }
    },
    [createFlow, createNode, createEdge, updateViewport]
  );

  // ============================================================================
  // 🎯 데이터 변환 유틸리티
  // ============================================================================

  const convertBackendToFrontend = useCallback((backendState: any) => {
    const nodes: Node[] = backendState.nodes.map((nodeData: any) => ({
      id: nodeData.node_id,
      type: nodeData.type,
      position: nodeData.position,
      data: nodeData.data,
      width: nodeData.width,
      height: nodeData.height,
      style: nodeData.style,
    }));

    const edges: Edge[] = backendState.edges.map((edgeData: any) => ({
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
