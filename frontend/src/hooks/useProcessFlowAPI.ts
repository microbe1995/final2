'use client';

import { useCallback } from 'react';
import { apiMethods } from '@/api/apiClient';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

// ============================================================================
// 🎯 MSA 기반 Process Flow API 관련 타입 정의
// ============================================================================

export interface CanvasListItem {
  id: string;
  name: string;
  description: string;
  metadata?: {
    createdAt: string;
    updatedAt: string;
    nodeCount: number;
    edgeCount: number;
  };
}

export interface ServiceHealthStatus {
  status: string;
  service: string;
  version: string;
  timestamp: number;
}

// ============================================================================
// 🔗 MSA 기반 Process Flow API 훅 (React Flow 전용)
// ============================================================================

export const useProcessFlowService = () => {
  // ============================================================================
  // 📋 플로우 목록 조회 (Boundary Service)
  // ============================================================================
  
  const loadSavedFlows = useCallback(async (): Promise<CanvasListItem[]> => {
    try {
      // MSA: Boundary Service의 Flow API 호출
      const response = await apiMethods.get<any>('/api/flow');
      
      // ReactFlow 데이터를 Canvas 형식으로 변환
      const canvasList: CanvasListItem[] = response.flows?.map((flow: any) => ({
        id: flow.id,
        name: flow.name,
        description: flow.description || '',
        metadata: {
          createdAt: flow.created_at,
          updatedAt: flow.updated_at,
          nodeCount: flow.nodes?.length || 0,
          edgeCount: flow.edges?.length || 0
        }
      })) || [];
      
      return canvasList;
    } catch (error) {
      console.error('❌ MSA Flow 목록 조회 실패:', error);
      return [];
    }
  }, []);

  // ============================================================================
  // 💾 ReactFlow 데이터를 MSA 백엔드에 저장
  // ============================================================================
  
  const saveReactFlowToBackend = useCallback(async (
    nodes: AppNodeType[],
    edges: AppEdgeType[],
    name?: string
  ): Promise<{ success: boolean; flowId?: string }> => {
    try {
      // 1단계: MSA Boundary Service에 Flow 생성
      const flowData = {
        name: name || `ReactFlow ${Date.now()}`,
        description: `React Flow 저장 - ${new Date().toISOString()}`,
        reactflow_data: {
          nodes: nodes.map(node => ({
            id: node.id,
            type: node.type,
            position: node.position,
            data: node.data,
            style: node.style,
            draggable: node.draggable,
            selectable: node.selectable,
            deletable: node.deletable
          })),
          edges: edges.map(edge => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type,
            data: edge.data,
            style: edge.style
          }))
        },
        viewport: { x: 0, y: 0, zoom: 1.0 },
        metadata: { 
          nodeCount: nodes.length, 
          edgeCount: edges.length,
          savedWith: 'React Flow MSA'
        }
      };
      
      const createdFlow = await apiMethods.post('/api/flow', flowData);
      console.log('✅ MSA ReactFlow 저장 완료:', createdFlow.id);
      
      return { success: true, flowId: createdFlow.id };
    } catch (error) {
      console.error('❌ MSA ReactFlow 저장 실패:', error);
      return { success: false };
    }
  }, []);

  // ============================================================================
  // 📥 MSA 백엔드에서 ReactFlow 데이터 로드
  // ============================================================================
  
  const loadReactFlowFromBackend = useCallback(async (
    flowId?: string
  ): Promise<{ nodes: AppNodeType[]; edges: AppEdgeType[]; metadata?: any } | null> => {
    try {
      let targetFlowId = flowId;
      
      if (!targetFlowId) {
        // 플로우 목록에서 최신 플로우 찾기
        const flowsResponse = await apiMethods.get('/api/flow');
        if (flowsResponse.flows && flowsResponse.flows.length > 0) {
          targetFlowId = flowsResponse.flows[0].id;
        } else {
          return null;
        }
      }
      
      // MSA: 특정 플로우의 ReactFlow 데이터 로드
      const flowData = await apiMethods.get(`/api/flow/${targetFlowId}`);
      
      if (flowData.reactflow_data) {
        return {
          nodes: flowData.reactflow_data.nodes || [],
          edges: flowData.reactflow_data.edges || [],
          metadata: {
            flow: flowData,
            nodeCount: flowData.reactflow_data.nodes?.length || 0,
            edgeCount: flowData.reactflow_data.edges?.length || 0
          }
        };
      }
      
      return null;
    } catch (error) {
      console.error('❌ MSA ReactFlow 로드 실패:', error);
      return null;
    }
  }, []);

  // ============================================================================
  // 🔍 MSA 서비스 상태 확인
  // ============================================================================
  
  const checkServiceStatus = useCallback(async (): Promise<ServiceHealthStatus | null> => {
    try {
      // MSA: 각 서비스의 헬스체크
      const boundaryHealth = await apiMethods.get('/health');
      
      return {
        status: boundaryHealth.status === 'healthy' ? 'healthy' : 'unhealthy',
        service: 'MSA Boundary Service (ReactFlow)',
        version: boundaryHealth.version || '1.0.0',
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ MSA 서비스 상태 확인 실패:', error);
      return {
        status: 'unhealthy',
        service: 'MSA Services',
        version: 'unknown',
        timestamp: Date.now()
      };
    }
  }, []);

  // ============================================================================
  // 🔄 ReactFlow 실시간 동기화 (MSA 방식)
  // ============================================================================
  
  const syncReactFlowChanges = useCallback(async (
    flowId: string,
    nodes: AppNodeType[],
    edges: AppEdgeType[]
  ): Promise<boolean> => {
    try {
      // MSA: Boundary Service로 ReactFlow 상태 동기화
      await apiMethods.put(`/api/flow/${flowId}/reactflow`, {
        nodes,
        edges,
        timestamp: Date.now()
      });
      
      console.log('✅ MSA ReactFlow 동기화 완료');
      return true;
    } catch (error) {
      console.error('❌ MSA ReactFlow 동기화 실패:', error);
      return false;
    }
  }, []);
  
  // ============================================================================
  // 🗑️ MSA Flow 삭제
  // ============================================================================
  
  const deleteFlow = useCallback(async (flowId: string): Promise<boolean> => {
    try {
      await apiMethods.delete(`/api/flow/${flowId}`);
      console.log('✅ MSA Flow 삭제 완료');
      return true;
    } catch (error) {
      console.error('❌ MSA Flow 삭제 실패:', error);
      return false;
    }
  }, []);

  return {
    // MSA 기반 ReactFlow API
    loadSavedFlows,
    saveReactFlowToBackend,
    loadReactFlowFromBackend,
    checkServiceStatus,
    deleteFlow,
    syncReactFlowChanges,
  };
};
