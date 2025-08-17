'use client';

import { useState, useCallback, useEffect } from 'react';
import { useProcessFlowAPI } from './useProcessFlowAPI';
import { CanvasListItem, ServiceHealthStatus } from './useProcessFlowAPI';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

// ============================================================================
// 🎯 Process Flow 상태 관리 훅
// ============================================================================

export const useProcessFlow = () => {
  // ============================================================================
  // 🎨 React Flow 상태
  // ============================================================================
  
  const [nodes, setNodes] = useState<AppNodeType[]>([]);
  const [edges, setEdges] = useState<AppEdgeType[]>([]);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<AppNodeType[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<AppEdgeType[]>([]);

  // ============================================================================
  // 🔗 백엔드 관련 상태
  // ============================================================================
  
  const [savedCanvases, setSavedCanvases] = useState<CanvasListItem[]>([]);
  const [isLoadingCanvases, setIsLoadingCanvases] = useState(false);
  const [serviceStatus, setServiceStatus] = useState<ServiceHealthStatus | null>(null);
  const [currentCanvasId, setCurrentCanvasId] = useState<string | null>(null);

  // ============================================================================
  // 🚀 API 훅 사용
  // ============================================================================
  
  const {
    loadSavedCanvases: loadCanvasesAPI,
    saveToBackend: saveToBackendAPI,
    loadFromBackend: loadFromBackendAPI,
    checkServiceStatus: checkServiceStatusAPI,
  } = useProcessFlowAPI();

  // ============================================================================
  // 🔄 Flow 변경 처리
  // ============================================================================
  
  const handleFlowChange = useCallback((newNodes: AppNodeType[], newEdges: AppEdgeType[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    
    // 선택된 요소들 업데이트
    setSelectedNodes(newNodes.filter(node => node.selected));
    setSelectedEdges(newEdges.filter(edge => edge.selected));
  }, []);

  // ============================================================================
  // 🔒 읽기 전용 모드 토글
  // ============================================================================
  
  const toggleReadOnly = useCallback(() => {
    setIsReadOnly(prev => !prev);
  }, []);

  // ============================================================================
  // 📤 Flow 내보내기
  // ============================================================================
  
  const exportFlow = useCallback(() => {
    const flowData = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
    };
    
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `process-flow-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }, [nodes, edges]);

  // ============================================================================
  // 📋 저장된 Canvas 목록 로드
  // ============================================================================
  
  const loadSavedCanvases = useCallback(async () => {
    try {
      setIsLoadingCanvases(true);
      const canvases = await loadCanvasesAPI();
      setSavedCanvases(canvases);
    } catch (error) {
      console.error('Canvas 목록 로드 실패:', error);
      setSavedCanvases([]);
    } finally {
      setIsLoadingCanvases(false);
    }
  }, [loadCanvasesAPI]);

  // ============================================================================
  // 💾 백엔드에 저장
  // ============================================================================
  
  const saveToBackend = useCallback(async (canvasName?: string) => {
    try {
      await saveToBackendAPI(nodes, edges, canvasName);
      
      // 저장된 Canvas 목록 새로고침
      await loadSavedCanvases();
      
      return true;
    } catch (error) {
      console.error('백엔드 저장 실패:', error);
      throw error;
    }
  }, [nodes, edges, saveToBackendAPI, loadSavedCanvases]);

  // ============================================================================
  // 📥 백엔드에서 로드
  // ============================================================================
  
  const loadFromBackend = useCallback(async (canvasId?: string) => {
    try {
      const flowData = await loadFromBackendAPI(canvasId);
      
      if (flowData) {
        setNodes(flowData.nodes);
        setEdges(flowData.edges);
        setCurrentCanvasId(canvasId || null);
        console.log('백엔드에서 공정도 로드 완료');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('백엔드 로드 실패:', error);
      throw error;
    }
  }, [loadFromBackendAPI]);

  // ============================================================================
  // 🔍 서비스 상태 확인
  // ============================================================================
  
  const checkServiceStatus = useCallback(async () => {
    try {
      const status = await checkServiceStatusAPI();
      setServiceStatus(status);
      return status;
    } catch (error) {
      console.error('서비스 상태 확인 실패:', error);
      setServiceStatus(null);
      return null;
    }
  }, [checkServiceStatusAPI]);

  // ============================================================================
  // 🧹 Flow 초기화
  // ============================================================================
  
  const clearFlow = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNodes([]);
    setSelectedEdges([]);
    setCurrentCanvasId(null);
  }, []);

  // ============================================================================
  // 🔄 초기화 - 컴포넌트 마운트 시 실행
  // ============================================================================
  
  useEffect(() => {
    loadSavedCanvases();
    checkServiceStatus();
  }, [loadSavedCanvases, checkServiceStatus]);

  return {
    // React Flow 상태
    nodes,
    edges,
    isReadOnly,
    selectedNodes,
    selectedEdges,
    
    // 백엔드 상태
    savedCanvases,
    isLoadingCanvases,
    serviceStatus,
    currentCanvasId,
    
    // 액션
    setNodes,
    setEdges,
    handleFlowChange,
    toggleReadOnly,
    exportFlow,
    loadSavedCanvases,
    saveToBackend,
    loadFromBackend,
    checkServiceStatus,
    clearFlow,
  };
};
