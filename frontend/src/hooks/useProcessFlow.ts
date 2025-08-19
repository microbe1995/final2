'use client';

import { useState, useCallback } from 'react';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

// ============================================================================
// 🎯 Pure React Flow 상태 관리 훅 (백엔드 의존성 제거)
// ============================================================================

export const useProcessFlowDomain = () => {
  // ============================================================================
  // 🎨 React Flow 상태만 관리
  // ============================================================================
  
  const [nodes, setNodes] = useState<AppNodeType[]>([]);
  const [edges, setEdges] = useState<AppEdgeType[]>([]);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<AppNodeType[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<AppEdgeType[]>([]);

  // ============================================================================
  // 🔄 Flow 변경 처리 (순수 클라이언트 사이드)
  // ============================================================================
  
  const handleFlowChange = useCallback((newNodes: AppNodeType[], newEdges: AppEdgeType[]) => {
    console.log('🔄 Pure React Flow - handleFlowChange 호출됨:', { newNodes, newEdges });
    setNodes(newNodes);
    setEdges(newEdges);
    
    // 선택된 요소들 업데이트
    setSelectedNodes(newNodes.filter(node => node.selected));
    setSelectedEdges(newEdges.filter(edge => edge.selected));
    console.log('✅ Pure React Flow - 상태 업데이트 완료');
  }, []);

  // ============================================================================
  // 🔒 읽기 전용 모드 토글
  // ============================================================================
  
  const toggleReadOnly = useCallback(() => {
    setIsReadOnly(prev => !prev);
  }, []);

  // ============================================================================
  // 📤 Flow 내보내기 (JSON 다운로드)
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
        createdWith: 'React Flow'
      }
    };
    
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `react-flow-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }, [nodes, edges]);

  // ============================================================================
  // 📥 Flow 가져오기 (JSON 파일 업로드)
  // ============================================================================
  
  const importFlow = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const flowData = JSON.parse(event.target?.result as string);
          
          if (flowData.nodes && flowData.edges) {
            setNodes(flowData.nodes);
            setEdges(flowData.edges);
            setSelectedNodes([]);
            setSelectedEdges([]);
            console.log('✅ Flow 가져오기 완료:', flowData);
          } else {
            alert('올바르지 않은 React Flow 파일 형식입니다.');
          }
        } catch (error) {
          console.error('Flow 가져오기 실패:', error);
          alert('파일을 읽는 중 오류가 발생했습니다.');
        }
      };
      reader.readAsText(file);
    };
    
    input.click();
  }, []);

  // ============================================================================
  // 🧹 Flow 초기화
  // ============================================================================
  
  const clearFlow = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNodes([]);
    setSelectedEdges([]);
  }, []);

  // ============================================================================
  // 📋 로컬 스토리지 저장/로드
  // ============================================================================
  
  const saveToLocalStorage = useCallback((name?: string) => {
    const flowData = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
      name: name || `Flow ${Date.now()}`
    };
    
    const key = `react-flow-${Date.now()}`;
    localStorage.setItem(key, JSON.stringify(flowData));
    
    console.log('✅ 로컬 스토리지에 저장 완료:', key);
    return key;
  }, [nodes, edges]);

  const loadFromLocalStorage = useCallback((key: string) => {
    try {
      const flowData = localStorage.getItem(key);
      if (flowData) {
        const parsed = JSON.parse(flowData);
        setNodes(parsed.nodes || []);
        setEdges(parsed.edges || []);
        setSelectedNodes([]);
        setSelectedEdges([]);
        console.log('✅ 로컬 스토리지에서 로드 완료:', key);
        return true;
      }
      return false;
    } catch (error) {
      console.error('로컬 스토리지 로드 실패:', error);
      return false;
    }
  }, []);

  const getSavedFlows = useCallback(() => {
    const savedFlows: { key: string; name: string; timestamp: string; nodeCount: number; edgeCount: number }[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('react-flow-')) {
        try {
          const flowData = JSON.parse(localStorage.getItem(key) || '{}');
          savedFlows.push({
            key,
            name: flowData.name || key,
            timestamp: flowData.timestamp || 'Unknown',
            nodeCount: flowData.nodes?.length || 0,
            edgeCount: flowData.edges?.length || 0
          });
        } catch (error) {
          console.warn('저장된 Flow 파싱 실패:', key);
        }
      }
    }
    
    return savedFlows.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, []);

  return {
    // React Flow 상태
    nodes,
    edges,
    isReadOnly,
    selectedNodes,
    selectedEdges,
    
    // 상태 업데이트
    setNodes,
    setEdges,
    handleFlowChange,
    toggleReadOnly,
    
    // 파일 관리
    exportFlow,
    importFlow,
    clearFlow,
    
    // 로컬 스토리지 관리
    saveToLocalStorage,
    loadFromLocalStorage,
    getSavedFlows,
  };
};