'use client';

import { useState, useCallback, useEffect } from 'react';
import { useProcessFlowService } from './useProcessFlowAPI';
import { CanvasListItem, ServiceHealthStatus } from './useProcessFlowAPI';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

// ============================================================================
// 🎯 MSA 기반 React Flow 상태 관리 훅
// ============================================================================

export const useProcessFlowDomain = () => {
  // ============================================================================
  // 🎨 React Flow 상태
  // ============================================================================
  
  const [nodes, setNodes] = useState<AppNodeType[]>([]);
  const [edges, setEdges] = useState<AppEdgeType[]>([]);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<AppNodeType[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<AppEdgeType[]>([]);

  // ============================================================================
  // 🔗 MSA 백엔드 관련 상태
  // ============================================================================
  
  const [savedCanvases, setSavedCanvases] = useState<CanvasListItem[]>([]);
  const [isLoadingCanvases, setIsLoadingCanvases] = useState(false);
  const [serviceStatus, setServiceStatus] = useState<ServiceHealthStatus | null>(null);
  const [currentCanvasId, setCurrentCanvasId] = useState<string | null>(null);

  // ============================================================================
  // 🚀 MSA API 훅 사용
  // ============================================================================
  
  const {
    loadSavedFlows,
    saveReactFlowToBackend,
    loadReactFlowFromBackend,
    checkServiceStatus,
    syncReactFlowChanges,
    deleteFlow,
  } = useProcessFlowService();

  // ============================================================================
  // 🔄 React Flow 변경 처리 (MSA 동기화 포함)
  // ============================================================================
  
  const handleFlowChange = useCallback(async (newNodes: AppNodeType[], newEdges: AppEdgeType[]) => {
    console.log('🔄 MSA React Flow - handleFlowChange 호출됨:', { newNodes, newEdges });
    setNodes(newNodes);
    setEdges(newEdges);
    
    // 선택된 요소들 업데이트
    setSelectedNodes(newNodes.filter(node => node.selected));
    setSelectedEdges(newEdges.filter(edge => edge.selected));
    
    // MSA: 백엔드에 실시간 동기화 (currentCanvasId가 있을 때만)
    if (currentCanvasId && !isReadOnly) {
      try {
        await syncReactFlowChanges(currentCanvasId, newNodes, newEdges);
      } catch (error) {
        console.warn('⚠️ MSA 실시간 동기화 실패 (오프라인 모드로 계속):', error);
      }
    }
    
    console.log('✅ MSA React Flow - 상태 업데이트 완료');
  }, [currentCanvasId, isReadOnly, syncReactFlowChanges]);

  // ============================================================================
  // 🔒 읽기 전용 모드 토글
  // ============================================================================
  
  const toggleReadOnly = useCallback(() => {
    setIsReadOnly(prev => !prev);
  }, []);

  // ============================================================================
  // 📤 React Flow 내보내기 (로컬 + MSA 백엔드)
  // ============================================================================
  
  const exportFlow = useCallback(() => {
    const flowData = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      metadata: {
        nodeCount: nodes.length,
        edgeCount: edges.length,
        createdWith: 'React Flow MSA',
        canvasId: currentCanvasId
      }
    };
    
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `react-flow-msa-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }, [nodes, edges, currentCanvasId]);

  // ============================================================================
  // 📥 React Flow 가져오기 (로컬 파일)
  // ============================================================================
  
  const importFlow = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = async (event) => {
        try {
          const flowData = JSON.parse(event.target?.result as string);
          
          if (flowData.nodes && flowData.edges) {
            setNodes(flowData.nodes);
            setEdges(flowData.edges);
            setSelectedNodes([]);
            setSelectedEdges([]);
            setCurrentCanvasId(null); // 새로 가져온 데이터는 백엔드 ID 없음
            console.log('✅ React Flow 가져오기 완료:', flowData);
          } else {
            alert('올바르지 않은 React Flow 파일 형식입니다.');
          }
        } catch (error) {
          console.error('React Flow 가져오기 실패:', error);
          alert('파일을 읽는 중 오류가 발생했습니다.');
        }
      };
      reader.readAsText(file);
    };
    
    input.click();
  }, []);

  // ============================================================================
  // 📋 MSA 백엔드에서 저장된 Canvas 목록 로드
  // ============================================================================
  
  const loadSavedCanvases = useCallback(async () => {
    try {
      setIsLoadingCanvases(true);
      const flows = await loadSavedFlows();
      setSavedCanvases(flows);
    } catch (error) {
      console.error('MSA Flow 목록 로드 실패:', error);
      setSavedCanvases([]);
    } finally {
      setIsLoadingCanvases(false);
    }
  }, [loadSavedFlows]);

  // ============================================================================
  // 💾 MSA 백엔드에 저장
  // ============================================================================
  
  const saveToBackend = useCallback(async (canvasName?: string) => {
    try {
      const result = await saveReactFlowToBackend(nodes, edges, canvasName);
      
      if (result.success) {
        setCurrentCanvasId(result.flowId || null);
        // 저장된 Canvas 목록 새로고침
        await loadSavedCanvases();
        return true;
      }
      
      throw new Error('저장 실패');
    } catch (error) {
      console.error('MSA 백엔드 저장 실패:', error);
      throw error;
    }
  }, [nodes, edges, saveReactFlowToBackend, loadSavedCanvases]);

  // ============================================================================
  // 📥 MSA 백엔드에서 로드
  // ============================================================================
  
  const loadFromBackend = useCallback(async (canvasId?: string) => {
    try {
      const flowData = await loadReactFlowFromBackend(canvasId);
      
      if (flowData) {
        setNodes(flowData.nodes);
        setEdges(flowData.edges);
        setCurrentCanvasId(canvasId || flowData.metadata?.flow?.id || null);
        console.log('MSA 백엔드에서 React Flow 로드 완료');
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('MSA 백엔드 로드 실패:', error);
      throw error;
    }
  }, [loadReactFlowFromBackend]);

  // ============================================================================
  // 🔍 MSA 서비스 상태 확인
  // ============================================================================
  
  const checkMSAServiceStatus = useCallback(async () => {
    try {
      const status = await checkServiceStatus();
      setServiceStatus(status);
      return status;
    } catch (error) {
      console.error('MSA 서비스 상태 확인 실패:', error);
      setServiceStatus(null);
      return null;
    }
  }, [checkServiceStatus]);

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
  // 🗑️ MSA 백엔드에서 Flow 삭제
  // ============================================================================
  
  const deleteCanvasFromBackend = useCallback(async (canvasId: string) => {
    try {
      const success = await deleteFlow(canvasId);
      if (success) {
        // 현재 로드된 캔버스가 삭제된 경우 초기화
        if (currentCanvasId === canvasId) {
          clearFlow();
        }
        // 목록 새로고침
        await loadSavedCanvases();
      }
      return success;
    } catch (error) {
      console.error('MSA Flow 삭제 실패:', error);
      return false;
    }
  }, [deleteFlow, currentCanvasId, clearFlow, loadSavedCanvases]);

  // ============================================================================
  // 🔄 초기화 - 컴포넌트 마운트 시 MSA 서비스 연결
  // ============================================================================
  
  useEffect(() => {
    loadSavedCanvases();
    checkMSAServiceStatus();
  }, [loadSavedCanvases, checkMSAServiceStatus]);

  return {
    // React Flow 상태
    nodes,
    edges,
    isReadOnly,
    selectedNodes,
    selectedEdges,
    
    // MSA 백엔드 상태
    savedCanvases,
    isLoadingCanvases,
    serviceStatus,
    currentCanvasId,
    
    // 액션
    setNodes,
    setEdges,
    handleFlowChange,
    toggleReadOnly,
    
    // 파일 관리 (하이브리드)
    exportFlow,
    importFlow,
    clearFlow,
    
    // MSA 백엔드 관리
    loadSavedCanvases,
    saveToBackend,
    loadFromBackend,
    checkMSAServiceStatus,
    deleteCanvasFromBackend,
  };
};