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
import GroupNode from './GroupNode';
import SourceStreamEdge from './SourceStreamEdge';
import axiosClient from '@/lib/axiosClient';
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
  Handle,
  Position,
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
  onClick,
}: {
  data: ProcessStepData;
  selected?: boolean;
  onClick?: (node: any) => void;
}) => {
  const getNodeStyle = () => {
    const baseStyle = 'p-3 rounded-lg border-2 min-w-[150px] transition-all relative';

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

  const getHandleStyle = (type: 'source' | 'target') => {
    const baseStyle = '!w-3 !h-3 !border-2 !border-white transition-colors';
    
    switch (data.type) {
      case 'input':
        return `${baseStyle} !bg-blue-600 hover:!bg-blue-700`;
      case 'process':
        return `${baseStyle} !bg-green-600 hover:!bg-green-700`;
      case 'output':
        return `${baseStyle} !bg-purple-600 hover:!bg-purple-700`;
      default:
        return `${baseStyle} !bg-gray-600 hover:!bg-gray-700`;
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
    <div 
      className={getNodeStyle()}
      onClick={() => onClick && onClick({ data, selected })}
      style={{ cursor: data.type === 'output' && data.productData ? 'pointer' : 'default' }}
    >
      {/* 🎯 Target 핸들 (입력) */}
      {data.type !== 'input' && (
        <Handle
          type='target'
          position={Position.Left}
          isConnectable={true}
          className={getHandleStyle('target')}
        />
      )}

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

      {/* 🎯 Source 핸들 (출력) */}
      {data.type !== 'output' && (
        <Handle
          type='source'
          position={Position.Right}
          isConnectable={true}
          className={getHandleStyle('source')}
        />
      )}
    </div>
  );
};

// nodeTypes는 함수 내부에서 정의됩니다

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
  sourceStream: (props: any) => <SourceStreamEdge {...props} />,
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

  // 제품 노드 관련 상태
  const [showProductModal, setShowProductModal] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [showProductDetailModal, setShowProductDetailModal] = useState(false);
  const [selectedProductNode, setSelectedProductNode] = useState<any>(null);

  // 그룹 관련 상태
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
  const [showGroupModal, setShowGroupModal] = useState(false);

  // React Flow 상태 관리
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges, deleteElements } = useReactFlow();

  // ============================================================================
  // 🎯 초기 데이터 로드
  // ============================================================================

  const fetchFlowsFromBackend = useCallback(async () => {
    try {
      const response = await axiosClient.get('/api/v1/boundary/flow');
      if (response.data && response.data.flows) {
        setFlows(response.data.flows);
        // 첫 번째 플로우가 있으면 자동 선택
        if (response.data.flows.length > 0 && !selectedFlow) {
          // selectFlow 함수가 정의되기 전이므로 직접 처리
          const firstFlow = response.data.flows[0];
          setSelectedFlow(firstFlow);
          setNodes(firstFlow.nodes || []);
          setEdges(firstFlow.edges || []);
        }
      }
    } catch (error) {
      console.error('백엔드에서 플로우 데이터 가져오기 실패:', error);
      // 백엔드 연결 실패 시 빈 배열로 초기화
      setFlows([]);
    }
  }, [selectedFlow, setNodes, setEdges]);

  useEffect(() => {
    fetchFlowsFromBackend();
  }, [fetchFlowsFromBackend]);

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

  const saveFlows = useCallback(async (newFlows: ProcessFlow[]) => {
    try {
      // 백엔드 API를 통한 플로우 저장
      for (const flow of newFlows) {
        if (flow.id.startsWith('flow-')) {
          // 새로 생성된 플로우인 경우 생성 API 호출
          await axiosClient.post('/api/v1/boundary/flow', {
            name: flow.name,
            description: flow.description,
            nodes: flow.nodes,
            edges: flow.edges
          });
        } else {
          // 기존 플로우인 경우 업데이트 API 호출
          await axiosClient.put(`/api/v1/boundary/flow/${flow.id}`, {
            name: flow.name,
            description: flow.description,
            nodes: flow.nodes,
            edges: flow.edges
          });
        }
      }
      setFlows(newFlows);
    } catch (error) {
      console.error('백엔드 플로우 저장 실패:', error);
      // 로컬 상태는 업데이트하되 백엔드 저장은 실패
      setFlows(newFlows);
    }
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
    alert('플로우가 저장되었습니다! (백엔드 연동 예정)');
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
  // 🎯 제품 노드 관련 함수들
  // ============================================================================

  const fetchProducts = useCallback(async () => {
    setIsLoadingProducts(true);
    try {
      const response = await axiosClient.get('/api/v1/boundary/product');
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('제품 데이터 가져오기 오류:', error);
      setProducts([]);
    } finally {
      setIsLoadingProducts(false);
    }
  }, []);

  const addProductNode = useCallback(async () => {
    await fetchProducts();
    setShowProductModal(true);
  }, [fetchProducts]);

  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<ProcessStepData> = {
      id: `product-${Date.now()}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        name: product.name,
        type: 'output',
        description: `제품: ${product.name}`,
        parameters: {
          product_id: product.product_id,
          cn_code: product.cn_code,
          production_qty: product.production_qty,
          sales_qty: product.sales_qty,
          export_qty: product.export_qty,
          inventory_qty: product.inventory_qty,
          defect_rate: product.defect_rate,
          period_start: product.period_start,
          period_end: product.period_end,
        },
        status: 'active',
        productData: product, // 제품 상세 데이터 저장
      },
    };

    addNodes(newNode);
    setShowProductModal(false);
    setSelectedProduct(null);
  }, [addNodes]);

  const handleProductNodeClick = useCallback((node: Node<ProcessStepData>) => {
    if (node.data.type === 'output' && node.data.productData) {
      setSelectedProductNode(node.data.productData);
      setShowProductDetailModal(true);
    }
  }, []);

  // nodeTypes 정의 (함수 내부에서 handleProductNodeClick 사용)
  const nodeTypes: NodeTypes = {
    custom: (props: any) => <CustomNode {...props} onClick={handleProductNodeClick} />,
    group: (props: any) => <GroupNode {...props} />,
  };

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

      const updatedNodes = nodes.map((node: Node<ProcessStepData>) =>
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
    async (params: Connection) => {
      if (params.source && params.target) {
        try {
          console.log('🔗 연결 시도:', params);
          
          // 로컬 상태에 즉시 추가 (사용자 경험 향상)
          const newEdge: Edge = {
            id: `e${params.source}-${params.target}`,
            source: params.source,
            target: params.target,
            type: 'custom',
            markerEnd: { type: MarkerType.ArrowClosed },
            data: {
              label: '연결',
              processType: 'standard'
            }
          };
          
          addEdges(newEdge);
          
          // 백엔드 API 호출 (선택적)
          if (selectedFlow) {
            try {
                             const response = await fetch(`/api/v1/boundary/flow/${selectedFlow.id}/connect`, {
                 method: 'POST',
                 headers: {
                   'Content-Type': 'application/json',
                 },
                 body: JSON.stringify({
                   source: params.source,
                   target: params.target,
                   sourceHandle: params.sourceHandle,
                   targetHandle: params.targetHandle
                 })
               });
              
              if (response.ok) {
                const result = await response.json();
                console.log('✅ 백엔드 연결 성공:', result);
              } else {
                console.warn('⚠️ 백엔드 연결 실패, 로컬 상태만 유지');
              }
            } catch (apiError) {
              console.warn('⚠️ 백엔드 API 호출 실패, 로컬 상태만 유지:', apiError);
            }
          }
          
          console.log('✅ 연결 완료:', newEdge.id);
        } catch (error) {
          console.error('❌ 연결 실패:', error);
        }
      }
    },
    [addEdges, selectedFlow]
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
              <Button
                onClick={addProductNode}
                className='flex items-center gap-2 bg-purple-600 hover:bg-purple-700'
              >
                <Plus className='h-4 w-4' />
                제품 노드
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
                 nodeStrokeColor={(n: any) => {
                   if (n.type === 'input') return '#3b82f6';
                   if (n.type === 'output') return '#8b5cf6';
                   return '#22c55e';
                 }}
                 nodeColor={(n: any) => {
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
                  <div>💡 노드의 핸들을 드래그하여 연결하세요</div>
                  <div>🔗 파란색 핸들: 입력, 초록색 핸들: 출력</div>
                  <div>🔄 연결선을 드래그하여 재연결</div>
                  <div>🗑️ Delete 키로 선택된 요소 삭제</div>
                  {isConnecting && (
                    <div className='text-blue-600 font-medium mt-2'>
                      🔗 연결 중... {connectionStart && `(${connectionStart})`}
                    </div>
                  )}
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
              {nodes.map((node: Node<ProcessStepData>) => (
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

      {/* 제품 선택 모달 */}
      {showProductModal && (
        <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
          <div className='bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto'>
            <div className='flex items-center justify-between mb-4'>
              <h2 className='text-xl font-semibold text-gray-900'>제품 선택</h2>
              <button
                onClick={() => setShowProductModal(false)}
                className='text-gray-400 hover:text-gray-600'
              >
                ✕
              </button>
            </div>
            
            {isLoadingProducts ? (
              <div className='text-center py-8'>
                <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto'></div>
                <p className='mt-2 text-gray-600'>제품 데이터를 불러오는 중...</p>
              </div>
            ) : products.length === 0 ? (
              <div className='text-center py-8'>
                <p className='text-gray-600'>등록된 제품이 없습니다.</p>
              </div>
            ) : (
              <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                {products.map((product) => (
                  <div
                    key={product.product_id}
                    onClick={() => handleProductSelect(product)}
                    className='p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition-colors'
                  >
                    <h3 className='font-semibold text-gray-900 mb-2'>{product.name}</h3>
                    <div className='text-sm text-gray-600 space-y-1'>
                      <p><span className='font-medium'>CN 코드:</span> {product.cn_code || 'N/A'}</p>
                      <p><span className='font-medium'>생산량:</span> {product.production_qty || 0}</p>
                      <p><span className='font-medium'>판매량:</span> {product.sales_qty || 0}</p>
                      <p><span className='font-medium'>수출량:</span> {product.export_qty || 0}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 제품 상세 정보 모달 */}
      {showProductDetailModal && selectedProductNode && (
        <div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
          <div className='bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto'>
            <div className='flex items-center justify-between mb-4'>
              <h2 className='text-xl font-semibold text-gray-900'>제품 상세 정보</h2>
              <button
                onClick={() => setShowProductDetailModal(false)}
                className='text-gray-400 hover:text-gray-600'
              >
                ✕
              </button>
            </div>
            
            <div className='space-y-4'>
              <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div>
                  <h3 className='font-semibold text-gray-900 mb-2'>기본 정보</h3>
                  <div className='space-y-2 text-sm'>
                    <div className='flex justify-between'>
                      <span className='text-gray-600'>제품명:</span>
                      <span className='font-medium'>{selectedProductNode.name}</span>
                    </div>
                    <div className='flex justify-between'>
                      <span className='text-gray-600'>제품 ID:</span>
                      <span className='font-medium'>{selectedProductNode.product_id}</span>
                    </div>
                    <div className='flex justify-between'>
                      <span className='text-gray-600'>CN 코드:</span>
                      <span className='font-medium'>{selectedProductNode.cn_code || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className='font-semibold text-gray-900 mb-2'>기간 정보</h3>
                  <div className='space-y-2 text-sm'>
                    <div className='flex justify-between'>
                      <span className='text-gray-600'>시작일:</span>
                      <span className='font-medium'>{selectedProductNode.period_start || 'N/A'}</span>
                    </div>
                    <div className='flex justify-between'>
                      <span className='text-gray-600'>종료일:</span>
                      <span className='font-medium'>{selectedProductNode.period_end || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className='font-semibold text-gray-900 mb-2'>수량 정보</h3>
                <div className='grid grid-cols-2 md:grid-cols-4 gap-4'>
                  <div className='text-center p-3 bg-blue-50 rounded-lg'>
                    <div className='text-2xl font-bold text-blue-600'>{selectedProductNode.production_qty || 0}</div>
                    <div className='text-sm text-gray-600'>생산량</div>
                  </div>
                  <div className='text-center p-3 bg-green-50 rounded-lg'>
                    <div className='text-2xl font-bold text-green-600'>{selectedProductNode.sales_qty || 0}</div>
                    <div className='text-sm text-gray-600'>판매량</div>
                  </div>
                  <div className='text-center p-3 bg-purple-50 rounded-lg'>
                    <div className='text-2xl font-bold text-purple-600'>{selectedProductNode.export_qty || 0}</div>
                    <div className='text-sm text-gray-600'>수출량</div>
                  </div>
                  <div className='text-center p-3 bg-orange-50 rounded-lg'>
                    <div className='text-2xl font-bold text-orange-600'>{selectedProductNode.inventory_qty || 0}</div>
                    <div className='text-sm text-gray-600'>재고량</div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className='font-semibold text-gray-900 mb-2'>품질 정보</h3>
                <div className='text-center p-4 bg-red-50 rounded-lg'>
                  <div className='text-2xl font-bold text-red-600'>{(selectedProductNode.defect_rate * 100 || 0).toFixed(2)}%</div>
                  <div className='text-sm text-gray-600'>불량률</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
