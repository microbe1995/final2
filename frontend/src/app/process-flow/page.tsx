'use client';

import React from 'react';
import ProcessControlHeader from '@/organisms/ProcessControlHeader';
import ProcessInfoSidebar from '@/organisms/ProcessInfoSidebar';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import { useProcessFlowDomain } from '@/hooks/useProcessFlow';
import { addEdge } from '@xyflow/react';
import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';

// ============================================================================
// 🎯 Process Flow 페이지 컴포넌트
// ============================================================================

export default function ProcessFlowPage() {
  // ============================================================================
  // 🎯 커스텀 훅 사용 - 단일 책임
  // ============================================================================
  
  // Process Flow 상태 및 API 관리
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
    saveToBackend,
    loadFromBackend,
    clearFlow,
  } = useProcessFlowDomain();

  // ReactFlow 노드/엣지 관리 (내장 기능 사용)
  const addProcessNode = () => {
    const newNode: ProcessNode = {
      id: `node-${Date.now()}`,
      type: 'processNode',
      position: { x: 250, y: 250 },
      data: {
        label: '새 공정 단계',
        processType: 'manufacturing',
        description: '공정 단계 설명을 입력하세요',
        parameters: {},
      },
    };
    handleFlowChange([...nodes, newNode], edges);
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
    const selectedNodes = nodes.filter((node) => node.selected);
    const selectedEdges = edges.filter((edge) => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      const newNodes = nodes.filter((node) => !node.selected);
      const newEdges = edges.filter((edge) => !edge.selected);
      handleFlowChange(newNodes, newEdges);
    } else {
      alert('삭제할 요소를 선택해주세요.');
    }
  };


  // ============================================================================
  // 🚀 이벤트 핸들러 - 단일 책임
  // ============================================================================
  
  // 백엔드 저장 핸들러
  const handleSaveToBackend = async () => {
    try {
      await saveToBackend();
      alert('공정도가 성공적으로 저장되었습니다!');
    } catch (error) {
      alert('백엔드 저장에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 백엔드 로드 핸들러
  const handleLoadFromBackend = async (canvasId?: string) => {
    try {
      const success = await loadFromBackend(canvasId);
      if (success) {
        alert('공정도를 성공적으로 불러왔습니다!');
      } else {
        alert('저장된 공정도가 없습니다. 새로 만들어보세요!');
      }
    } catch (error) {
      alert('백엔드 로드에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // Flow 초기화 핸들러
  const handleClearFlow = () => {
    if (confirm('현재 공정도를 모두 지우시겠습니까?')) {
      clearFlow();
    }
  };

  // ============================================================================
  // 🎨 렌더링 - UI만 담당
  // ============================================================================

  return (
    <div className="min-h-screen bg-[#0b0c0f]">
      {/* 헤더 */}
      <ProcessControlHeader
        serviceStatus={serviceStatus}
        isReadOnly={isReadOnly}
        onToggleReadOnly={toggleReadOnly}
        onExport={exportFlow}
        onSaveToBackend={handleSaveToBackend}
        onLoadFromBackend={handleLoadFromBackend}
        onClearFlow={handleClearFlow}
        savedCanvases={savedCanvases}
        isLoadingCanvases={isLoadingCanvases}
        currentCanvasId={currentCanvasId}
      />

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 왼쪽 사이드바 - 정보 패널 */}
          <div className="lg:col-span-1">
            <ProcessInfoSidebar
              nodes={nodes}
              edges={edges}
              selectedNodes={selectedNodes}
              selectedEdges={selectedEdges}
              savedCanvases={savedCanvases}
              currentCanvasId={currentCanvasId}
            />
          </div>

          {/* 메인 공정도 에디터 - ReactFlow 표준 */}
          <div className="lg:col-span-3">
            <div className="bg-[#1e293b] rounded-lg shadow-lg p-6 border border-[#334155]">
              {/* React Flow 에디터 - 명시적 높이 설정 */}
              <div className="h-[600px] w-full">
                <ProcessFlowEditor
                  initialNodes={nodes}
                  initialEdges={edges}
                  onFlowChange={handleFlowChange}
                  readOnly={isReadOnly}
                  onDeleteSelected={deleteSelectedElements}
                />
              </div>
              
              {/* ReactFlow 내부 Panel로 대체 */}
            </div>
          </div>
        </div>
      </div>

      {/* 모달 제거 - ReactFlow Panel로 대체 */}
    </div>
  );
}
