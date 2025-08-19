'use client';

import React, { useState, useCallback, useEffect, useRef, useMemo, useTransition } from 'react';
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
  type ReactFlowInstance,
  type Node,
  type Edge,
  type OnInit,
  type OnBeforeDelete,
  type ConnectionLineType,
  type SelectionMode,
  type PanOnScrollMode,
  type ConnectionMode,
  type ReactFlowJsonObject,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ProcessNodeComponent from '../organisms/ProcessNode';
import ProcessEdgeComponent from '../organisms/ProcessEdge';
import GroupNodeComponent from '@/components/organisms/GroupNode';
import CustomNodeComponent from '@/components/organisms/CustomNode';

import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';

// ============================================================================
// 🎯 React Flow 고급 기능 훅들
// ============================================================================

import { useLayoutEngine, useEdgeRouting, useAdvancedViewport } from '@/hooks';

// ============================================================================
// 🎯 노드 및 엣지 타입 정의
// ============================================================================

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
  edgeZIndex?: number;
}

// ============================================================================
// 🎯 React Flow Editor 컴포넌트 (완전 리팩토링)
// ============================================================================

const ProcessFlowEditor: React.FC<ProcessFlowEditorProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
  onDeleteSelected,
  flowId,
  edgeZIndex: propEdgeZIndex
}) => {
  // ============================================================================
  // 🎯 상태 관리
  // ============================================================================
  
  const [nodes, setNodes] = useState<AppNodeType[]>(initialNodes);
  const [edges, setEdges] = useState<AppEdgeType[]>(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance<AppNodeType, AppEdgeType> | null>(null);
  const [selectedElements, setSelectedElements] = useState<{ nodes: Node[]; edges: Edge[] }>({ nodes: [], edges: [] });
  const [isPending, startTransition] = useTransition();
  
  // Sub Flow 관련 상태
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());
  const [edgeZIndex, setEdgeZIndex] = useState<number>(propEdgeZIndex || 1);
  
  // 성능 최적화 상태
  const [showMiniMap, setShowMiniMap] = useState(true);
  const [showControls, setShowControls] = useState(true);
  const [onlyRenderVisible, setOnlyRenderVisible] = useState(true);

  // ============================================================================
  // 🎯 React Flow 고급 기능 훅들
  // ============================================================================
  
  const layoutEngine = useLayoutEngine();
  const edgeRouting = useEdgeRouting();
  const advancedViewport = useAdvancedViewport();

  // ============================================================================
  // 🎯 외부 상태 동기화
  // ============================================================================
  
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes]);

  useEffect(() => {
    setEdges(initialEdges);
  }, [initialEdges]);

  // ============================================================================
  // 🎯 노드 변경 핸들러 (성능 최적화)
  // ============================================================================
  
  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      startTransition(() => {
        const newNodes = applyNodeChanges(changes, nodes) as AppNodeType[];
        setNodes(newNodes);
        onFlowChange?.(newNodes, edges);
        
        // Sub Flow: 그룹 노드 변경 시 자식 노드 위치 업데이트
        changes.forEach(change => {
          if (change.type === 'position' && change.position) {
            const node = newNodes.find(n => n.id === change.id);
            if (node?.parentId) {
              const parentNode = newNodes.find(n => n.id === node.parentId);
              if (parentNode) {
                const relativeX = node.position.x - parentNode.position.x;
                const relativeY = node.position.y - parentNode.position.y;
                node.position.x = parentNode.position.x + relativeX;
                node.position.y = parentNode.position.y + relativeY;
              }
            }
          }
        });
      });
    },
    [nodes, edges, onFlowChange]
  );

  // ============================================================================
  // 🎯 엣지 변경 핸들러
  // ============================================================================
  
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      const newEdges = applyEdgeChanges(changes, edges) as AppEdgeType[];
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
    },
    [edges, nodes, onFlowChange]
  );

  // ============================================================================
  // 🎯 연결 검증 및 생성 (Validation + Reconnect)
  // ============================================================================
  
  const isValidConnection = useCallback((connection: Connection) => {
    if (!connection.source || !connection.target) return false;
    
    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);
    
    if (!sourceNode || !targetNode) return false;
    
    // 예시: process 노드에서 meter 노드로만 연결 허용
    if (sourceNode.data?.kind === 'process' && targetNode.data?.kind === 'meter') {
      return true;
    }
    
    // 기본 연결 규칙: 같은 타입끼리는 연결 금지
    if (sourceNode.type === targetNode.type) {
      return false;
    }
    
    return true;
  }, [nodes]);

  const onConnect: OnConnect = useCallback(
    (params: Connection) => {
      if (!isValidConnection(params)) {
        // 연결 검증 실패 시 알림
        console.warn('❌ 유효하지 않은 연결:', params);
        return;
      }
      
      const newEdge: ProcessEdge = {
        id: `edge-${Date.now()}`,
        source: params.source!,
        target: params.target!,
        type: 'processEdge',
        data: {
          label: '공정 흐름',
          processType: 'standard',
        },
      };
      
      const newEdges = addEdge(newEdge, edges);
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
      console.log('✅ 새로운 연결 생성:', newEdge);
    },
    [edges, nodes, onFlowChange, isValidConnection]
  );

  // ============================================================================
  // 🎯 재연결 핸들러
  // ============================================================================
  
  const onEdgeUpdate = useCallback(
    (oldEdge: Edge, newConnection: Connection) => {
      if (!isValidConnection(newConnection)) {
        console.warn('❌ 재연결 검증 실패:', newConnection);
        return;
      }
      
      setEdges((els) => 
        els.map(edge => 
          edge.id === oldEdge.id 
            ? { ...edge, source: newConnection.source!, target: newConnection.target! }
            : edge
        )
      );
      console.log('✅ 엣지 재연결 완료:', { oldEdge, newConnection });
    },
    [isValidConnection]
  );

  // ============================================================================
  // 🎯 키보드 단축키 핸들러 (완전 구현)
  // ============================================================================
  
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (readOnly) return;
    
    // Delete/Backspace 키로 선택된 요소 삭제
    if ((event.key === 'Delete' || event.key === 'Backspace') && onDeleteSelected) {
      event.preventDefault();
      onDeleteSelected();
    }
    
         // Ctrl/Cmd + A: 전체 선택
     if ((event.ctrlKey || event.metaKey) && event.key === 'a') {
       event.preventDefault();
       if (reactFlowInstance) {
         // 전체 선택은 setNodes로 구현
         setNodes(prev => prev.map(node => ({ ...node, selected: true })));
         setEdges(prev => prev.map(edge => ({ ...edge, selected: true })));
       }
     }
    
    // Ctrl/Cmd + S: 저장 (개발용)
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault();
      handleSaveFlow();
    }
  }, [readOnly, onDeleteSelected, reactFlowInstance]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  // ============================================================================
  // 🎯 이벤트 핸들러 (완전 구현)
  // ============================================================================
  
  const onInit = useCallback((instance: ReactFlowInstance<AppNodeType, AppEdgeType>) => {
    setReactFlowInstance(instance);
    instance.fitView({ padding: 0.2, includeHiddenNodes: false });
    console.log('🚀 React Flow 초기화 완료');
  }, []);

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    console.log('🖱️ 노드 클릭:', node);
  }, []);

  const onEdgeClick = useCallback((event: React.MouseEvent, edge: Edge) => {
    console.log('🖱️ 엣지 클릭:', edge);
  }, []);

  const onMove = useCallback((event: any, viewport: any) => {
    console.log('🔄 뷰포트 이동:', viewport);
  }, []);

  const onSelectionChange = useCallback(({ nodes, edges }: { nodes: Node[]; edges: Edge[] }) => {
    setSelectedElements({ nodes, edges });
    console.log('📋 선택 변경:', { nodes: nodes.length, edges: edges.length });
  }, []);

  const onBeforeDelete = useCallback(async (elements: { nodes: Node[]; edges: Edge[] }) => {
    // 예시: 특정 노드 삭제 방지
    const hasProtectedNode = elements.nodes.some(node => node.data?.protected === true);
    if (hasProtectedNode) {
      console.warn('⚠️ 보호된 노드는 삭제할 수 없습니다');
      return false;
    }
    return true;
  }, []);

  // ============================================================================
  // 🎯 저장/복원 기능 (JSON)
  // ============================================================================
  
  const handleSaveFlow = useCallback(() => {
    if (!reactFlowInstance) return;
    
    const flowObject: ReactFlowJsonObject = reactFlowInstance.toObject();
    const jsonString = JSON.stringify(flowObject, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `flow-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('💾 플로우 저장 완료');
  }, [reactFlowInstance]);

  const handleLoadFlow = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const flowObject = JSON.parse(e.target?.result as string);
        setNodes(flowObject.nodes || []);
        setEdges(flowObject.edges || []);
        console.log('📂 플로우 로드 완료');
      } catch (error) {
        console.error('❌ 플로우 로드 실패:', error);
      }
    };
    reader.readAsText(file);
  }, []);

  // ============================================================================
  // 🎯 그룹 노드 관리
  // ============================================================================
  
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

  // ============================================================================
  // 🎯 커스텀 노드 라벨 변경 핸들러
  // ============================================================================
  
  const handleLabelChange = useCallback((nodeId: string, newLabel: string) => {
    setNodes(prev => 
      prev.map(node => 
        node.id === nodeId 
          ? { ...node, data: { ...node.data, label: newLabel } }
          : node
      )
    );
    
    // 상위 컴포넌트에 변경 알림
    onFlowChange?.(nodes, edges);
    
    console.log('✅ 노드 라벨 변경:', { nodeId, newLabel });
  }, [nodes, edges, onFlowChange]);

  // ============================================================================
  // 🎯 노드 타입 정의 (동적 생성)
  // ============================================================================
  
  const nodeTypes = useMemo(() => ({
    processNode: ProcessNodeComponent as any,
    groupNode: GroupNodeComponent as any,
    customNode: (props: any) => (
      <CustomNodeComponent {...props} onLabelChange={handleLabelChange} />
    ),
  }), [handleLabelChange]);

  const handleGroupResize = useCallback((groupId: string, width: number, height: number) => {
    setNodes(prev => 
      prev.map(node => 
        node.id === groupId 
          ? { ...node, style: { ...node.style, width, height } }
          : node
      )
    );
  }, []);

  const createFacilityGroup = useCallback(() => {
    const groupId = `facility-group-${Date.now()}`;
    const newGroup: AppNodeType = {
      id: groupId,
      type: 'groupNode',
      position: { x: 100, y: 100 },
      data: {
        label: '새 시설군',
        description: '공정 노드들을 포함하는 시설군',
        groupType: 'facility',
        childCount: 0,
        isExpanded: true,
        minWidth: 400,
        minHeight: 300,
        style: { width: 500, height: 400 }
      },
      style: { width: 500, height: 400 }
    };
    
    setNodes(prev => [...prev, newGroup]);
  }, []);

  // ============================================================================
  // 🎯 커스텀 노드 생성 함수
  // ============================================================================
  
  const createCustomNode = useCallback((kind: 'process' | 'meter' | 'sensor' | 'valve') => {
    const nodeId = `custom-${kind}-${Date.now()}`;
    const position = { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 };
    
    const nodeData = {
      label: `새 ${kind} 노드`,
      description: `${kind} 노드 설명`,
      kind,
      status: 'active' as const,
      value: Math.floor(Math.random() * 100),
      unit: kind === 'process' ? 'kW' : kind === 'meter' ? 'L/min' : kind === 'sensor' ? '°C' : '%'
    };

    const newNode: AppNodeType = {
      id: nodeId,
      type: 'customNode',
      position,
      data: nodeData
    };

    setNodes(prev => [...prev, newNode]);
    console.log('✅ 커스텀 노드 생성:', { kind, nodeId });
  }, []);

  // ============================================================================
  // 🎯 성능 최적화 설정
  // ============================================================================
  
  const performanceOptions = useMemo(() => ({
    onlyRenderVisibleElements: onlyRenderVisible,
    minZoom: 0.25,
    maxZoom: 2.5,
         translateExtent: [[-1000, -1000], [3000, 3000]] as [[number, number], [number, number]],
     nodeExtent: [[-500, -500], [2000, 2000]] as [[number, number], [number, number]],
    fitViewOptions: {
      padding: 0.2,
      includeHiddenNodes: false,
      minZoom: 0.1,
      maxZoom: 1.5
    }
  }), [onlyRenderVisible]);

  // ============================================================================
  // 🎯 상호작용 정책 설정
  // ============================================================================
  
  const interactionPolicy = useMemo(() => ({
    nodesDraggable: !readOnly,
    nodesConnectable: !readOnly,
    elementsSelectable: true,
    selectionOnDrag: true,
    selectionMode: 'partial' as SelectionMode,
    panOnDrag: true,
    panOnScroll: true,
    panOnScrollMode: 'free' as PanOnScrollMode,
    zoomOnScroll: true,
    zoomOnDoubleClick: false,
    autoPanOnNodeDrag: true,
    autoPanOnConnect: true,
    autoPanSpeed: 20,
    connectOnClick: true,
    connectionMode: 'strict' as ConnectionMode,
    edgesReconnectable: true,
    snapToGrid: true,
         snapGrid: [10, 10] as [number, number],
    deleteKeyCode: ['Delete', 'Backspace'],
    selectionKeyCode: 'Shift',
    multiSelectionKeyCode: ['Meta', 'Control'],
    panActivationKeyCode: 'Space',
    zoomActivationKeyCode: null,
    disableKeyboardA11y: false
  }), [readOnly]);

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
        
        // 성능 최적화
        {...performanceOptions}
        
        // 상호작용 정책
        {...interactionPolicy}
        
        // 기본 설정
        fitView
        attributionPosition="bottom-left"
        className="bg-[#0b0c0f]"
        defaultEdgeOptions={{ zIndex: edgeZIndex }}
        
        // 이벤트 핸들러
        onInit={onInit}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onMove={onMove}
        onSelectionChange={onSelectionChange}
        onBeforeDelete={onBeforeDelete}
        
        // 그룹 노드 드래그 제한
        onNodeDrag={(event, node, nodes) => {
          if (node.parentId) {
            const parentGroup = nodes.find(n => n.id === node.parentId);
            if (parentGroup && parentGroup.type === 'groupNode') {
              const groupData = parentGroup.data as any;
              const groupWidth = groupData.style?.width || 400;
              const groupHeight = groupData.style?.height || 300;
              
              const maxX = groupWidth - 150;
              const maxY = groupHeight - 50;
              
              if (node.position.x < 0) node.position.x = 0;
              if (node.position.y < 0) node.position.y = 0;
              if (node.position.x > maxX) node.position.x = maxX;
              if (node.position.y > maxY) node.position.y = maxY;
            }
          }
        }}
      >
        {/* 배경 */}
        <Background 
          color="#334155" 
          gap={16} 
          variant={'dots' as any} 
        />
        
        {/* 컨트롤 (토글 가능) */}
        {showControls && (
          <Controls 
            position="top-left"
            showZoom={true}
            showFitView={true}
            showInteractive={true}
          />
        )}
        
        {/* 미니맵 (토글 가능) */}
        {showMiniMap && (
          <MiniMap 
            position="bottom-right"
            nodeColor="#3b82f6"
            maskColor="rgb(0, 0, 0, 0.2)"
            zoomable
            pannable
          />
        )}

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
            <span className="px-2 py-1 bg-purple-600 rounded text-xs">
              그룹: {nodes.filter(n => n.type === 'groupNode').length}개
            </span>
            <span className="px-2 py-1 bg-purple-600 rounded text-xs">
              자식: {nodes.filter(n => n.parentId).length}개
            </span>
            <span className="px-2 py-1 bg-orange-600 rounded text-xs">
              레이아웃: {layoutEngine.currentAlgorithm}
            </span>
            <span className="px-2 py-1 bg-indigo-600 rounded text-xs">
              라우팅: {edgeRouting.currentRoutingType}
            </span>
            <span className="px-2 py-1 bg-teal-600 rounded text-xs">
              뷰포트: {advancedViewport.viewport.mode}
            </span>
          </div>
        </Panel>

        {/* 하단 도움말 패널 */}
        <Panel position="bottom-center" className="bg-[#1e293b] text-white p-2 rounded border border-[#334155] shadow-lg">
          <div className="text-xs text-[#94a3b8]">
            {readOnly ? (
              '🔒 읽기 전용 모드 - 노드 선택 및 확대/축소만 가능합니다'
            ) : (
              '🎯 편집 모드 - 드래그로 노드 이동, 핸들 연결로 엣지 생성, Delete/Backspace 키로 삭제, Ctrl+S로 저장'
            )}
          </div>
        </Panel>

        {/* 고급 기능 컨트롤 패널 */}
        <Panel position="bottom-left" className="bg-[#1e293b] text-white p-3 rounded border border-[#334155] shadow-lg">
          <div className="space-y-2">
            <div className="text-xs font-semibold text-[#cbd5e1]">🎨 고급 기능</div>
            
            {/* 성능 최적화 토글 */}
            <div className="flex gap-1">
              <button 
                onClick={() => setShowControls(!showControls)} 
                className={`px-2 py-1 rounded text-xs ${showControls ? 'bg-blue-600' : 'bg-gray-600'}`}
              >
                {showControls ? '👁️' : '🙈'} 컨트롤
              </button>
              <button 
                onClick={() => setShowMiniMap(!showMiniMap)} 
                className={`px-2 py-1 rounded text-xs ${showMiniMap ? 'bg-blue-600' : 'bg-gray-600'}`}
              >
                {showMiniMap ? '👁️' : '🙈'} 미니맵
              </button>
              <button 
                onClick={() => setOnlyRenderVisible(!onlyRenderVisible)} 
                className={`px-2 py-1 rounded text-xs ${onlyRenderVisible ? 'bg-green-600' : 'bg-red-600'}`}
              >
                {onlyRenderVisible ? '⚡' : '🐌'} 성능
              </button>
            </div>
            
            {/* 저장/로드 */}
            <div className="flex gap-1">
              <button onClick={handleSaveFlow} className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs">
                💾 저장
              </button>
              <label className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs cursor-pointer">
                📂 로드
                <input
                  type="file"
                  accept=".json"
                  onChange={handleLoadFlow}
                  className="hidden"
                />
              </label>
            </div>
            
            {/* 시설군 그룹 관리 */}
            <div className="flex gap-1">
              <button onClick={createFacilityGroup} className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                🏭 시설군 생성
              </button>
              <button onClick={() => setNodes([])} className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs">
                🗑️ 전체 삭제
              </button>
            </div>

            {/* 커스텀 노드 생성 */}
            <div className="flex gap-1">
              <button onClick={() => createCustomNode('process')} className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs">
                ⚙️ 공정 노드
              </button>
              <button onClick={() => createCustomNode('meter')} className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs">
                📊 계측 노드
              </button>
              <button onClick={() => createCustomNode('sensor')} className="px-2 py-1 bg-yellow-600 hover:bg-yellow-700 rounded text-xs">
                📡 센서 노드
              </button>
              <button onClick={() => createCustomNode('valve')} className="px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-xs">
                🔴 밸브 노드
              </button>
            </div>

            {/* ELK 레이아웃 엔진 컨트롤 */}
            <div className="flex gap-1">
              <button
                onClick={() => layoutEngine.applyAutoLayout(nodes, edges)}
                disabled={layoutEngine.isLayouting}
                className="px-2 py-1 bg-orange-600 hover:bg-orange-700 rounded text-xs disabled:opacity-50"
              >
                {layoutEngine.isLayouting ? '🔄' : '🎯'} ELK 자동 레이아웃
              </button>
              <button
                onClick={() => layoutEngine.applyELKLayout(nodes, edges, { layout: 'layered' })}
                disabled={layoutEngine.isLayouting}
                className="px-2 py-1 bg-orange-500 hover:bg-orange-600 rounded text-xs disabled:opacity-50"
              >
                📐 계층형
              </button>
              <button
                onClick={() => layoutEngine.applyELKLayout(nodes, edges, { layout: 'force' })}
                disabled={layoutEngine.isLayouting}
                className="px-2 py-1 bg-orange-500 hover:bg-orange-600 rounded text-xs disabled:opacity-50"
              >
                ⚡ 물리형
              </button>
              <button
                onClick={() => layoutEngine.resetLayout(nodes, edges)}
                className="px-2 py-1 bg-orange-700 hover:bg-orange-800 rounded text-xs"
              >
                🔄 리셋
              </button>
            </div>

            {/* 엣지 라우팅 컨트롤 */}
            <div className="flex gap-1">
              <button
                onClick={() => edgeRouting.applyAutoRouting(edges, nodes)}
                disabled={edgeRouting.isRouting}
                className="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 rounded text-xs disabled:opacity-50"
              >
                {edgeRouting.isRouting ? '🔄' : '🛣️'} 자동 라우팅
              </button>
              <button
                onClick={() => edgeRouting.resetRouting(edges)}
                className="px-2 py-1 bg-indigo-700 hover:bg-indigo-800 rounded text-xs"
              >
                🔄 리셋
              </button>
            </div>

            {/* 뷰포트 모드 컨트롤 */}
            <div className="flex gap-1">
              <button
                onClick={advancedViewport.enableDefaultMode}
                className={`px-2 py-1 rounded text-xs ${
                  advancedViewport.isInDefaultMode 
                    ? 'bg-teal-600 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                🖱️ 기본
              </button>
              <button
                onClick={advancedViewport.enableDesignToolMode}
                className={`px-2 py-1 rounded text-xs ${
                  advancedViewport.isInDesignMode 
                    ? 'bg-teal-600 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                🎨 디자인
              </button>
              <button
                onClick={advancedViewport.enableMapMode}
                className={`px-2 py-1 rounded text-xs ${
                  advancedViewport.isInMapMode 
                    ? 'bg-teal-600 text-white' 
                    : 'bg-gray-600 hover:bg-gray-700'
                }`}
              >
                🗺️ 지도
              </button>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export default ProcessFlowEditor;