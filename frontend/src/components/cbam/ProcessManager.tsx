'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import {
  Plus, Trash2, Save, Download, Building
} from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
// import GroupNode from '@/components/atomic/atoms/GroupNode'; // ✅ 제거: 내장 group 사용
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import {
  ReactFlow,
  ReactFlowProvider,
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
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

/* ============================================================================
   커스텀 Edge
   - markerEnd는 defaultEdgeOptions에서만 설정(중복 방지)
============================================================================ */
const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, selected }: any) => {
  const [edgePath] = React.useMemo(() => {
    const cx = (sourceX + targetX) / 2;
    return [`M ${sourceX} ${sourceY} Q ${cx} ${sourceY} ${targetX} ${targetY}`];
  }, [sourceX, sourceY, targetX, targetY]);

  return (
    <path
      id={id}
      className="react-flow__edge-path"
      d={edgePath}
      stroke={selected ? '#3b82f6' : '#6b7280'}
      strokeWidth={selected ? 3 : 2}
      fill="none"
    />
  );
};

const edgeTypes: EdgeTypes = { custom: CustomEdge };

/* ============================================================================
   내부 컴포넌트
============================================================================ */
function ProcessManagerInner() {
  // 상태 훅
  const [nodes, , onNodesChange] = useNodesState<any>([]);
  const [edges, , onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges } = useReactFlow();

  // 사업장 관련 상태
  const [installs, setInstalls] = useState<any[]>([]);
  const [selectedInstall, setSelectedInstall] = useState<any>(null);
  const [showInstallModal, setShowInstallModal] = useState(false);

  // 제품 목록 모달 상태
  const [products, setProducts] = useState<any[]>([]);
  const [showProductModal, setShowProductModal] = useState(false);

  // 공정 목록 모달 상태
  const [processes, setProcesses] = useState<any[]>([]);
  const [showProcessModal, setShowProcessModal] = useState(false);

  // 사업장 목록 불러오기
  const fetchInstalls = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
    } catch (error) {
      console.error('사업장 목록 조회 실패:', error);
      setInstalls([]);
    }
  }, []);

  // 선택된 사업장의 제품 목록 불러오기
  const fetchProductsByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      // 선택된 사업장의 제품만 필터링
      const filteredProducts = response.data.filter((product: any) => product.install_id === installId);
      setProducts(filteredProducts);
    } catch (error) {
      console.error('제품 목록 조회 실패:', error);
      setProducts([]);
    }
  }, []);

  // 선택된 사업장의 공정 목록 불러오기
  const fetchProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      // 선택된 사업장의 제품에 속한 공정만 필터링
      const installProducts = products.filter((product: any) => product.install_id === installId);
      const productIds = installProducts.map((product: any) => product.id);
      const filteredProcesses = response.data.filter((process: any) => productIds.includes(process.product_id));
      setProcesses(filteredProcesses);
    } catch (error) {
      console.error('공정 목록 조회 실패:', error);
      setProcesses([]);
    }
  }, [products]);

  // 사업장 선택 시 제품과 공정 목록 업데이트
  useEffect(() => {
    if (selectedInstall) {
      fetchProductsByInstall(selectedInstall.id);
    }
  }, [selectedInstall, fetchProductsByInstall]);

  useEffect(() => {
    if (selectedInstall && products.length > 0) {
      fetchProcessesByInstall(selectedInstall.id);
    }
  }, [selectedInstall, products, fetchProcessesByInstall]);

  // 컴포넌트 마운트 시 사업장 목록 불러오기
  useEffect(() => {
    fetchInstalls();
  }, [fetchInstalls]);

  // 사업장 선택 모달 열기
  const openInstallModal = useCallback(() => {
    setShowInstallModal(true);
  }, []);

  // 사업장 선택
  const handleInstallSelect = useCallback((install: any) => {
    setSelectedInstall(install);
    setShowInstallModal(false);
    // 캔버스 초기화
    onNodesChange([]);
    onEdgesChange([]);
  }, [onNodesChange, onEdgesChange]);

  // 제품 노드 추가(모달 열기)
  const addProductNode = useCallback(async () => {
    if (!selectedInstall) {
      alert('먼저 사업장을 선택해주세요.');
      return;
    }
    setShowProductModal(true);
  }, [selectedInstall]);

  // 공정 노드 추가(모달 열기)
  const addProcessNode = useCallback(async () => {
    if (!selectedInstall) {
      alert('먼저 사업장을 선택해주세요.');
      return;
    }
    setShowProcessModal(true);
  }, [selectedInstall]);

  // 제품 선택 → 노드 추가
  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<any> = {
      id: `product-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: product.product_name,
        description: `제품: ${product.product_name}`,
        variant: 'product',
        productData: product,
      },
    };

    addNodes(newNode);
    setShowProductModal(false);
  }, [addNodes]);

  // 공정 선택 → 노드 추가
  const handleProcessSelect = useCallback((process: any) => {
    const newNode: Node<any> = {
      id: `process-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: process.process_name,
        description: `공정: ${process.process_name}`,
        variant: 'process',
        processData: process,
      },
    };

    addNodes(newNode);
    setShowProcessModal(false);
  }, [addNodes]);

  // 그룹 노드 추가
  const addGroupNode = useCallback(() => {
    const newNode: Node<any> = {
      id: `group-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'group',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      style: { width: 200, height: 100 },
      data: { label: '그룹' },
    };

    addNodes(newNode);
  }, [addNodes]);

  const nodeTypes: NodeTypes = { custom: ProductNode };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 헤더 */}
      <div className="bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold">CBAM 산정경계설정</h1>
        <p className="text-gray-300">CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.</p>
        {selectedInstall && (
          <div className="mt-2 p-2 bg-blue-600/20 border border-blue-500/30 rounded-lg">
            <p className="text-blue-300 text-sm">
              🏭 선택된 사업장: <span className="font-semibold">{selectedInstall.install_name}</span>
              {selectedInstall.reporting_year && ` (${selectedInstall.reporting_year}년)`}
            </p>
          </div>
        )}
      </div>

      {/* 버튼 */}
      <div className="bg-gray-800 p-4 flex gap-2">
        <Button onClick={openInstallModal} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Building className="h-4 w-4" /> 사업장 선택
        </Button>
        <Button onClick={addProductNode} disabled={!selectedInstall} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 제품 노드
        </Button>
        <Button onClick={addProcessNode} disabled={!selectedInstall} className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 공정 노드
        </Button>
        <Button onClick={addGroupNode} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 그룹 노드
        </Button>
      </div>

      {/* ReactFlow 캔버스 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={(params: Connection) =>
            addEdges({
              id: `e-${Date.now()}-${Math.random().toString(36).slice(2)}`,
              source: params.source!,
              target: params.target!,
              sourceHandle: params.sourceHandle ?? undefined,
              targetHandle: params.targetHandle ?? undefined,
              type: 'custom',
            })
          }
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          defaultEdgeOptions={{ type: 'custom', markerEnd: { type: MarkerType.ArrowClosed } }}
          deleteKeyCode="Delete"
          className="bg-gray-900" // ✅ 다크 캔버스
          fitView
        >
          <Background color="#334155" gap={24} size={1} />
          <Controls className="!bg-gray-800 !border !border-gray-700 !text-gray-200 !rounded-md" position="bottom-left" />
          <MiniMap
            className="!border !border-gray-700 !rounded-md"
            style={{ backgroundColor: '#0b1220' }}
            maskColor="rgba(17,24,39,0.6)"
            nodeColor={() => '#a78bfa'}
            nodeStrokeColor={() => '#e5e7eb'}
            pannable
            zoomable
          />
        </ReactFlow>
      </div>

      {/* 사업장 선택 모달 */}
      {showInstallModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">사업장 선택</h3>
              <button onClick={() => setShowInstallModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {installs.length > 0 ? (
                installs.map((install) => (
                  <div
                    key={install.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                    onClick={() => handleInstallSelect(install)}
                  >
                    <div className="font-medium text-white">{install.install_name}</div>
                    <div className="text-sm text-gray-300">ID: {install.id}</div>
                    {install.reporting_year && (
                      <div className="text-sm text-gray-300">보고기간: {install.reporting_year}년</div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  등록된 사업장이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 제품 선택 모달 */}
      {showProductModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">제품 선택</h3>
              <button onClick={() => setShowProductModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {products.length > 0 ? (
                products.map((product) => (
                  <div
                    key={product.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                    onClick={() => handleProductSelect(product)}
                  >
                    <div className="font-medium text-white">{product.product_name}</div>
                    <div className="text-sm text-gray-300">카테고리: {product.product_category}</div>
                    <div className="text-sm text-gray-300">수량: {product.product_amount}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  선택된 사업장에 등록된 제품이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 공정 선택 모달 */}
      {showProcessModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">공정 선택</h3>
              <button onClick={() => setShowProcessModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {processes.length > 0 ? (
                processes.map((process) => (
                  <div
                    key={process.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-purple-400 transition-colors"
                    onClick={() => handleProcessSelect(process)}
                  >
                    <div className="font-medium text-white">{process.process_name}</div>
                    <div className="text-sm text-gray-300">시작일: {process.start_period}</div>
                    <div className="text-sm text-gray-300">종료일: {process.end_period}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  선택된 사업장에 등록된 공정이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================================
   메인 컴포넌트
============================================================================ */
export default function ProcessManager() {
  return (
    <div className="w-full h-screen">
      <ReactFlowProvider>
        <ProcessManagerInner />
      </ReactFlowProvider>
    </div>
  );
}
