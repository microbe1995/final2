'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  addEdge,
  Connection,
  applyNodeChanges,
  applyEdgeChanges,
  Controls,
  MiniMap,
  Background,
  Panel,
  type OnConnect,
  type OnNodesChange,
  type OnEdgesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ProcessNodeComponent from '../organisms/ProcessNode';
import ProcessEdgeComponent from '../organisms/ProcessEdge';
import GroupNodeComponent from '../organisms/GroupNode';

import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';

// ============================================================================
// 🎯 노드 및 엣지 타입 정의
// ============================================================================

const nodeTypes = {
  processNode: ProcessNodeComponent as any,
  groupNode: GroupNodeComponent as any,
};

const edgeTypes = {
  processEdge: ProcessEdgeComponent as any,
};

// ============================================================================
// 🎯 Props 인터페이스
// ============================================================================

interface ProcessFlowEditorProps {
  initialNodes?: AppNodeType[];
  initialEdges?: AppEdgeType[];
  onFlowChange?: (nodes: AppNodeType[], edges: AppEdgeType[]) => void;
  readOnly?: boolean;
  onDeleteSelected?: () => void;
  flowId?: string; // MSA 백엔드 동기화용 Flow ID
  // Sub Flow 기능 추가
  edgeZIndex?: number;
}

// ============================================================================
// 🎯 Pure React Flow Editor 컴포넌트 (백엔드 동기화 제거)
// ============================================================================

const ProcessFlowEditor: React.FC<ProcessFlowEditorProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
  onDeleteSelected,
  flowId,
  // Sub Flow 기능 추가
  edgeZIndex: propEdgeZIndex
}) => {
  // ✅ Pure React Flow 상태 관리
  const [nodes, setNodes] = useState<AppNodeType[]>(initialNodes);
  const [edges, setEdges] = useState<AppEdgeType[]>(initialEdges);
  
  // Sub Flow 관련 상태
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [edgeZIndex, setEdgeZIndex] = useState<number>(propEdgeZIndex || 1);

  // 외부에서 전달받은 nodes/edges가 변경되면 내부 상태도 업데이트
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes]);

  useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges]);

  // ✅ Pure React Flow: applyNodeChanges, applyEdgeChanges 사용
  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      const newNodes = applyNodeChanges(changes, nodes) as AppNodeType[];
      setNodes(newNodes);
      onFlowChange?.(newNodes, edges);
      
      // Sub Flow: 그룹 노드 변경 시 자식 노드 위치 업데이트
      changes.forEach(change => {
        if (change.type === 'position' && change.position) {
          const node = newNodes.find(n => n.id === change.id);
          if (node?.parentId) {
            // 부모 노드가 이동하면 자식 노드도 함께 이동
            const parentNode = newNodes.find(n => n.id === node.parentId);
            if (parentNode) {
              // 자식 노드 위치를 부모 기준으로 상대적 위치로 조정
              const relativeX = node.position.x - parentNode.position.x;
              const relativeY = node.position.y - parentNode.position.y;
              node.position.x = parentNode.position.x + relativeX;
              node.position.y = parentNode.position.y + relativeY;
            }
          }
        }
      });
    },
    [nodes, edges, onFlowChange]
  );

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      const newEdges = applyEdgeChanges(changes, edges) as AppEdgeType[];
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
    },
    [nodes, edges, onFlowChange]
  );

  // ✅ Pure React Flow: addEdge 사용
  const onConnect: OnConnect = useCallback(
    (params: Connection) => {
      const newEdge: ProcessEdge = {
        id: `edge-${Date.now()}`,
        source: params.source,
        target: params.target,
        type: 'processEdge',
        data: {
          label: '공정 흐름',
          processType: 'standard',
        },
      };
      
      const newEdges = addEdge(newEdge, edges);
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
    },
    [edges, nodes, onFlowChange]
  );

  // 키보드 단축키 핸들러
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (readOnly) return;
    
    // Delete 키로 선택된 요소 삭제
    if (event.key === 'Delete' && onDeleteSelected) {
      onDeleteSelected();
    }
  }, [readOnly, onDeleteSelected]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-[#0b0c0f]"
        // 상호작용 설정
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={true}
        zoomOnScroll={true}
        panOnScroll={false}
        panOnDrag={true}
        selectNodesOnDrag={false}
        // 연결 설정
        connectionMode={'loose' as any}
        snapToGrid={true}
        snapGrid={[15, 15]}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        minZoom={0.1}
        maxZoom={2}
        // Sub Flow 지원
        defaultEdgeOptions={{ zIndex: edgeZIndex }}
      >
        {/* 배경 */}
        <Background 
          color="#334155" 
          gap={16} 
          variant={'dots' as any} 
        />
        
        {/* 컨트롤 */}
        <Controls 
          position="top-left"
          showZoom={true}
          showFitView={true}
          showInteractive={true}
        />
        
        {/* 미니맵 */}
        <MiniMap 
          position="bottom-right"
          nodeColor="#3b82f6"
          maskColor="rgb(0, 0, 0, 0.2)"
          zoomable
          pannable
        />

        {/* 상단 정보 패널 */}
        <Panel position="top-center" className="bg-[#1e293b] text-white p-3 rounded border border-[#334155] shadow-lg">
          <div className="flex items-center gap-4 text-sm">
            <span>노드: {nodes.length}</span>
            <span>엣지: {edges.length}</span>
            <span className={`px-2 py-1 rounded text-xs ${
              readOnly 
                ? 'bg-gray-600 text-gray-200' 
                : 'bg-blue-600 text-white'
            }`}>
              {readOnly ? '읽기 전용' : '편집 모드'}
            </span>
            {flowId && (
              <span className="px-2 py-1 bg-green-600 rounded text-xs">
                MSA 동기화 ON
              </span>
            )}
            {/* Sub Flow 정보 */}
            <span className="px-2 py-1 bg-purple-600 rounded text-xs">
              그룹: {nodes.filter(n => n.type === 'groupNode').length}개
            </span>
            <span className="px-2 py-1 bg-purple-600 rounded text-xs">
              자식: {nodes.filter(n => n.parentId).length}개
            </span>
          </div>
        </Panel>

        {/* 하단 도움말 패널 */}
        <Panel position="bottom-center" className="bg-[#1e293b] text-white p-2 rounded border border-[#334155] shadow-lg">
          <div className="text-xs text-[#94a3b8]">
            {readOnly ? (
              '🔒 읽기 전용 모드 - 노드 선택 및 확대/축소만 가능합니다'
            ) : (
              '🎯 편집 모드 - 드래그로 노드 이동, 핸들 연결로 엣지 생성, Delete 키로 삭제'
            )}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default ProcessFlowEditor;