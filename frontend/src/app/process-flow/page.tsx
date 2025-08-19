'use client';

import React, { useState, useCallback } from 'react';
import ProcessControlHeader from '@/organisms/ProcessControlHeader';
import ProcessInfoSidebar from '@/organisms/ProcessInfoSidebar';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import { useProcessFlowDomain } from '@/hooks/useProcessFlow';
import { addEdge } from '@xyflow/react';
import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge, GroupNodeData } from '@/types/reactFlow';

// ============================================================================
// 🎯 MSA 기반 React Flow Process Flow 페이지
// ============================================================================

export default function ProcessFlowPage() {
  // ============================================================================
  // 🎯 MSA 기반 React Flow 상태 관리
  // ============================================================================
  
  const {
    nodes,
    edges,
    isReadOnly,
    selectedNodes,
    selectedEdges,
    savedCanvases,
    isLoadingCanvases,
    serviceStatus,
    currentCanvasId,
    handleFlowChange,
    toggleReadOnly,
    exportFlow,
    importFlow,
    saveToBackend,
    loadFromBackend,
    clearFlow,
    deleteCanvasFromBackend,
  } = useProcessFlowDomain();

  // Sub Flow 관련 상태
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [edgeZIndex, setEdgeZIndex] = useState<number>(1);

  // ============================================================================
  // 🎨 React Flow 노드/엣지 생성 함수들
  // ============================================================================
  
  const addProcessNode = () => {
    const newNode: ProcessNode = {
      id: `node-${Date.now()}`,
      type: 'processNode',
      position: { 
        x: Math.random() * 400 + 100, 
        y: Math.random() * 300 + 100 
      },
      data: {
        label: '새 공정 단계',
        processType: 'manufacturing',
        description: '공정 단계 설명을 입력하세요',
        parameters: {},
      },
    };
    handleFlowChange([...nodes, newNode], edges);
  };

  // Sub Flow: 그룹 노드 추가
  const addGroupNode = () => {
    const newGroupNode: AppNodeType = {
      id: `group-${Date.now()}`,
      type: 'groupNode',
      position: { 
        x: Math.random() * 400 + 100, 
        y: Math.random() * 300 + 100 
      },
      data: {
        label: '새 공정 그룹',
        description: '공정 그룹 설명을 입력하세요',
        groupType: 'subprocess',
        childCount: 0,
        isExpanded: true,
        style: { width: 300, height: 200 }
      } as GroupNodeData,
      style: { width: 300, height: 200 }
    };
    handleFlowChange([...nodes, newGroupNode], edges);
  };

  const addProcessEdge = () => {
    if (nodes.length < 2) {
      alert('엣지를 추가하려면 최소 2개의 노드가 필요합니다.');
      return;
    }
    const newEdge: ProcessEdge = {
      id: `edge-${Date.now()}`,
      source: nodes[0].id,
      target: nodes[1].id,
      type: 'processEdge',
      data: { label: '공정 흐름', processType: 'standard' },
    };
    handleFlowChange(nodes, addEdge(newEdge, edges));
  };

  const deleteSelectedElements = () => {
    const selectedNodesList = nodes.filter((node) => node.selected);
    const selectedEdgesList = edges.filter((edge) => edge.selected);
    
    if (selectedNodesList.length > 0 || selectedEdgesList.length > 0) {
      const newNodes = nodes.filter((node) => !node.selected);
      const newEdges = edges.filter((edge) => !edge.selected);
      handleFlowChange(newNodes, newEdges);
    } else {
      alert('삭제할 요소를 선택해주세요.');
    }
  };

  // Sub Flow: 그룹 확장/축소 토글
  const toggleGroupExpansion = useCallback((groupId: string) => {
    setExpandedGroups(prev => {
      const newSet = new Set(prev);
      if (newSet.has(groupId)) {
        newSet.delete(groupId);
      } else {
        newSet.add(groupId);
      }
      return newSet;
    });
  }, []);

  // Sub Flow: Edge Z-Index 조정
  const handleEdgeZIndexChange = (zIndex: number) => {
    setEdgeZIndex(zIndex);
  };

  // ============================================================================
  // 🚀 MSA 백엔드 이벤트 핸들러
  // ============================================================================
  
  const handleSaveToBackend = async () => {
    try {
      const name = prompt('저장할 이름을 입력하세요:', `Flow ${new Date().toLocaleDateString()}`);
      if (name) {
        await saveToBackend(name);
        alert('MSA 백엔드에 성공적으로 저장되었습니다!');
      }
    } catch (error) {
      alert('MSA 백엔드 저장에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleLoadFromBackend = async (canvasId?: string) => {
    try {
      const success = await loadFromBackend(canvasId);
      if (success) {
        alert('MSA 백엔드에서 성공적으로 불러왔습니다!');
      } else {
        alert('저장된 공정도가 없습니다. 새로 만들어보세요!');
      }
    } catch (error) {
      alert('MSA 백엔드 로드에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleDeleteCanvas = async (canvasId: string) => {
    if (confirm('정말로 이 공정도를 삭제하시겠습니까?')) {
      try {
        const success = await deleteCanvasFromBackend(canvasId);
        if (success) {
          alert('공정도가 삭제되었습니다.');
        } else {
          alert('삭제에 실패했습니다.');
        }
      } catch (error) {
        alert('삭제 중 오류가 발생했습니다.');
      }
    }
  };

  const handleClearFlow = () => {
    if (confirm('현재 공정도를 모두 지우시겠습니까?')) {
      clearFlow();
    }
  };

  // ============================================================================
  // 🎨 렌더링 - MSA 기반 UI
  // ============================================================================

  return (
    <div className="min-h-screen bg-[#0b0c0f]">
      {/* MSA 연결 상태가 포함된 헤더 */}
              <ProcessControlHeader
          serviceStatus={serviceStatus}
          isReadOnly={isReadOnly}
          onToggleReadOnly={toggleReadOnly}
          onExport={exportFlow}
          onImport={importFlow}
          onSaveToBackend={handleSaveToBackend}
          onLoadFromBackend={handleLoadFromBackend}
          onClearFlow={handleClearFlow}
          savedCanvases={savedCanvases}
          isLoadingCanvases={isLoadingCanvases}
          currentCanvasId={currentCanvasId}
          nodeCount={nodes.length}
          edgeCount={edges.length}
          // Sub Flow 기능 추가
          onAddGroupNode={addGroupNode}
          onToggleGroupExpansion={toggleGroupExpansion}
          onEdgeZIndexChange={handleEdgeZIndexChange}
          edgeZIndex={edgeZIndex}
          expandedGroups={expandedGroups}
        />

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 왼쪽 사이드바 - MSA 정보 + React Flow 컨트롤 */}
          <div className="lg:col-span-1">
            <ProcessInfoSidebar
              nodes={nodes}
              edges={edges}
              selectedNodes={selectedNodes}
              selectedEdges={selectedEdges}
              savedCanvases={savedCanvases}
              currentCanvasId={currentCanvasId}
              isLoadingCanvases={isLoadingCanvases}
              serviceStatus={serviceStatus}
              onLoadCanvas={handleLoadFromBackend}
              onDeleteCanvas={handleDeleteCanvas}
              onAddNode={addProcessNode}
              onAddEdge={addProcessEdge}
              onDeleteSelected={deleteSelectedElements}
              isReadOnly={isReadOnly}
            />
          </div>

          {/* 메인 React Flow 에디터 */}
          <div className="lg:col-span-3">
            <div className="bg-[#1e293b] rounded-lg shadow-lg p-6 border border-[#334155]">
              {/* React Flow 에디터 - MSA 실시간 동기화 */}
              <div className="h-[600px] w-full">
                <ProcessFlowEditor
                  initialNodes={nodes}
                  initialEdges={edges}
                  onFlowChange={handleFlowChange}
                  readOnly={isReadOnly}
                  onDeleteSelected={deleteSelectedElements}
                  flowId={currentCanvasId || undefined} // MSA 동기화용 ID
                  // Sub Flow 기능 추가
                  edgeZIndex={edgeZIndex}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}