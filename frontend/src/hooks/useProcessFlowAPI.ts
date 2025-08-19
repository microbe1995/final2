'use client';

import { useCallback } from 'react';
import { apiMethods } from '@/api/apiClient';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

// ============================================================================
// 🎯 Process Flow API 관련 타입 정의
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
// 🔗 Process Flow API 훅
// ============================================================================

export const useProcessFlowService = () => {
  // ============================================================================
  // 📋 플로우 목록 조회
  // ============================================================================
  
  const loadSavedFlows = useCallback(async (): Promise<CanvasListItem[]> => {
    try {
      // ReactFlow Flow API 사용
      const response = await apiMethods.get<any>('/api/v1/boundary/flow');
      
      // Flow 데이터를 Canvas 형식으로 변환
      const canvasList: CanvasListItem[] = response.flows?.map((flow: any) => ({
        id: flow.id,
        name: flow.name,
        description: flow.description || '',
        metadata: {
          createdAt: flow.created_at,
          updatedAt: flow.updated_at,
          nodeCount: 0, // TODO: 노드 개수 계산
          edgeCount: 0  // TODO: 엣지 개수 계산
        }
      })) || [];
      
      return canvasList;
    } catch (error) {
      console.error('❌ Flow 목록 조회 실패:', error);
      return [];
    }
  }, []);

  // ============================================================================
  // 💾 플로우 백엔드 저장
  // ============================================================================
  
  const saveToBackend = useCallback(async (
    nodes: AppNodeType[],
    edges: AppEdgeType[],
    name?: string
  ): Promise<boolean> => {
    try {
      // 1단계: 플로우 생성
      const flowData = {
        name: name || `Flow ${Date.now()}`,
        description: `ReactFlow 저장 - ${new Date().toISOString()}`,
        viewport: { x: 0, y: 0, zoom: 1.0 },
        settings: { panOnDrag: true, zoomOnScroll: true },
        metadata: { nodeCount: nodes.length, edgeCount: edges.length }
      };
      
      const createdFlow = await apiMethods.post('/api/v1/boundary/flow', flowData);
      console.log('✅ 플로우 생성 완료:', createdFlow.id);
      
      // 2단계: 노드들 저장
      for (const node of nodes) {
        const nodeData = {
          flow_id: createdFlow.id,
          type: node.type || 'default',
          position: node.position,
          data: {
            label: node.data?.label || 'Node',
            description: node.data?.description || '',
            color: node.data?.color || '',
            icon: node.data?.icon || '',
            metadata: node.data || {}
          },
          width: node.width,
          height: node.height,
          draggable: node.draggable !== false,
          selectable: node.selectable !== false,
          deletable: node.deletable !== false,
          style: node.style || {}
        };
        
        await apiMethods.post('/api/v1/boundary/node', nodeData);
      }
      
      console.log('✅ 백엔드 저장 완료 - 플로우:', createdFlow.id, '노드:', nodes.length, '개');
      return true;
    } catch (error) {
      console.error('❌ 백엔드 저장 실패:', error);
      throw error;
    }
  }, []);

  // ============================================================================
  // 📥 플로우 백엔드에서 로드
  // ============================================================================
  
  const loadFromBackend = useCallback(async (
    flowId?: string
  ): Promise<{ nodes: AppNodeType[]; edges: AppEdgeType[]; metadata?: any } | null> => {
    try {
      if (flowId) {
        // 특정 플로우의 전체 상태 로드
        const flowState = await apiMethods.get(`/api/v1/boundary/flow/${flowId}/state`);
        
        // ReactFlow 형식으로 변환
        const reactFlowData = {
          nodes: flowState.nodes || [],
          edges: flowState.edges || [],
          metadata: {
            flow: flowState.flow,
            nodeCount: flowState.nodes?.length || 0,
            edgeCount: flowState.edges?.length || 0
          }
        };
        
        return reactFlowData;
      } else {
        // 플로우 목록에서 첫 번째 플로우 로드
        const flowsResponse = await apiMethods.get('/api/v1/boundary/flow');
        
        if (flowsResponse.flows && flowsResponse.flows.length > 0) {
          const latestFlow = flowsResponse.flows[0];
          // 재귀 호출 대신 직접 로드
          const flowState = await apiMethods.get(`/api/v1/boundary/flow/${latestFlow.id}/state`);
          
          return {
            nodes: flowState.nodes || [],
            edges: flowState.edges || [],
            metadata: {
              flow: flowState.flow,
              nodeCount: flowState.nodes?.length || 0,
              edgeCount: flowState.edges?.length || 0
            }
          };
        }
      }
      
      return null;
    } catch (error) {
      console.error('❌ 백엔드 로드 실패:', error);
      throw error;
    }
  }, []);

  // ============================================================================
  // 🔍 서비스 상태 확인
  // ============================================================================
  
  const checkServiceStatus = useCallback(async (): Promise<ServiceHealthStatus | null> => {
    try {
      // ReactFlow Node/Flow 서비스 상태 확인
      const nodeHealth = await apiMethods.get('/api/v1/boundary/node/health');
      const flowHealth = await apiMethods.get('/api/v1/boundary/flow/health');
      
      return {
        status: nodeHealth.status === 'healthy' && flowHealth.status === 'healthy' ? 'healthy' : 'unhealthy',
        service: 'ReactFlow Backend Services',
        version: '1.0.0',
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('❌ 서비스 상태 확인 실패:', error);
      return null;
    }
  }, []);

  // ============================================================================
  // 🔄 ReactFlow 실시간 동기화 함수들
  // ============================================================================
  
  const syncNodeChanges = useCallback(async (
    flowId: string,
    nodeChanges: any[]
  ): Promise<boolean> => {
    try {
      await apiMethods.post(`/api/v1/boundary/node/batch-update`, {
        nodes: nodeChanges
      });
      console.log('✅ 노드 변경사항 동기화 완료');
      return true;
    } catch (error) {
      console.error('❌ 노드 변경사항 동기화 실패:', error);
      return false;
    }
  }, []);
  
  const syncViewportChange = useCallback(async (
    flowId: string,
    viewport: { x: number; y: number; zoom: number }
  ): Promise<boolean> => {
    try {
      await apiMethods.put(`/api/v1/boundary/flow/${flowId}/viewport`, {
        viewport
      });
      console.log('✅ 뷰포트 상태 동기화 완료');
      return true;
    } catch (error) {
      console.error('❌ 뷰포트 상태 동기화 실패:', error);
      return false;
    }
  }, []);
  
  const createNode = useCallback(async (
    flowId: string,
    nodeData: any
  ): Promise<any> => {
    try {
      const newNode = await apiMethods.post('/api/v1/boundary/node', {
        ...nodeData,
        flow_id: flowId
      });
      console.log('✅ 새 노드 생성 완료:', newNode.id);
      return newNode;
    } catch (error) {
      console.error('❌ 노드 생성 실패:', error);
      throw error;
    }
  }, []);

  // ============================================================================
  // 🗑️ Flow 삭제
  // ============================================================================
  
  const deleteFlow = useCallback(async (flowId: string): Promise<boolean> => {
    try {
      await apiMethods.delete(`/api/v1/boundary/flow/${flowId}`);
      console.log('✅ Flow 삭제 완료');
      return true;
    } catch (error) {
      console.error('❌ Flow 삭제 실패:', error);
      throw error;
    }
  }, []);

  return {
    loadSavedFlows,
    saveToBackend,
    loadFromBackend,
    checkServiceStatus,
    deleteFlow,
    // ReactFlow 실시간 동기화 함수들
    syncNodeChanges,
    syncViewportChange,
    createNode,
  };
};
