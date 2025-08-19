'use client';

import React, { useState } from 'react';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import { useProcessFlowDomain } from '@/hooks/useProcessFlow';
import { addEdge } from '@xyflow/react';
import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';
import Card from '@/molecules/Card';
import Button from '@/atoms/Button';
import Badge from '@/atoms/Badge';

// ============================================================================
// 🎯 Pure React Flow 기반 Process Flow 페이지
// ============================================================================

export default function ProcessFlowPage() {
  // ============================================================================
  // 🎯 Pure React Flow 상태 관리 (백엔드 의존성 제거)
  // ============================================================================
  
  const {
    nodes,
    edges,
    isReadOnly,
    selectedNodes,
    selectedEdges,
    handleFlowChange,
    toggleReadOnly,
    exportFlow,
    importFlow,
    clearFlow,
    saveToLocalStorage,
    loadFromLocalStorage,
    getSavedFlows,
  } = useProcessFlowDomain();

  // 로컬 저장된 Flow 목록 상태
  const [savedFlows, setSavedFlows] = useState(getSavedFlows());
  const [showSavedFlows, setShowSavedFlows] = useState(false);

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

  // ============================================================================
  // 🚀 로컬 스토리지 이벤트 핸들러
  // ============================================================================
  
  const handleSaveToLocal = () => {
    const name = prompt('Flow 이름을 입력하세요:', `Flow ${new Date().toLocaleDateString()}`);
    if (name) {
      saveToLocalStorage(name);
      setSavedFlows(getSavedFlows()); // 목록 새로고침
      alert('로컬에 저장되었습니다!');
    }
  };

  const handleLoadFromLocal = (key: string) => {
    if (loadFromLocalStorage(key)) {
      alert('Flow를 성공적으로 불러왔습니다!');
      setShowSavedFlows(false);
    } else {
      alert('Flow를 불러오는데 실패했습니다.');
    }
  };

  const handleClearFlow = () => {
    if (confirm('현재 공정도를 모두 지우시겠습니까?')) {
      clearFlow();
    }
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================

  return (
    <div className="min-h-screen bg-[#0b0c0f] text-white">
      {/* 헤더 */}
      <div className="bg-[#1e293b] border-b border-[#334155] p-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">공정도 관리</h1>
              <p className="text-[#94a3b8] mt-1">React Flow 기반의 인터랙티브 공정도 에디터</p>
            </div>
            
            <div className="flex items-center gap-3">
              <Badge variant={isReadOnly ? 'secondary' : 'primary'}>
                {isReadOnly ? '읽기 전용' : '편집 모드'}
              </Badge>
              
              <Button
                variant="secondary"
                size="sm"
                onClick={toggleReadOnly}
              >
                {isReadOnly ? '편집 모드' : '읽기 전용'}
              </Button>
              
              <Button
                variant="primary"
                size="sm"
                onClick={exportFlow}
              >
                내보내기
              </Button>
              
              <Button
                variant="secondary"
                size="sm"
                onClick={importFlow}
              >
                가져오기
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 왼쪽 사이드바 - 컨트롤 패널 */}
          <div className="lg:col-span-1 space-y-4">
            {/* 공정도 정보 */}
            <Card className="p-4 bg-[#1e293b] border-[#334155]">
              <h3 className="text-lg font-semibold text-white mb-4">공정도 정보</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[#94a3b8]">공정 단계:</span>
                  <span className="text-white font-medium">{nodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#94a3b8]">연결 흐름:</span>
                  <span className="text-white font-medium">{edges.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#94a3b8]">선택된 노드:</span>
                  <span className="text-white font-medium">{selectedNodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#94a3b8]">선택된 엣지:</span>
                  <span className="text-white font-medium">{selectedEdges.length}</span>
                </div>
              </div>
            </Card>

            {/* 편집 도구 */}
            <Card className="p-4 bg-[#1e293b] border-[#334155]">
              <h3 className="text-lg font-semibold text-white mb-4">편집 도구</h3>
              <div className="space-y-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={addProcessNode}
                  disabled={isReadOnly}
                  className="w-full"
                >
                  + 공정 노드
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={addProcessEdge}
                  disabled={isReadOnly || nodes.length < 2}
                  className="w-full"
                >
                  + 공정 흐름
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={deleteSelectedElements}
                  disabled={isReadOnly}
                  className="w-full"
                >
                  선택 삭제
                </Button>
              </div>
            </Card>

            {/* 로컬 저장 관리 */}
            <Card className="p-4 bg-[#1e293b] border-[#334155]">
              <h3 className="text-lg font-semibold text-white mb-4">로컬 저장 관리</h3>
              <div className="space-y-2">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSaveToLocal}
                  className="w-full"
                >
                  로컬 저장
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowSavedFlows(!showSavedFlows)}
                  className="w-full"
                >
                  저장된 Flow 보기
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleClearFlow}
                  className="w-full"
                >
                  전체 초기화
                </Button>
              </div>

              {/* 저장된 Flow 목록 */}
              {showSavedFlows && (
                <div className="mt-4 space-y-2">
                  <h4 className="text-sm font-medium text-[#94a3b8]">저장된 Flow 목록</h4>
                  {savedFlows.length === 0 ? (
                    <p className="text-xs text-[#64748b]">저장된 Flow가 없습니다.</p>
                  ) : (
                    <div className="space-y-1 max-h-40 overflow-y-auto">
                      {savedFlows.map((flow) => (
                        <div key={flow.key} className="p-2 bg-[#334155] rounded text-xs">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-white font-medium truncate">{flow.name}</p>
                              <p className="text-[#94a3b8]">
                                노드: {flow.nodeCount}, 엣지: {flow.edgeCount}
                              </p>
                            </div>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => handleLoadFromLocal(flow.key)}
                              className="ml-2 text-xs py-1 px-2"
                            >
                              로드
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </Card>
          </div>

          {/* 메인 공정도 에디터 */}
          <div className="lg:col-span-3">
            <Card className="p-6 bg-[#1e293b] border-[#334155]">
              <div className="h-[600px] w-full">
                <ProcessFlowEditor
                  initialNodes={nodes}
                  initialEdges={edges}
                  onFlowChange={handleFlowChange}
                  readOnly={isReadOnly}
                  onDeleteSelected={deleteSelectedElements}
                />
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}