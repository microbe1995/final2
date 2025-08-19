'use client';

import {
  ReactFlow,
  ReactFlowProvider,
  MarkerType,
  Background,
  Panel,
  useViewport,
  useConnection,
  Controls,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
} from '@xyflow/react';

import { useCallback, useState, useEffect } from 'react';
import { AnnotationNode } from '@/components/atoms/AnnotationNode';
import NodeWrapper from '@/components/atoms/NodeWrapper';
import { useReactFlowAPI } from '@/hooks/useReactFlowAPI';
import type { Node, Edge } from '@xyflow/react';

import '@xyflow/react/dist/style.css';

const nodeTypes = {
  annotation: AnnotationNode,
};

// ============================================================================
// 🎯 Props 인터페이스
// ============================================================================

interface ConnectedReactFlowProps {
  flowId?: string;
  autoSave?: boolean;
  saveInterval?: number;
}

// ============================================================================
// 🎯 뷰포트 정보 표시 컴포넌트
// ============================================================================

function ViewportWithAnnotation() {
  const viewport = useViewport();

  return (
    <>
      <NodeWrapper bottom={0} left={90} width={420}>
        <AnnotationNode
          data={{
            label: 'The viewport is defined by x, y and zoom, which is the transform & scale applied to the flow.',
          }}
        />
      </NodeWrapper>
      <div
        style={{
          fontFamily: 'monospace',
          background: 'white',
          padding: '8px',
          borderRadius: '6px',
          border: '1px solid #ddd',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <div style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          <div>x: {viewport.x.toFixed(2)}</div>
          <div>y: {viewport.y.toFixed(2)}</div>
          <div>zoom: {viewport.zoom.toFixed(2)}</div>
        </div>
      </div>
    </>
  );
}

// ============================================================================
// 🎯 메인 플로우 컴포넌트
// ============================================================================

function Flow({ flowId, autoSave, saveInterval }: ConnectedReactFlowProps) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  const connection = useConnection();
  const flowAPI = useReactFlowAPI();

  // ============================================================================
  // 🎯 초기 데이터 로드
  // ============================================================================

  useEffect(() => {
    const loadFlowData = async () => {
      if (!flowId) {
        // 플로우 ID가 없으면 새 플로우 생성
        const newFlow = await flowAPI.createFlow({
          name: `플로우 ${new Date().toLocaleString()}`,
          description: 'React Flow 다이어그램',
          viewport: { x: 0, y: 0, zoom: 1 }
        });
        
        if (newFlow) {
          // 기본 어노테이션 노드들 추가
          const initialNodes = [
            {
              id: 'annotation-1',
              type: 'annotation',
              draggable: false,
              selectable: false,
              data: {
                label: 'This is a "node"',
                arrowStyle: 'arrow-bottom-right',
              },
              position: { x: -65, y: -50 },
            },
            {
              id: '1-1',
              type: 'default',
              data: { label: 'node label' },
              position: { x: 150, y: 0 },
            },
            {
              id: 'annotation-2',
              type: 'annotation',
              draggable: false,
              selectable: false,
              data: {
                label: 'This is a "handle"',
                arrowStyle: 'arrow-top-left',
              },
              position: { x: 235, y: 35 },
            },
          ];
          
          setNodes(initialNodes);
          // 백엔드에 초기 노드들 저장
          await flowAPI.saveFlowState(newFlow.id, initialNodes, [], { x: 0, y: 0, zoom: 1 });
        }
      } else {
        // 기존 플로우 로드
        const flowState = await flowAPI.getFlowState(flowId);
        if (flowState) {
          const converted = flowAPI.convertBackendToFrontend(flowState);
          setNodes(converted.nodes);
          setEdges(converted.edges);
        }
      }
      setIsLoading(false);
    };

    loadFlowData();
  }, [flowId, flowAPI]);

  // ============================================================================
  // 🎯 자동 저장 기능
  // ============================================================================

  const saveToBackend = useCallback(async () => {
    if (!flowId || !hasUnsavedChanges) return;
    
    const viewport = { x: 0, y: 0, zoom: 1 }; // 실제로는 현재 뷰포트 값 사용
    const success = await flowAPI.saveFlowState(flowId, nodes, edges, viewport);
    
    if (success) {
      setLastSaved(new Date());
      setHasUnsavedChanges(false);
    }
  }, [flowId, nodes, edges, hasUnsavedChanges, flowAPI]);

  // 자동 저장 인터벌
  useEffect(() => {
    if (!autoSave || !saveInterval) return;
    
    const interval = setInterval(() => {
      saveToBackend();
    }, saveInterval);
    
    return () => clearInterval(interval);
  }, [autoSave, saveInterval, saveToBackend]);

  // ============================================================================
  // 🎯 노드/엣지 변경 핸들러
  // ============================================================================

  const onNodesChange = useCallback((changes: any) => {
    setNodes(prev => applyNodeChanges(changes, prev));
    setHasUnsavedChanges(true);
  }, []);

  const onEdgesChange = useCallback((changes: any) => {
    setEdges(prev => applyEdgeChanges(changes, prev));
    setHasUnsavedChanges(true);
  }, []);

  const onConnect = useCallback((connection: any) => {
    setEdges(prev => addEdge(connection, prev));
    setHasUnsavedChanges(true);
  }, []);

  // ============================================================================
  // 🎯 연결 어노테이션 로직
  // ============================================================================

  const onMouseMove = useCallback(() => {
    if (connection.inProgress) {
      const { from, to } = connection;
      const nodePosition = { x: to.x, y: to.y };

      setNodes(prevNodes => {
        const nodeExists = prevNodes.some(node => node.id === 'connection-annotation');
        const connectionAnnotation = {
          id: 'connection-annotation',
          type: 'annotation',
          selectable: false,
          data: {
            label: 'this is a "connection"',
            arrowStyle: 'arrow-top-left',
          },
          position: nodePosition,
          hidden: Math.abs(to.y - from.y) < 25 && Math.abs(to.x - from.x) < 25,
        };

        if (nodeExists) {
          return prevNodes.map(node =>
            node.id === 'connection-annotation' ? connectionAnnotation : node
          );
        } else {
          return [...prevNodes, connectionAnnotation];
        }
      });
    }
  }, [connection]);

  const onConnectEnd = useCallback(() => {
    setNodes(prevNodes =>
      prevNodes.filter(node => node.id !== 'connection-annotation')
    );
  }, []);

  // ============================================================================
  // 🎯 수동 저장
  // ============================================================================

  const handleManualSave = useCallback(() => {
    saveToBackend();
  }, [saveToBackend]);

  if (isLoading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">플로우 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100%' }} onMouseMove={onMouseMove}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onConnectEnd={onConnectEnd}
        fitView
        preventScrolling={false}
      >
        <Background />
        <Controls position="top-left" />
        
        {/* 뷰포트 정보 패널 */}
        <Panel position="bottom-left">
          <ViewportWithAnnotation />
        </Panel>
        
        {/* 저장 상태 패널 */}
        <Panel position="top-right">
          <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${hasUnsavedChanges ? 'bg-orange-500' : 'bg-green-500'}`}></div>
                <span className="text-sm font-medium">
                  {hasUnsavedChanges ? '저장되지 않음' : '저장됨'}
                </span>
              </div>
              
              {lastSaved && (
                <div className="text-xs text-gray-500">
                  마지막 저장: {lastSaved.toLocaleTimeString()}
                </div>
              )}
              
              <button
                onClick={handleManualSave}
                disabled={!hasUnsavedChanges}
                className={`px-3 py-1 rounded text-sm ${
                  hasUnsavedChanges
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                수동 저장
              </button>
              
              <div className="text-xs text-gray-400">
                노드: {nodes.length} | 엣지: {edges.length}
              </div>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

// ============================================================================
// 🎯 메인 컴포넌트 (Provider 포함)
// ============================================================================

function ConnectedReactFlow({ 
  flowId, 
  autoSave = true, 
  saveInterval = 10000 // 10초마다 자동 저장
}: ConnectedReactFlowProps) {
  return (
    <ReactFlowProvider>
      <Flow flowId={flowId} autoSave={autoSave} saveInterval={saveInterval} />
    </ReactFlowProvider>
  );
}

export default ConnectedReactFlow;
