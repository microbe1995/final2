'use client';

import { useCallback } from 'react';
import { Node, Edge } from '@xyflow/react';
import { apiMethods } from '@/api/apiClient';
import { transformFlowToCanvas, transformCanvasToFlow } from '@/types/transformers';
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
  // 📋 Canvas 목록 조회
  // ============================================================================
  
  const loadSavedCanvases = useCallback(async (): Promise<CanvasListItem[]> => {
    try {
      const response = await apiMethods.get<CanvasListItem[]>('/api/v1/cal-boundary/canvas');
      return response || [];
    } catch (error) {
      console.error('❌ Canvas 목록 조회 실패:', error);
      return [];
    }
  }, []);

  // ============================================================================
  // 💾 Canvas 백엔드 저장
  // ============================================================================
  
  const saveToBackend = useCallback(async (
    nodes: AppNodeType[],
    edges: AppEdgeType[],
    name?: string
  ): Promise<boolean> => {
    try {
      // 간단한 유효성 검사
      if (!nodes || nodes.length === 0) {
        throw new Error('최소 1개 이상의 노드가 필요합니다.');
      }

      // React Flow 데이터를 Canvas 형식으로 변환
      const canvasData = transformFlowToCanvas(nodes, edges, name);
      
      // 백엔드에 저장
      await apiMethods.post('/api/v1/cal-boundary/canvas', canvasData);
      
      console.log('✅ 백엔드 저장 완료');
      return true;
    } catch (error) {
      console.error('❌ 백엔드 저장 실패:', error);
      throw error;
    }
  }, []);

  // ============================================================================
  // 📥 Canvas 백엔드에서 로드
  // ============================================================================
  
  const loadFromBackend = useCallback(async (
    canvasId?: string
  ): Promise<{ nodes: AppNodeType[]; edges: AppEdgeType[]; metadata?: any } | null> => {
    try {
      if (canvasId) {
        // 특정 Canvas 로드
        const canvas = await apiMethods.get(`/api/v1/cal-boundary/canvas/${canvasId}`);
        return transformCanvasToFlow(canvas);
      } else {
        // 최신 Canvas 로드
        const canvases = await apiMethods.get<CanvasListItem[]>('/api/v1/cal-boundary/canvas');
        
        if (canvases && canvases.length > 0) {
          const latestCanvas = canvases[0];
          const canvas = await apiMethods.get(`/api/v1/cal-boundary/canvas/${latestCanvas.id}`);
          return transformCanvasToFlow(canvas);
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
      const response = await apiMethods.get<ServiceHealthStatus>('/api/v1/gateway/services/health');
      return response;
    } catch (error) {
      console.error('❌ 서비스 상태 확인 실패:', error);
      return null;
    }
  }, []);

  // ============================================================================
  // 🗑️ Canvas 삭제
  // ============================================================================
  
  const deleteCanvas = useCallback(async (canvasId: string): Promise<boolean> => {
    try {
      await apiMethods.delete(`/api/v1/cal-boundary/canvas/${canvasId}`);
      console.log('✅ Canvas 삭제 완료');
      return true;
    } catch (error) {
      console.error('❌ Canvas 삭제 실패:', error);
      throw error;
    }
  }, []);

  // ============================================================================
  // ✏️ Canvas 업데이트
  // ============================================================================
  
  const updateCanvas = useCallback(async (
    canvasId: string,
    nodes: AppNodeType[],
    edges: AppEdgeType[],
    name?: string
  ): Promise<boolean> => {
    try {
      // 간단한 유효성 검사
      if (!nodes || nodes.length === 0) {
        throw new Error('최소 1개 이상의 노드가 필요합니다.');
      }

      // React Flow 데이터를 Canvas 형식으로 변환
      const canvasData = transformFlowToCanvas(nodes, edges, name);
      
      // 백엔드에 업데이트
      await apiMethods.put(`/api/v1/cal-boundary/canvas/${canvasId}`, canvasData);
      
      console.log('✅ Canvas 업데이트 완료');
      return true;
    } catch (error) {
      console.error('❌ Canvas 업데이트 실패:', error);
      throw error;
    }
  }, []);

  return {
    loadSavedCanvases,
    saveToBackend,
    loadFromBackend,
    checkServiceStatus,
    deleteCanvas,
    updateCanvas,
  };
};
