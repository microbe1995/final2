'use client';

import React from 'react';
import ProcessFlowHeader from '@/organisms/ProcessFlowHeader';
import ProcessFlowInfoPanel from '@/organisms/ProcessFlowInfoPanel';
import ProcessFlowMain from '@/organisms/ProcessFlowMain';
import ProcessTypeModal from '@/molecules/ProcessTypeModal';
import { useProcessFlow } from '@/hooks/useProcessFlow';
import { useNodeManagement } from '@/hooks/useNodeManagement';
import { useProcessTypeModal } from '@/hooks/useProcessTypeModal';

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
  } = useProcessFlow();

  // 노드/엣지 관리
  const {
    addProcessNode,
    addProcessEdge,
    deleteSelectedElements,
  } = useNodeManagement(nodes, edges, handleFlowChange);

  // Process Type 모달 관리
  const {
    isOpen: isProcessTypeModalOpen,
    openModal: openProcessTypeModal,
    closeModal: closeProcessTypeModal,
    handleSelectType,
  } = useProcessTypeModal(addProcessNode, addProcessEdge);

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
      <ProcessFlowHeader
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
            <ProcessFlowInfoPanel
              nodes={nodes}
              edges={edges}
              selectedNodes={selectedNodes}
              selectedEdges={selectedEdges}
              savedCanvases={savedCanvases}
              currentCanvasId={currentCanvasId}
            />
          </div>

          {/* 메인 공정도 에디터 */}
          <ProcessFlowMain
            nodes={nodes}
            edges={edges}
            isReadOnly={isReadOnly}
            onFlowChange={handleFlowChange}
            onAddElement={openProcessTypeModal}
            onDeleteSelected={deleteSelectedElements}
          />
        </div>
      </div>

      {/* 공정 요소 유형 선택 모달 */}
      <ProcessTypeModal
        isOpen={isProcessTypeModalOpen}
        onClose={closeProcessTypeModal}
        onSelectType={handleSelectType}
      />
    </div>
  );
}
