'use client';

import React, { useState, useCallback } from 'react';
import Button from '@/components/atomic/atoms/Button';
import {
  Plus, Trash2, Save, Download
} from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
// import GroupNode from '@/components/atomic/atoms/GroupNode'; // ✅ 제거: 내장 group 사용
import axiosClient from '@/lib/axiosClient';
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

  // 제품 목록 모달 상태
  const [products, setProducts] = useState<any[]>([]);
  const [showProductModal, setShowProductModal] = useState(false);

  // 제품 불러오기
  const fetchProducts = useCallback(async () => {
    try {
      const res = await axiosClient.get('/api/v1/boundary/product');
      setProducts(res.data.products || []);
    } catch {
      setProducts([
        { product_id: 'dummy-1', name: '테스트 제품 1', cn_code: '7208.51.00', production_qty: 1000, sales_qty: 800, export_qty: 200, inventory_qty: 150, defect_rate: 0.05, period_start: '2024-01-01', period_end: '2024-12-31' },
        { product_id: 'dummy-2', name: '테스트 제품 2', cn_code: '7208.52.00', production_qty: 2000, sales_qty: 1800, export_qty: 400, inventory_qty: 300, defect_rate: 0.03, period_start: '2024-01-01', period_end: '2024-12-31' },
        { product_id: 'dummy-3', name: '테스트 제품 3', cn_code: '7208.53.00', production_qty: 1500, sales_qty: 1200, export_qty: 300, inventory_qty: 200, defect_rate: 0.07, period_start: '2024-01-01', period_end: '2024-12-31' },
      ]);
    }
  }, []);

  // 제품 노드 추가(모달 열기)
  const addProductNode = useCallback(async () => {
    await fetchProducts();
    setShowProductModal(true);
  }, [fetchProducts]);

  // 제품 선택 → 노드 추가
  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<any> = {
      id: `product-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: product.name,
        description: `제품: ${product.name}`,
        variant: 'product',
        productData: product,
        name: product.name,
        type: 'output',
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
      },
    };
    addNodes(newNode);
    setShowProductModal(false);
  }, [addNodes]);

  // 그룹 노드 추가(내장 group 타입 사용)
  const addGroupNode = useCallback(() => {
    const id = `group-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    addNodes({
      id,
      type: 'group', // ✅ 내장 타입. 커스텀 컴포넌트 매핑 금지
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: { label: `그룹 ${id}`, description: '산정경계' },
      style: {
        width: 420,
        height: 320,
        border: '2px solid #a78bfa',
        borderRadius: 12,
        background: '#0b1220', // 다크 배경
        pointerEvents: 'auto',
      },
      className: 'shadow-sm',
    });
  }, [addNodes]);

  // ✅ 커스텀 노드 매핑(제품만)
  const nodeTypes: NodeTypes = { custom: ProductNode };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 헤더 */}
      <div className="bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold">CBAM 프로세스 관리</h1>
        <p className="text-gray-300">CBAM 관련 프로세스 플로우를 생성하고 관리합니다.</p>
      </div>

      {/* 버튼 */}
      <div className="bg-gray-800 p-4 flex gap-2">
        <Button onClick={addProductNode} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 제품 노드
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

      {/* 제품 선택 모달 */}
      {showProductModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">제품 선택</h3>
              <button onClick={() => setShowProductModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="space-y-2">
              {products.map((p) => (
                <div
                  key={p.product_id}
                  className="p-3 border rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  onClick={() => handleProductSelect(p)}
                >
                  <div className="font-medium">{p.name}</div>
                  <div className="text-sm text-gray-600">CN: {p.cn_code}</div>
                  <div className="text-sm text-gray-600">생산량: {p.production_qty}</div>
                </div>
              ))}
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
