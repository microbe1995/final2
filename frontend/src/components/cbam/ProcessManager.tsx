'use client';

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/Button';
import {
  Plus,
  Edit,
  Trash2,
  Save,
  Download,
  Upload,
  Eye,
  Settings,
  Link,
  Unlink,
} from 'lucide-react';
import ProcessStepModal from './ProcessStepModal';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  NodeTypes,
  EdgeTypes,
  Panel,
  useReactFlow,
  ConnectionMode,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// ============================================================================
// 🎯 CBAM 프로세스 타입 정의
// ============================================================================

interface ProcessStepData extends Record<string, unknown> {
  name: string;
  type: 'input' | 'process' | 'output';
  description: string;
  parameters: Record<string, any>;
  status: 'active' | 'inactive' | 'error';
}

interface ProcessFlow {
  id: string;
  name: string;
  description: string;
  nodes: Node<ProcessStepData>[];
  edges: Edge[];
  createdAt: string;
  updatedAt: string;
  version: string;
}

// ============================================================================
// 🎯 커스텀 노드 타입 정의
// ============================================================================

const CustomNode = ({
  data,
  selected,
}: {
  data: ProcessStepData;
  selected?: boolean;
}) => {
  const getNodeStyle = () => {
    const baseStyle = 'p-3 rounded-lg border-2 min-w-[150px] transition-all';

    switch (data.type) {
      case 'input':
        return `${baseStyle} bg-blue-100 border-blue-300 text-blue-800 ${
          selected ? 'border-blue-500 shadow-lg' : ''
        }`;
      case 'process':
        return `${baseStyle} bg-green-100 border-green-300 text-green-800 ${
          selected ? 'border-green-500 shadow-lg' : ''
        }`;
      case 'output':
        return `${baseStyle} bg-purple-100 border-purple-300 text-purple-800 ${
          selected ? 'border-purple-500 shadow-lg' : ''
        }`;
      default:
        return `${baseStyle} bg-gray-100 border-gray-300 text-gray-800 ${
          selected ? 'border-gray-500 shadow-lg' : ''
        }`;
    }
  };

  const getStatusColor = () => {
    switch (data.status) {
      case 'active':
        return 'bg-green-500';
      case 'inactive':
        return 'bg-gray-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className={getNodeStyle()}>
      <div className='flex items-center justify-between mb-2'>
        <div className='flex items-center gap-2'>
          <span className='text-xs font-medium uppercase opacity-70'>
            {data.type}
          </span>
          <div className={`w-2 h-2 rounded-full ${getStatusColor()}`} />
        </div>
      </div>
      <div className='font-semibold text-sm mb-1'>{data.name}</div>
      <div className='text-xs opacity-70 mb-2'>{data.description}</div>

      {/* 파라미터 미리보기 */}
      {Object.keys(data.parameters).length > 0 && (
        <div className='text-xs opacity-60'>
          {Object.entries(data.parameters)
            .slice(0, 2)
            .map(([key, value]) => (
              <div key={key} className='flex justify-between'>
                <span>{key}:</span>
                <span className='font-medium'>{String(value)}</span>
              </div>
            ))}
          {Object.keys(data.parameters).length > 2 && (
            <div className='text-center opacity-50'>...</div>
          )}
        </div>
      )}
    </div>
  );
};

const nodeTypes: NodeTypes = {
  custom: CustomNode,
};

// ============================================================================
// 🎯 커스텀 엣지 타입 정의
// ============================================================================

const CustomEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  selected,
}: any) => {
  const [edgePath] = useMemo(() => {
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;

    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY} ${targetX} ${targetY}`;

    return [path];
  }, [sourceX, sourceY, targetX, targetY]);

  return (
    <>
      <path
        id={id}
        className='react-flow__edge-path'
        d={edgePath}
        stroke={selected ? '#3b82f6' : '#6b7280'}
        strokeWidth={selected ? 3 : 2}
        fill='none'
        markerEnd='url(#arrowhead)'
      />
      {selected && (
        <path
          d={edgePath}
          stroke='#3b82f6'
          strokeWidth={6}
          fill='none'
          opacity={0.3}
        />
      )}
    </>
  );
};

const edgeTypes: EdgeTypes = {
  custom: CustomEdge,
};

// ============================================================================
// 🎯 CBAM 프로세스 매니저 컴포넌트
// ============================================================================

export default function ProcessManager() {
  const [flows, setFlows] = useState<ProcessFlow[]>([]);
  const [selectedFlow, setSelectedFlow] = useState<ProcessFlow | null>(null);
  const [showProcessModal, setShowProcessModal] = useState(false);
  const [editingNode, setEditingNode] = useState<Node<ProcessStepData> | null>(
    null
  );
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<string | null>(null);

  // React Flow 상태 관리
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges, deleteElements } = useReactFlow();

  // ============================================================================
  // 🎯 초기 데이터 로드
  // ============================================================================

  useEffect(() => {
    const savedFlows = localStorage.getItem('cbam-process-flows');
    if (savedFlows) {
      try {
        const parsedFlows = JSON.parse(savedFlows);
        setFlows(parsedFlows);

        // 첫 번째 플로우가 있으면 자동 선택
        if (parsedFlows.length > 0 && !selectedFlow) {
          selectFlow(parsedFlows[0]);
        }
      } catch (error) {
        // 개발 환경에서만 에러 로그 출력
        if (process.env.NODE_ENV === 'development') {
          console.error('저장된 플로우 로드 실패:', error);
        }
      }
    }
  }, []);

  // selectedFlow가 변경될 때 자동으로 선택
  useEffect(() => {
    if (selectedFlow) {
      setNodes(selectedFlow.nodes);
      setEdges(selectedFlow.edges);
    }
  }, [selectedFlow, setNodes, setEdges]);

  // ============================================================================
  // 🎯 플로우 저장
  // ============================================================================

  const saveFlows = useCallback((newFlows: ProcessFlow[]) => {
    localStorage.setItem('cbam-process-flows', JSON.stringify(newFlows));
    setFlows(newFlows);
  }, []);

  // ============================================================================
  // 🎯 새 플로우 생성
  // ============================================================================

  const createNewFlow = useCallback(() => {
    const defaultNodes: Node<ProcessStepData>[] = [
      {
        id: 'input-1',
        type: 'custom',
        position: { x: 100, y: 100 },
        data: {
          name: '원료 입력',
          type: 'input',
          description: '철광석, 코크스 등 원료 투입',
          parameters: { material: 'iron_ore', quantity: 1000, unit: 'ton' },
          status: 'active',
        },
      },
      {
        id: 'process-1',
        type: 'custom',
        position: { x: 350, y: 100 },
        data: {
          name: '고로 공정',
          type: 'process',
          description: '철광석 환원 및 용융 공정',
          parameters: { temperature: 1500, pressure: 1.2, duration: 8 },
          status: 'active',
        },
      },
      {
        id: 'process-2',
        type: 'custom',
        position: { x: 600, y: 100 },
        data: {
          name: '제강 공정',
          type: 'process',
          description: '탄소 함량 조절 및 정련',
          parameters: { carbon_content: 0.15, oxygen_blow: true, duration: 4 },
          status: 'active',
        },
      },
      {
        id: 'output-1',
        type: 'custom',
        position: { x: 850, y: 100 },
        data: {
          name: '최종 제품',
          type: 'output',
          description: '철강 제품 (강판, 강재)',
          parameters: {
            product_type: 'steel_plate',
            quantity: 800,
            unit: 'ton',
          },
          status: 'active',
        },
      },
    ];

    const defaultEdges: Edge[] = [
      {
        id: 'e1-2',
        source: 'input-1',
        target: 'process-1',
        type: 'custom',
        markerEnd: { type: MarkerType.ArrowClosed },
      },
      {
        id: 'e2-3',
        source: 'process-1',
        target: 'process-2',
        type: 'custom',
        markerEnd: { type: MarkerType.ArrowClosed },
      },
      {
        id: 'e3-4',
        source: 'process-2',
        target: 'output-1',
        type: 'custom',
        markerEnd: { type: MarkerType.ArrowClosed },
      },
    ];

    const newFlow: ProcessFlow = {
      id: `flow-${Date.now()}`,
      name: '새 CBAM 프로세스',
      description: '새로 생성된 CBAM 프로세스 플로우',
      nodes: defaultNodes,
      edges: defaultEdges,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: '1.0.0',
    };

    const updatedFlows = [...flows, newFlow];
    saveFlows(updatedFlows);
    selectFlow(newFlow);
  }, [flows, saveFlows]);

  // ============================================================================
  // 🎯 플로우 선택
  // ============================================================================

  const selectFlow = useCallback(
    (flow: ProcessFlow) => {
      setSelectedFlow(flow);
      setNodes(flow.nodes);
      setEdges(flow.edges);
    },
    [setNodes, setEdges]
  );

  // ============================================================================
  // 🎯 플로우 삭제
  // ============================================================================

  const deleteFlow = useCallback(
    (flowId: string) => {
      if (window.confirm('정말로 이 플로우를 삭제하시겠습니까?')) {
        const updatedFlows = flows.filter(flow => flow.id !== flowId);
        saveFlows(updatedFlows);
        if (selectedFlow?.id === flowId) {
          setSelectedFlow(null);
          setNodes([]);
          setEdges([]);
        }
      }
    },
    [flows, selectedFlow, saveFlows, setNodes, setEdges]
  );

  // ============================================================================
  // 🎯 플로우 저장
  // ============================================================================

  const saveCurrentFlow = useCallback(() => {
    if (!selectedFlow) return;

    const updatedFlow: ProcessFlow = {
      ...selectedFlow,
      nodes,
      edges,
      updatedAt: new Date().toISOString(),
    };

    const updatedFlows = flows.map(flow =>
      flow.id === selectedFlow.id ? updatedFlow : flow
    );

    saveFlows(updatedFlows);
    setSelectedFlow(updatedFlow);
    alert('플로우가 저장되었습니다!');
  }, [selectedFlow, nodes, edges, flows, saveFlows]);

  // ============================================================================
  // 🎯 플로우 내보내기
  // ============================================================================

  const exportFlow = useCallback((flow: ProcessFlow) => {
    const dataStr = JSON.stringify(flow, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `${flow.name.replace(/\s+/g, '_')}.json`;
    link.click();

    URL.revokeObjectURL(url);
  }, []);

  // ============================================================================
  // 🎯 플로우 가져오기
  // ============================================================================

  const importFlow = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = e => {
        try {
          const importedFlow: ProcessFlow = JSON.parse(
            e.target?.result as string
          );
          importedFlow.id = `flow-${Date.now()}`;
          importedFlow.createdAt = new Date().toISOString();
          importedFlow.updatedAt = new Date().toISOString();

          const updatedFlows = [...flows, importedFlow];
          saveFlows(updatedFlows);
          selectFlow(importedFlow);
          alert('플로우가 성공적으로 가져와졌습니다!');
        } catch (error) {
          alert('플로우 파일 형식이 올바르지 않습니다.');
        }
      };
      reader.readAsText(file);
    },
    [flows, saveFlows, selectFlow]
  );

  // ============================================================================
  // 🎯 새 노드 추가
  // ============================================================================

  const addNewNode = useCallback(() => {
    if (!selectedFlow) return;

    const newNode: Node<ProcessStepData> = {
      id: `node-${Date.now()}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        name: '새 단계',
        type: 'process',
        description: '새로 추가된 프로세스 단계',
        parameters: {},
        status: 'active',
      },
    };

    addNodes(newNode);
  }, [selectedFlow, addNodes]);

  // ============================================================================
  // 🎯 노드 편집
  // ============================================================================

  const editNode = useCallback((node: Node<ProcessStepData>) => {
    setEditingNode(node);
    setShowProcessModal(true);
  }, []);

  // ============================================================================
  // 🎯 노드 저장
  // ============================================================================

  const saveNode = useCallback(
    (updatedData: ProcessStepData) => {
      if (!editingNode) return;

      const updatedNodes = nodes.map(node =>
        node.id === editingNode.id ? { ...node, data: updatedData } : node
      );

      setNodes(updatedNodes);
      setShowProcessModal(false);
      setEditingNode(null);
    },
    [editingNode, nodes, setNodes]
  );

  // ============================================================================
  // 🎯 연결 관리
  // ============================================================================

  const onConnect = useCallback(
    (params: Connection) => {
      if (params.source && params.target) {
        const newEdge: Edge = {
          id: `e${params.source}-${params.target}`,
          source: params.source,
          target: params.target,
          type: 'custom',
          markerEnd: { type: MarkerType.ArrowClosed },
        };
        addEdges(newEdge);
      }
    },
    [addEdges]
  );

  const onConnectStart = useCallback((event: any, params: any) => {
    setIsConnecting(true);
    setConnectionStart(params.nodeId);
  }, []);

  const onConnectEnd = useCallback(() => {
    setIsConnecting(false);
    setConnectionStart(null);
  }, []);

  // ============================================================================
  // 🎯 메인 렌더링
  // ============================================================================

  return (
    <div className='space-y-6'>
      {/* 플로우 목록 */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
        {flows.map(flow => (
          <div
            key={flow.id}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedFlow?.id === flow.id
                ? 'border-primary bg-primary/5'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
            onClick={() => selectFlow(flow)}
          >
            <div className='flex items-start justify-between mb-3'>
              <h3 className='font-semibold text-gray-900'>{flow.name}</h3>
              <div className='flex gap-2'>
                <button
                  onClick={e => {
                    e.stopPropagation();
                    exportFlow(flow);
                  }}
                  className='p-1 hover:bg-gray-100 rounded'
                  title='내보내기'
                >
                  <Download className='h-4 w-4' />
                </button>
                <button
                  onClick={e => {
                    e.stopPropagation();
                    deleteFlow(flow.id);
                  }}
                  className='p-1 hover:bg-red-100 rounded text-red-600'
                  title='삭제'
                >
                  <Trash2 className='h-4 w-4' />
                </button>
              </div>
            </div>
            <p className='text-sm text-gray-600 mb-3'>{flow.description}</p>
            <div className='flex items-center justify-between text-xs text-gray-500'>
              <span>노드: {flow.nodes.length}개</span>
              <span>v{flow.version}</span>
            </div>
          </div>
        ))}

        {/* 새 플로우 생성 버튼 */}
        <button
          onClick={createNewFlow}
          className='p-4 rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 transition-colors flex flex-col items-center justify-center text-gray-500 hover:text-gray-700'
        >
          <Plus className='h-8 w-8 mb-2' />
          <span className='font-medium'>새 플로우 생성</span>
        </button>
      </div>

      {/* 선택된 플로우 상세 보기 */}
      {selectedFlow && (
        <div className='space-y-6'>
          <div className='flex items-center justify-between'>
            <div>
              <h2 className='text-2xl font-bold text-gray-900'>
                {selectedFlow.name}
              </h2>
              <p className='text-gray-600'>{selectedFlow.description}</p>
            </div>
            <div className='flex gap-3'>
              <Button
                onClick={saveCurrentFlow}
                className='flex items-center gap-2 bg-blue-600 hover:bg-blue-700'
              >
                <Save className='h-4 w-4' />
                저장
              </Button>
              <Button
                onClick={addNewNode}
                className='flex items-center gap-2 bg-green-600 hover:bg-green-700'
              >
                <Plus className='h-4 w-4' />
                노드 추가
              </Button>
            </div>
          </div>

          {/* React Flow 캔버스 */}
          <div className='h-[600px] border-2 border-gray-200 rounded-lg overflow-hidden'>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onConnectStart={onConnectStart}
              onConnectEnd={onConnectEnd}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              connectionMode={ConnectionMode.Loose}
              deleteKeyCode='Delete'
              multiSelectionKeyCode='Shift'
              panOnDrag={true}
              zoomOnScroll={true}
              zoomOnPinch={true}
              panOnScroll={false}
              preventScrolling={true}
              className='bg-gray-50'
            >
              <Background gap={12} size={1} />
              <Controls />
              <MiniMap
                nodeStrokeColor={n => {
                  if (n.type === 'input') return '#3b82f6';
                  if (n.type === 'output') return '#8b5cf6';
                  return '#22c55e';
                }}
                nodeColor={n => {
                  if (n.type === 'input') return '#dbeafe';
                  if (n.type === 'output') return '#f3e8ff';
                  return '#dcfce7';
                }}
              />

              {/* 상단 패널 */}
              <Panel
                position='top-left'
                className='bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg'
              >
                <div className='flex items-center gap-2 text-sm text-gray-600'>
                  <div className='w-3 h-3 bg-blue-500 rounded-full'></div>
                  <span>입력</span>
                  <div className='w-3 h-3 bg-green-500 rounded-full ml-2'></div>
                  <span>처리</span>
                  <div className='w-3 h-3 bg-purple-500 rounded-full ml-2'></div>
                  <span>출력</span>
                </div>
              </Panel>

              {/* 우측 패널 */}
              <Panel
                position='top-right'
                className='bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg'
              >
                <div className='text-sm text-gray-600'>
                  <div>💡 노드를 드래그하여 연결하세요</div>
                  <div>🔄 연결선을 드래그하여 재연결</div>
                  <div>🗑️ Delete 키로 선택된 요소 삭제</div>
                </div>
              </Panel>
            </ReactFlow>
          </div>

          {/* 노드 상세 정보 */}
          <div className='space-y-4'>
            <h3 className='text-lg font-semibold text-gray-900'>
              노드 상세 정보
            </h3>
            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
              {nodes.map(node => (
                <div
                  key={node.id}
                  className={`p-4 rounded-lg border-2 ${
                    node.data.type === 'input'
                      ? 'border-blue-200 bg-blue-50'
                      : node.data.type === 'process'
                        ? 'border-green-200 bg-green-50'
                        : 'border-purple-200 bg-purple-50'
                  }`}
                >
                  <div className='flex items-center justify-between mb-3'>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        node.data.type === 'input'
                          ? 'bg-blue-100 text-blue-800'
                          : node.data.type === 'process'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-purple-100 text-purple-800'
                      }`}
                    >
                      {node.data.type}
                    </span>
                    <div className='flex gap-2'>
                      <button
                        onClick={() => editNode(node)}
                        className='p-1 hover:bg-white/50 rounded'
                      >
                        <Edit className='h-3 w-3' />
                      </button>
                      <button
                        onClick={() => deleteElements({ nodes: [node] })}
                        className='p-1 hover:bg-red-100 rounded text-red-600'
                      >
                        <Trash2 className='h-3 w-3' />
                      </button>
                    </div>
                  </div>
                  <h4 className='font-semibold text-gray-900 mb-2'>
                    {node.data.name}
                  </h4>
                  <p className='text-sm text-gray-600 mb-3'>
                    {node.data.description}
                  </p>

                  {/* 파라미터 표시 */}
                  {Object.keys(node.data.parameters).length > 0 && (
                    <div className='space-y-2'>
                      <h5 className='text-xs font-medium text-gray-700 uppercase'>
                        파라미터
                      </h5>
                      {Object.entries(node.data.parameters).map(
                        ([key, value]) => (
                          <div
                            key={key}
                            className='flex justify-between text-xs'
                          >
                            <span className='text-gray-600'>{key}:</span>
                            <span className='font-medium'>{String(value)}</span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 플로우 가져오기 */}
      <div className='border-t pt-6'>
        <h3 className='text-lg font-semibold text-gray-900 mb-4'>
          플로우 가져오기
        </h3>
        <div className='flex items-center gap-4'>
          <input
            type='file'
            accept='.json'
            onChange={importFlow}
            className='block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-primary/90'
          />
          <p className='text-sm text-gray-500'>
            JSON 형식의 CBAM 프로세스 플로우 파일을 선택하세요
          </p>
        </div>
      </div>

      {/* 프로세스 단계 편집 모달 */}
      <ProcessStepModal
        isOpen={showProcessModal}
        onClose={() => {
          setShowProcessModal(false);
          setEditingNode(null);
        }}
        node={editingNode}
        onSave={saveNode}
      />
    </div>
  );
}
